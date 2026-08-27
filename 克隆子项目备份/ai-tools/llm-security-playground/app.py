# ---------------------------------------------------------------------------
# app.py - Flask application
# LLM Security Playground - CyberSecurity Course, Kore University of Enna
# © Moreno La Quatra - https://mlaquatra.me/
# ---------------------------------------------------------------------------

import argparse
import json
import logging
from flask import Flask, render_template, request, Response, jsonify

from config import MODELS, MODEL_FAMILIES, FAMILY_DISPLAY, EXAMPLE_PROMPTS
from inference import ModelManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
model_manager = ModelManager()


# ── Page ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        models=MODELS,
        model_families=MODEL_FAMILIES,
        family_display=FAMILY_DISPLAY,
        example_prompts=EXAMPLE_PROMPTS,
    )


# ── API: Model catalogue ────────────────────────────────────────────────────

@app.route("/api/models")
def api_models():
    return jsonify(MODELS)


# ── API: Trigger model loading ──────────────────────────────────────────────

@app.route("/api/load", methods=["POST"])
def api_load():
    data = request.get_json(silent=True) or {}
    model_key = data.get("model", "").strip()

    if model_key not in MODELS:
        return jsonify({"error": f"Unknown model: {model_key}"}), 400

    cfg = MODELS[model_key]
    model_manager.load_model_async(model_key, cfg["hf_id"], cfg["family"])
    return jsonify({"status": "loading", "model": model_key})


# ── API: Model status ───────────────────────────────────────────────────────

@app.route("/api/model-status")
def api_model_status():
    model_key = request.args.get("model", "").strip()
    if model_key not in MODELS:
        return jsonify({"error": f"Unknown model: {model_key}"}), 400

    return jsonify({
        "model": model_key,
        "status": model_manager.get_status(model_key),
        "error":  model_manager.get_error(model_key),
    })


# ── API: Streaming generation ───────────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True) or {}

    model_key       = data.get("model", "").strip()
    prompt          = data.get("prompt", "").strip()
    messages        = data.get("messages", [])          # for chat models
    max_tokens      = int(data.get("max_tokens", 256))
    temperature     = float(data.get("temperature", 0.8))
    top_p           = float(data.get("top_p", 0.9))
    enable_thinking = bool(data.get("enable_thinking", False))

    if model_key not in MODELS:
        return jsonify({"error": f"Unknown model: {model_key}"}), 400

    if not model_manager.is_loaded(model_key):
        return jsonify({"error": "Model not loaded. Click 'Load' first."}), 409

    if not prompt and not messages:
        return jsonify({"error": "No prompt provided."}), 400

    cfg = MODELS[model_key]

    def event_stream():
        try:
            for token in model_manager.generate_stream(
                model_key=model_key,
                model_config=cfg,
                prompt=prompt,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                enable_thinking=enable_thinking,
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as exc:
            logger.exception(f"[{model_key}] stream error: {exc}")
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Security Playground")
    parser.add_argument("--port", type=int, default=9999, help="Port to listen on (default: 9999)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    args = parser.parse_args()
    app.run(debug=False, threaded=True, host=args.host, port=args.port)

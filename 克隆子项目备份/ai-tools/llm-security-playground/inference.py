# ---------------------------------------------------------------------------
# inference.py - Model loading & streaming generation
# LLM Security Playground · CyberSecurity Course, Kore University of Enna
# © Moreno La Quatra - https://mlaquatra.me/
# ---------------------------------------------------------------------------

import threading
import logging
import torch

logger = logging.getLogger(__name__)

# ── Lazy imports to avoid loading torch on import ──────────────────────────
_transformers = None


def _get_transformers():
    global _transformers
    if _transformers is None:
        import transformers as tf
        _transformers = tf
    return _transformers


# ── Device helpers ──────────────────────────────────────────────────────────

def _best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _best_dtype():
    dev = _best_device()
    # bfloat16 is well-supported on CUDA Ampere+; use float16 on older or MPS
    if dev == "cuda":
        return torch.bfloat16
    if dev == "mps":
        return torch.float16
    return torch.float32


# ── ModelManager ────────────────────────────────────────────────────────────

class ModelManager:
    """
    Thread-safe manager for multiple HuggingFace models.
    Models are loaded lazily (on first load_model_async call) and kept
    in memory for the lifetime of the process.
    """

    def __init__(self):
        self._models: dict = {}       # model_key → model
        self._tokenizers: dict = {}   # model_key → tokenizer / processor
        self._status: dict = {}       # model_key → 'idle'|'loading'|'loaded'|'error'
        self._errors: dict = {}       # model_key → error string
        self._gen_locks: dict = {}    # model_key → Lock (1 generation at a time per model)
        self._global_load_lock = threading.Lock()

    # ── Status helpers ───────────────────────────────────────────────────

    def get_status(self, model_key: str) -> str:
        return self._status.get(model_key, "idle")

    def get_error(self, model_key: str) -> str | None:
        return self._errors.get(model_key)

    def is_loaded(self, model_key: str) -> bool:
        return self._status.get(model_key) == "loaded"

    def all_statuses(self) -> dict:
        return {k: self._status.get(k, "idle") for k in self._status}

    # ── Loading ──────────────────────────────────────────────────────────

    def load_model_async(self, model_key: str, hf_id: str, family: str):
        """Kick off model loading in a daemon thread (non-blocking)."""
        with self._global_load_lock:
            if self._status.get(model_key) in ("loading", "loaded"):
                return  # already in progress or done
            self._status[model_key] = "loading"

        t = threading.Thread(
            target=self._load_worker,
            args=(model_key, hf_id, family),
            daemon=True,
            name=f"load-{model_key}",
        )
        t.start()

    def _load_worker(self, model_key: str, hf_id: str, family: str):
        tf = _get_transformers()
        try:
            logger.info(f"[{model_key}] Loading {hf_id} …")
            dtype = _best_dtype()

            if family == "gemma":
                # Gemma 4 uses AutoProcessor (handles multimodal; text-only still works)
                tokenizer = tf.AutoProcessor.from_pretrained(hf_id)
            else:
                tokenizer = tf.AutoTokenizer.from_pretrained(hf_id)
                if tokenizer.pad_token_id is None:
                    tokenizer.pad_token_id = tokenizer.eos_token_id

            model = tf.AutoModelForCausalLM.from_pretrained(
                hf_id,
                torch_dtype=dtype,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            model.eval()

            self._models[model_key] = model
            self._tokenizers[model_key] = tokenizer
            self._gen_locks[model_key] = threading.Lock()
            self._status[model_key] = "loaded"

            logger.info(f"[{model_key}] Ready on {model.device}")

        except Exception as exc:
            logger.exception(f"[{model_key}] Load failed: {exc}")
            self._status[model_key] = "error"
            self._errors[model_key] = str(exc)

    # ── Generation ───────────────────────────────────────────────────────

    def generate_stream(
        self,
        model_key: str,
        model_config: dict,
        prompt: str,
        messages: list,
        max_tokens: int,
        temperature: float,
        top_p: float,
        enable_thinking: bool = False,
    ):
        """
        Yield decoded text tokens one by one using TextIteratorStreamer.

        For *base* models the raw `prompt` is tokenised without any chat
        template, so the model simply continues the text - demonstrating the
        absence of alignment.

        For *instruct* models the `messages` list (or a single user message
        built from `prompt`) is formatted with the model's chat template.
        """
        if not self.is_loaded(model_key):
            raise RuntimeError(f"Model '{model_key}' is not loaded.")

        tf = _get_transformers()
        model = self._models[model_key]
        tokenizer = self._tokenizers[model_key]
        family = model_config["family"]
        model_type = model_config["type"]

        # ── Build input text ─────────────────────────────────────────────
        if model_type == "base":
            # Raw text completion - no template
            input_text = prompt
        else:
            # Chat mode - apply template
            if not messages:
                messages = [{"role": "user", "content": prompt}]

            if family == "gemma":
                # AutoProcessor.apply_chat_template supports enable_thinking
                input_text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=enable_thinking,
                )
            else:
                # Qwen3.5 - enable_thinking controls <think> blocks
                input_text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=enable_thinking,
                )

        # ── Tokenise ─────────────────────────────────────────────────────
        if family == "gemma":
            # Use processor with text= kwarg
            inputs = tokenizer(text=input_text, return_tensors="pt").to(model.device)
            # Retrieve the underlying tokenizer for the streamer
            inner_tok = tokenizer.tokenizer
        else:
            inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
            inner_tok = tokenizer

        # ── Streamer ─────────────────────────────────────────────────────
        streamer = tf.TextIteratorStreamer(
            inner_tok,
            skip_prompt=True,
            skip_special_tokens=True,
            timeout=120.0,
        )

        # ── Generation kwargs ────────────────────────────────────────────
        do_sample = temperature > 0.01
        gen_kwargs: dict = {
            **inputs,
            "max_new_tokens": max_tokens,
            "do_sample": do_sample,
            "streamer": streamer,
            "pad_token_id": (
                inner_tok.pad_token_id
                if inner_tok.pad_token_id is not None
                else inner_tok.eos_token_id
            ),
            "repetition_penalty": 1.1,
        }
        if do_sample:
            gen_kwargs["temperature"] = temperature
            gen_kwargs["top_p"] = top_p

        # ── Run generation in background thread ──────────────────────────
        gen_lock = self._gen_locks[model_key]
        errors: list = []

        def _run():
            acquired = gen_lock.acquire(blocking=False)
            if not acquired:
                errors.append("Another generation is already running for this model.")
                # Push sentinel to unblock the streamer iterator
                streamer.on_finalized_text("", stream_end=True)
                return
            try:
                model.generate(**gen_kwargs)
            except Exception as exc:
                logger.exception(f"[{model_key}] Generation error: {exc}")
                errors.append(str(exc))
            finally:
                gen_lock.release()

        gen_thread = threading.Thread(target=_run, daemon=True)
        gen_thread.start()

        # ── Yield tokens ─────────────────────────────────────────────────
        for token in streamer:
            if errors:
                raise RuntimeError(errors[0])
            yield token

        gen_thread.join()
        if errors:
            raise RuntimeError(errors[0])

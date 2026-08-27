/* ============================================================
   app.js - LLM Security Playground frontend
   CyberSecurity Course · Kore University of Enna
   © Moreno La Quatra - https://mlaquatra.me/
   ============================================================ */

'use strict';

// ── State ─────────────────────────────────────────────────────────────────
const MODELS   = JSON.parse(document.getElementById('models-data').textContent);
const FAMILIES = JSON.parse(document.getElementById('families-data').textContent);

const state = {
  family:              'qwen',    // current model family key
  baseKey:             '',        // model key for left (base) panel
  alignedKey:          '',        // model key for right (aligned) panel
  statusLeft:          'idle',
  statusRight:         'idle',
  generatingLeft:      false,
  generatingRight:     false,
  conversationRight:   [],        // chat history for aligned panel
  pollIntervalLeft:    null,
  pollIntervalRight:   null,
};

// ── DOM cache ──────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const dom = {
  overlay:          $('disclaimer-overlay'),
  promptInput:      $('prompt-input'),
  btnGenerate:      $('btn-generate'),
  btnGenerateText:  $('btn-generate-text'),
  btnGenerateSpinner: $('btn-generate-spinner'),
  paramsGrid:       $('params-grid'),
  paramsArrow:      $('params-arrow'),
  temperature:      $('temperature'),
  topP:             $('top-p'),
  maxTokens:        $('max-tokens'),
  toggleThinking:   $('toggle-thinking'),
  // Left (base)
  panelLeft:        $('panel-left'),
  outputLeft:       $('output-left'),
  placeholderLeft:  $('placeholder-left'),
  dotLeft:          $('dot-left'),
  statusTextLeft:   $('status-text-left'),
  btnLoadLeft:      $('btn-load-left'),
  modelNameLeft:    $('model-name-left'),
  modelDescLeft:    $('model-desc-left'),
  modelHfLeft:      $('model-hf-left'),
  thinkingLeft:     $('thinking-left'),
  thinkingContentLeft: $('thinking-content-left'),
  // Right (aligned)
  panelRight:       $('panel-right'),
  outputRight:      $('output-right'),
  placeholderRight: $('placeholder-right'),
  dotRight:         $('dot-right'),
  statusTextRight:  $('status-text-right'),
  btnLoadRight:     $('btn-load-right'),
  modelNameRight:   $('model-name-right'),
  modelDescRight:   $('model-desc-right'),
  modelHfRight:     $('model-hf-right'),
  thinkingRight:    $('thinking-right'),
  thinkingContentRight: $('thinking-content-right'),
};

// ── Disclaimer ──────────────────────────────────────────────────────────────
function closeDisclaimer() {
  dom.overlay.classList.add('hidden');
  sessionStorage.setItem('disclaimer-accepted', '1');
}

function openDisclaimer() {
  dom.overlay.classList.remove('hidden');
}

// ── Family / model selection ────────────────────────────────────────────────
function setFamily(familyKey) {
  state.family = familyKey;

  // Update tab styles
  document.querySelectorAll('.family-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.family === familyKey);
  });

  // Identify base / aligned keys for this family
  const [baseKey, alignedKey] = FAMILIES[familyKey];
  state.baseKey    = baseKey;
  state.alignedKey = alignedKey;

  // Populate panel headers
  _applyModelMeta('left',  baseKey);
  _applyModelMeta('right', alignedKey);

  // Enable load buttons
  dom.btnLoadLeft.disabled  = false;
  dom.btnLoadRight.disabled = false;

  // Clear previous conversations / outputs
  clearConversations();

  // Start polling for already-loaded models
  _pollStatus('left',  baseKey);
  _pollStatus('right', alignedKey);
}

function _applyModelMeta(side, key) {
  const m = MODELS[key];
  if (!m) return;
  const nameEl   = side === 'left' ? dom.modelNameLeft   : dom.modelNameRight;
  const descEl   = side === 'left' ? dom.modelDescLeft   : dom.modelDescRight;
  const hfEl     = side === 'left' ? dom.modelHfLeft     : dom.modelHfRight;

  nameEl.textContent = `${m.name}  (${m.params})`;
  descEl.textContent = m.description + ' ' + m.detail;
  hfEl.href          = m.hf_url;
  hfEl.style.display = 'inline';
}

// ── Model loading ───────────────────────────────────────────────────────────
function loadModel(side) {
  const key     = side === 'left' ? state.baseKey : state.alignedKey;
  const btnEl   = side === 'left' ? dom.btnLoadLeft : dom.btnLoadRight;

  if (!key) return;

  btnEl.disabled   = true;
  btnEl.textContent = 'Loading…';

  fetch('/api/load', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: key }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        _setStatus(side, 'error');
        _showNotice(side === 'left' ? dom.outputLeft : dom.outputRight, data.error, 'error');
        btnEl.disabled    = false;
        btnEl.textContent = 'Retry Load';
        return;
      }
      _setStatus(side, 'loading');
      _pollStatus(side, key);
    })
    .catch(err => {
      _setStatus(side, 'error');
      btnEl.disabled    = false;
      btnEl.textContent = 'Retry Load';
    });
}

function _pollStatus(side, key) {
  if (!key) return;
  const intervalKey = side === 'left' ? 'pollIntervalLeft' : 'pollIntervalRight';

  // Clear previous interval
  if (state[intervalKey]) {
    clearInterval(state[intervalKey]);
    state[intervalKey] = null;
  }

  // If already loaded, just update UI
  const currentStatus = side === 'left' ? state.statusLeft : state.statusRight;
  if (currentStatus === 'loaded') return;

  state[intervalKey] = setInterval(async () => {
    try {
      const res = await fetch(`/api/model-status?model=${encodeURIComponent(key)}`);
      const data = await res.json();

      _setStatus(side, data.status);

      if (data.status === 'loaded' || data.status === 'error') {
        clearInterval(state[intervalKey]);
        state[intervalKey] = null;

        const btnEl = side === 'left' ? dom.btnLoadLeft : dom.btnLoadRight;
        if (data.status === 'loaded') {
          btnEl.style.display = 'none';
        } else {
          btnEl.disabled    = false;
          btnEl.textContent = 'Retry Load';
          const outputEl = side === 'left' ? dom.outputLeft : dom.outputRight;
          _showNotice(outputEl, data.error || 'Load failed. Check the server log.', 'error');
        }
      }
    } catch (_) { /* network error - keep polling */ }
  }, 2000);
}

function _setStatus(side, statusStr) {
  if (side === 'left')  state.statusLeft  = statusStr;
  else                  state.statusRight = statusStr;

  const dotEl  = side === 'left' ? dom.dotLeft  : dom.dotRight;
  const textEl = side === 'left' ? dom.statusTextLeft : dom.statusTextRight;

  dotEl.className = 'status-dot ' + {
    idle:    'dot-idle',
    loading: 'dot-loading',
    loaded:  'dot-loaded',
    error:   'dot-error',
  }[statusStr] || 'dot-idle';

  textEl.textContent = {
    idle:    'Not loaded',
    loading: 'Loading…',
    loaded:  'Loaded ✓',
    error:   'Error',
  }[statusStr] || statusStr;
}

// ── Generate ────────────────────────────────────────────────────────────────
function sendPrompt() {
  const rawPrompt = dom.promptInput.value.trim();
  if (!rawPrompt) {
    dom.promptInput.focus();
    return;
  }

  const leftLoaded  = state.statusLeft  === 'loaded';
  const rightLoaded = state.statusRight === 'loaded';
  if (!leftLoaded && !rightLoaded) {
    _flashInput();
    return;
  }

  const temperature    = parseFloat(dom.temperature.value);
  const topP           = parseFloat(dom.topP.value);
  const maxTokens      = parseInt(dom.maxTokens.value, 10);
  const enableThinking = dom.toggleThinking.checked;

  // Disable generate button while at least one panel is running
  _setGenerateBtn(true);

  const tasks = [];

  if (leftLoaded && !state.generatingLeft) {
    tasks.push(_generateLeft(rawPrompt, temperature, topP, maxTokens, enableThinking));
  }
  if (rightLoaded && !state.generatingRight) {
    tasks.push(_generateRight(rawPrompt, temperature, topP, maxTokens, enableThinking));
  }

  Promise.allSettled(tasks).then(() => _setGenerateBtn(false));
}

function _setGenerateBtn(busy) {
  dom.btnGenerate.disabled             = busy;
  dom.btnGenerateText.style.display    = busy ? 'none'   : 'inline';
  dom.btnGenerateSpinner.style.display = busy ? 'inline-flex' : 'none';
}

// ── Left panel: text completion (base model) ────────────────────────────────
async function _generateLeft(prompt, temperature, topP, maxTokens, enableThinking) {
  state.generatingLeft = true;

  // Hide placeholder
  _hidePlaceholder('left');

  // Render prompt prefix
  const wrap = document.createElement('div');
  wrap.className = 'completion-wrap';

  const promptSpan = document.createElement('span');
  promptSpan.className = 'completion-prompt';
  promptSpan.textContent = '▸ ' + prompt;
  wrap.appendChild(promptSpan);

  const outputSpan = document.createElement('span');
  outputSpan.className = 'completion-text generating-cursor';
  wrap.appendChild(outputSpan);

  dom.outputLeft.appendChild(wrap);

  try {
    await _streamGeneration(
      state.baseKey,
      { model_type: 'base' },
      { prompt },
      temperature, topP, maxTokens, enableThinking,
      token => {
        outputSpan.textContent += token;
        dom.outputLeft.scrollTop = dom.outputLeft.scrollHeight;
      },
      null,   // no thinking callback for base
      err => {
        outputSpan.classList.remove('generating-cursor');
        _showNotice(dom.outputLeft, err, 'error');
      }
    );
  } finally {
    outputSpan.classList.remove('generating-cursor');
    state.generatingLeft = false;
  }
}

// ── Right panel: chat (aligned model) ──────────────────────────────────────
async function _generateRight(prompt, temperature, topP, maxTokens, enableThinking) {
  state.generatingRight = true;

  _hidePlaceholder('right');

  // Add user bubble
  const userMsg = { role: 'user', content: prompt };
  state.conversationRight.push(userMsg);
  _appendChatBubble(dom.outputRight, 'user', prompt);

  // Add (empty) assistant bubble
  const bubble = _appendChatBubble(dom.outputRight, 'assistant', '');

  let assistantText = '';
  let thinkingText  = '';
  let inThinking    = false;

  try {
    await _streamGeneration(
      state.alignedKey,
      { model_type: 'instruct' },
      { messages: state.conversationRight },
      temperature, topP, maxTokens, enableThinking,
      token => {
        // Rudimentary thinking tag detection
        if (enableThinking) {
          if (token.includes('<think>'))   { inThinking = true; }
          if (token.includes('</think>'))  { inThinking = false; return; }
          if (inThinking) {
            thinkingText += token;
            _updateThinking('right', thinkingText);
            return;
          }
        }
        assistantText += token;
        bubble.textContent = assistantText;
        dom.outputRight.scrollTop = dom.outputRight.scrollHeight;
      },
      null,
      err => {
        bubble.classList.remove('generating-cursor');
        _showNotice(dom.outputRight, err, 'error');
      }
    );
  } finally {
    bubble.classList.remove('generating-cursor');
    state.conversationRight.push({ role: 'assistant', content: assistantText });
    state.generatingRight = false;
  }
}

// ── Core streaming helper ───────────────────────────────────────────────────
async function _streamGeneration(
  modelKey, modelConfig,
  { prompt = '', messages = [] },
  temperature, topP, maxTokens, enableThinking,
  onToken, onThinking, onError
) {
  const body = {
    model:          modelKey,
    prompt,
    messages,
    temperature,
    top_p:          topP,
    max_tokens:     maxTokens,
    enable_thinking: enableThinking,
  };

  let response;
  try {
    response = await fetch('/api/generate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
  } catch (netErr) {
    if (onError) onError('Network error: ' + netErr.message);
    return;
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({ error: response.statusText }));
    if (onError) onError(data.error || 'Request failed');
    return;
  }

  const reader  = response.body.getReader();
  const decoder = new TextDecoder();
  let   buffer  = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Extract complete SSE events
    const parts = buffer.split('\n\n');
    buffer = parts.pop();   // keep incomplete tail

    for (const part of parts) {
      for (const line of part.split('\n')) {
        if (!line.startsWith('data: ')) continue;
        try {
          const ev = JSON.parse(line.slice(6));
          if (ev.token !== undefined && onToken) onToken(ev.token);
          if (ev.done)  return;
          if (ev.error && onError) { onError(ev.error); return; }
        } catch (_) { /* malformed line - skip */ }
      }
    }
  }
}

// ── UI helpers ──────────────────────────────────────────────────────────────
function _hidePlaceholder(side) {
  const el = side === 'left' ? dom.placeholderLeft : dom.placeholderRight;
  if (el) el.style.display = 'none';
}

function _appendChatBubble(container, role, text) {
  const wrap = document.createElement('div');
  wrap.className = `chat-message ${role === 'user' ? 'user-message' : 'assistant-message'}`;

  const label = document.createElement('span');
  label.className   = 'chat-role-label';
  label.textContent = role === 'user' ? 'You' : 'Assistant';
  wrap.appendChild(label);

  const bubble = document.createElement('div');
  bubble.className   = 'chat-bubble' + (role === 'assistant' ? ' generating-cursor' : '');
  bubble.textContent = text;
  wrap.appendChild(bubble);

  container.appendChild(wrap);
  container.scrollTop = container.scrollHeight;
  return bubble;
}

function _updateThinking(side, text) {
  const blockEl   = side === 'left' ? dom.thinkingLeft   : dom.thinkingRight;
  const contentEl = side === 'left' ? dom.thinkingContentLeft : dom.thinkingContentRight;
  if (!blockEl || !contentEl) return;
  blockEl.style.display   = '';
  contentEl.textContent   = text;
}

function toggleThinking(side) {
  const blockEl = side === 'left' ? dom.thinkingLeft : dom.thinkingRight;
  const btn     = blockEl.querySelector('button');
  const content = blockEl.querySelector('.thinking-content');
  const collapsed = content.style.display === 'none';
  content.style.display = collapsed ? '' : 'none';
  btn.textContent       = collapsed ? 'Hide' : 'Show';
}

function _showNotice(container, message, type = 'info') {
  const div = document.createElement('div');
  div.className   = `notice notice-${type}`;
  div.textContent = (type === 'error' ? '✕ ' : 'ℹ ') + message;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function _flashInput() {
  dom.promptInput.style.borderColor = 'var(--base)';
  setTimeout(() => { dom.promptInput.style.borderColor = ''; }, 1200);
}

// ── Controls ─────────────────────────────────────────────────────────────────
function clearInput() {
  dom.promptInput.value = '';
  dom.promptInput.focus();
}

function setPrompt(btn) {
  dom.promptInput.value = btn.dataset.prompt || '';
  dom.promptInput.focus();
  // Scroll textarea to top
  dom.promptInput.scrollTop = 0;
}

function clearConversations() {
  state.conversationRight = [];

  // Left panel - clear output
  dom.outputLeft.innerHTML  = '';
  const phL = document.createElement('div');
  phL.className   = 'output-placeholder';
  phL.id          = 'placeholder-left';
  phL.textContent = 'Load the model, then enter a prompt to see unfiltered text continuation.';
  dom.outputLeft.appendChild(phL);
  // Update the live reference so _hidePlaceholder() works after clear
  dom.placeholderLeft = phL;

  // Right panel - clear output
  dom.outputRight.innerHTML = '';
  const phR = document.createElement('div');
  phR.className   = 'output-placeholder';
  phR.id          = 'placeholder-right';
  phR.textContent = 'Load the model, then send a message to start the chat.';
  dom.outputRight.appendChild(phR);
  dom.placeholderRight = phR;

  // Reset thinking blocks
  [dom.thinkingLeft, dom.thinkingRight].forEach(el => {
    if (el) el.style.display = 'none';
  });
  if (dom.thinkingContentLeft)  dom.thinkingContentLeft.textContent  = '';
  if (dom.thinkingContentRight) dom.thinkingContentRight.textContent = '';
}

function toggleParams() {
  const open = dom.paramsGrid.style.display !== 'none';
  dom.paramsGrid.style.display = open ? 'none' : 'grid';
  dom.paramsArrow.classList.toggle('open', !open);
  $('params-toggle').setAttribute('aria-expanded', String(!open));
}

function resetParams() {
  dom.temperature.value = 0.8;
  dom.topP.value        = 0.9;
  dom.maxTokens.value   = 256;
  $('temperature-val').textContent = '0.8';
  $('top-p-val').textContent       = '0.90';
  $('max-tokens-val').textContent  = '256';
}

// ── Keyboard shortcut: Ctrl/Cmd + Enter to generate ──────────────────────────
dom.promptInput.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    sendPrompt();
  }
});

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Disclaimer: show unless already accepted this session
  if (!sessionStorage.getItem('disclaimer-accepted')) {
    dom.overlay.classList.remove('hidden');
  } else {
    dom.overlay.classList.add('hidden');
  }

  // Activate top-p value display (range already has oninput in HTML but sync here)
  $('top-p-val').textContent = parseFloat(dom.topP.value).toFixed(2);

  // Default family
  setFamily('qwen');
});

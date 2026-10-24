/**
 * SitePulse AI - Backend API Client
 */

const API_BASE_URL = '/api/v1';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Health check failed:', err);
    return {
      status: 'offline',
      version: '0.1.0',
      ollama_connected: false,
      ollama_url: 'http://localhost:11434',
      active_model: 'gemma4',
      available_models: [],
    };
  }
}

export async function fetchModels() {
  try {
    const res = await fetch(`${API_BASE_URL}/models`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { connected: false, active_model: 'gemma4', available_models: [] };
  }
}

export async function analyzeWebsite({ url, includeAi = true, model = null, customPrompt = null }) {
  const endpoint = `${API_BASE_URL}/analyze`;
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url,
      include_ai: includeAi,
      model,
      custom_prompt: customPrompt,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Audit failed with HTTP status ${res.status}`);
  }

  return await res.json();
}

export async function quickScanWebsite(url) {
  const endpoint = `${API_BASE_URL}/quick-scan`;
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, include_ai: false }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Quick scan failed with HTTP status ${res.status}`);
  }

  return await res.json();
}

export async function sendChatMessage({ message, url, contextIssues = [], model = null }) {
  const endpoint = `${API_BASE_URL}/chat`;
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      url,
      context_issues: contextIssues,
      model,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `AI Assistant chat failed: HTTP ${res.status}`);
  }

  return await res.json();
}

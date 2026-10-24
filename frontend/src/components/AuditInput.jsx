import React, { useState } from 'react';
import { 
  Globe, Search, Sparkles, Zap, Sliders, ChevronDown, ChevronUp, 
  RefreshCw, CheckCircle2, Shield, AlertCircle
} from 'lucide-react';

export default function AuditInput({
  onAudit,
  isLoading,
  loadingStep = '',
  availableModels = [],
  activeModel = 'gemma4',
}) {
  const [url, setUrl] = useState('');
  const [includeAi, setIncludeAi] = useState(true);
  const [selectedModel, setSelectedModel] = useState(activeModel);
  const [customPrompt, setCustomPrompt] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const quickUrls = [
    { name: 'Hacker News', url: 'https://news.ycombinator.com' },
    { name: 'GitHub', url: 'https://github.com' },
    { name: 'Stripe', url: 'https://stripe.com' },
    { name: 'Tailwind CSS', url: 'https://tailwindcss.com' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    const trimmed = url.trim();
    if (!trimmed) {
      setErrorMsg('Please enter a valid website URL to inspect.');
      return;
    }

    onAudit({
      url: trimmed,
      includeAi,
      model: selectedModel,
      customPrompt: customPrompt.trim() || null,
    });
  };

  const handleQuickUrl = (quickUrl) => {
    setUrl(quickUrl);
    setErrorMsg('');
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Hero Headline */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-cyan-500/10 via-indigo-500/10 to-violet-500/10 text-cyan-300 border border-cyan-500/20 backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>AI-Powered Website Health & Technical Audit Engine</span>
        </div>

        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
          Audit any website with{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
            instant AI precision.
          </span>
        </h1>

        <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Inspect technical SEO, accessibility practices, security response headers, and mobile readiness. Get prioritized, plain-English solutions with executable code fixes.
        </p>
      </div>

      {/* Main Audit Input Card */}
      <div className="glass-panel p-3 sm:p-4 rounded-2xl border border-slate-700/80 shadow-2xl relative glow-cyan">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
            {/* Input field */}
            <div className="relative flex-1">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-2 pointer-events-none text-slate-400">
                <Globe className="w-5 h-5 text-cyan-400" />
              </div>
              <input
                id="input-website-url"
                type="text"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (errorMsg) setErrorMsg('');
                }}
                disabled={isLoading}
                placeholder="Enter public URL (e.g. https://yourbusiness.com)"
                className="w-full bg-slate-900/90 text-white placeholder-slate-500 pl-12 pr-4 py-3.5 rounded-xl border border-slate-700 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 text-sm sm:text-base font-medium transition-all"
              />
            </div>

            {/* Run Audit Button */}
            <button
              id="btn-run-audit"
              type="submit"
              disabled={isLoading}
              className="px-6 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/25 active:scale-98 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                  <span>Inspecting...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-slate-950 fill-slate-950" />
                  <span>Run Audit</span>
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="text-xs text-rose-400 px-2 flex items-center gap-1.5 font-medium">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Quick options row */}
          <div className="pt-1 flex flex-wrap items-center justify-between gap-3 text-xs">
            {/* Mode toggle */}
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-slate-300 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={includeAi}
                  onChange={(e) => setIncludeAi(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-slate-900 w-4 h-4"
                />
                <span className="flex items-center gap-1 font-medium">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Deep AI Synthesis (Ollama)
                </span>
              </label>

              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
              >
                <Sliders className="w-3.5 h-3.5 text-slate-400" />
                <span>Options</span>
                {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            </div>

            {/* Quick URL Suggestions */}
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-slate-500">Quick Test:</span>
              {quickUrls.map((q) => (
                <button
                  key={q.name}
                  type="button"
                  onClick={() => handleQuickUrl(q.url)}
                  className="px-2 py-0.5 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-[11px] transition-colors"
                >
                  {q.name}
                </button>
              ))}
            </div>
          </div>

          {/* Advanced options collapsible */}
          {showAdvanced && (
            <div className="pt-3 border-t border-slate-800/80 space-y-3 text-xs bg-slate-950/40 p-3 rounded-xl">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Model selector */}
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">
                    Ollama Open-Weight Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full bg-slate-900 text-slate-200 p-2 rounded-lg border border-slate-700 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="gemma4">gemma4 (Recommended, Fast & Flexible)</option>
                    <option value="llama3.2">llama3.2 (Fast & Concise)</option>
                    <option value="llama3.1">llama3.1 (High Reasoning)</option>
                    <option value="mistral">mistral (Balanced)</option>
                    <option value="qwen2.5-coder">qwen2.5-coder (Code Fixes)</option>
                    {availableModels
                      .filter((m) => !['gemma4', 'llama3.2', 'llama3.1', 'mistral', 'qwen2.5-coder'].includes(m))
                      .map((m) => (
                        <option key={m} value={m}>
                          {m} (Installed Locally)
                        </option>
                      ))}
                  </select>
                </div>

                {/* Custom Focus Prompt */}
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">
                    Custom Advisor Focus (Optional)
                  </label>
                  <input
                    type="text"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="e.g. Focus on mobile page speed and WCAG 2.1"
                    className="w-full bg-slate-900 text-slate-200 p-2 rounded-lg border border-slate-700 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>
            </div>
          )}
        </form>

        {/* Loading Progress State */}
        {isLoading && (
          <div className="mt-4 p-4 rounded-xl bg-slate-950/80 border border-cyan-500/30 space-y-2.5 animate-pulse">
            <div className="flex items-center justify-between text-xs font-semibold text-cyan-400">
              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                <span>{loadingStep || 'Inspecting website...'}</span>
              </div>
              <span className="font-mono text-slate-400">Please wait</span>
            </div>

            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 animate-[pulse_1.5s_ease-in-out_infinite] w-3/4 rounded-full" />
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Step: HTTP Fetch → Metadata → Scoring → AI Remediation</span>
              <span>100% Deterministic Evidence</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

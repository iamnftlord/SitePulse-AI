import React from 'react';
import { Activity, Cpu, Sparkles, CheckCircle2, AlertCircle, RefreshCw, FileText, Globe } from 'lucide-react';

export default function Navbar({
  systemHealth,
  onSelectSample,
  onReset,
  hasAudit,
  onOpenExport,
}) {
  const isHealthy = systemHealth?.status === 'healthy';
  const isOllamaConnected = systemHealth?.ollama_connected;
  const activeModel = systemHealth?.active_model || 'llama3.2';

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand */}
        <div 
          onClick={onReset}
          className="flex items-center gap-3 cursor-pointer group transition-transform active:scale-95"
        >
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-violet-500 shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-shadow">
            <Activity className="w-5 h-5 text-white animate-pulse" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-300 bg-clip-text text-transparent">
                SitePulse
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
              Website Health & Technical Audit Agent
            </p>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="flex items-center gap-2.5 sm:gap-4">
          {/* Quick Demos */}
          <div className="hidden md:flex items-center gap-1.5 bg-slate-900/80 border border-slate-800 rounded-lg p-1 text-xs">
            <span className="text-slate-400 px-2 flex items-center gap-1 font-medium">
              <Globe className="w-3.5 h-3.5 text-cyan-400" /> Presets:
            </span>
            <button
              id="preset-cloudflow"
              onClick={() => onSelectSample('saas')}
              className="px-2.5 py-1 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors cursor-pointer"
              title="Load SaaS Infrastructure Audit (Score 88)"
            >
              CloudFlow (SaaS)
            </button>
            <button
              id="preset-artisan"
              onClick={() => onSelectSample('ecommerce')}
              className="px-2.5 py-1 rounded hover:bg-slate-800 text-rose-300 hover:text-rose-200 transition-colors cursor-pointer"
              title="Load E-commerce with critical defects (Score 54)"
            >
              Artisan Shop (Defects)
            </button>
          </div>

          {/* AI / Backend Status Badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium glass-card border border-slate-800">
            <div className={`w-2 h-2 rounded-full ${isOllamaConnected ? 'bg-emerald-400 animate-pulse' : 'bg-cyan-400'}`} />
            <span className="text-slate-300 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              {isOllamaConnected ? `Ollama (${activeModel})` : 'AI Heuristic Engine'}
            </span>
          </div>

          {/* Actions */}
          {hasAudit && (
            <button
              onClick={onOpenExport}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/80 transition-all active:scale-95 shadow-sm"
              title="Export Report"
            >
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export</span>
            </button>
          )}

          {hasAudit && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-md shadow-cyan-500/20 transition-all active:scale-95"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Audit</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

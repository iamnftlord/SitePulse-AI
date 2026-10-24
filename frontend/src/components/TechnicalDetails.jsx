import React, { useState } from 'react';
import { 
  Globe, Shield, Clock, FileCode, Check, X, 
  Layers, Smartphone, ExternalLink, ChevronDown, ChevronUp, Cpu
} from 'lucide-react';

export default function TechnicalDetails({ metadata }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!metadata) return null;

  const securityHeaderList = [
    { key: 'strict-transport-security', label: 'Strict-Transport-Security (HSTS)' },
    { key: 'content-security-policy', label: 'Content-Security-Policy (CSP)' },
    { key: 'x-frame-options', label: 'X-Frame-Options (Clickjacking)' },
    { key: 'x-content-type-options', label: 'X-Content-Type-Options' },
    { key: 'referrer-policy', label: 'Referrer-Policy' },
    { key: 'permissions-policy', label: 'Permissions-Policy' },
  ];

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 overflow-hidden">
      {/* Header / Toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Crawled Technical Metadata & Headers
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
                {metadata.status_code} {metadata.is_https ? 'HTTPS' : 'HTTP'}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Raw inspection data, security response headers, viewport, and detected framework stack
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
          <span>{isOpen ? 'Collapse' : 'Inspect'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expanded Details */}
      {isOpen && (
        <div className="p-6 border-t border-slate-800/80 space-y-6 bg-slate-950/40">
          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Server Latency</span>
              <span className="text-lg font-bold font-mono text-cyan-400 flex items-center gap-1 mt-0.5">
                <Clock className="w-3.5 h-3.5" /> {metadata.load_time_ms} ms
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Payload Weight</span>
              <span className="text-lg font-bold font-mono text-white flex items-center gap-1 mt-0.5">
                <FileCode className="w-3.5 h-3.5 text-indigo-400" />
                {(metadata.page_size_bytes / 1024).toFixed(1)} KB
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Mobile Viewport</span>
              <span className="text-lg font-bold font-mono flex items-center gap-1 mt-0.5">
                <Smartphone className="w-3.5 h-3.5" />
                {metadata.has_viewport ? (
                  <span className="text-emerald-400">Configured</span>
                ) : (
                  <span className="text-rose-400">Missing</span>
                )}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">HTML Language</span>
              <span className="text-lg font-bold font-mono text-white flex items-center gap-1 mt-0.5">
                <Globe className="w-3.5 h-3.5 text-cyan-400" />
                {metadata.html_lang ? `lang="${metadata.html_lang}"` : <span className="text-rose-400">None</span>}
              </span>
            </div>
          </div>

          {/* On-Page Meta Elements */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Extracted On-Page Meta Tags
            </h4>
            <div className="space-y-2.5 text-xs font-mono">
              {/* Title */}
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-cyan-400 font-semibold">&lt;title&gt;</span>
                  <span className="text-[11px] text-slate-400">
                    {metadata.title_length} chars {metadata.title_length > 60 && '(Truncated in SERPs)'}
                  </span>
                </div>
                <p className="text-slate-200 font-sans break-all">
                  {metadata.title || <span className="text-rose-400 italic">None detected</span>}
                </p>
              </div>

              {/* Meta Description */}
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-indigo-400 font-semibold">&lt;meta name="description"&gt;</span>
                  <span className="text-[11px] text-slate-400">
                    {metadata.meta_description_length} chars (Target: 120-160)
                  </span>
                </div>
                <p className="text-slate-200 font-sans break-all">
                  {metadata.meta_description || <span className="text-rose-400 italic">None detected</span>}
                </p>
              </div>

              {/* Canonical & OG */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                  <span className="text-slate-400 font-sans block text-[11px] mb-0.5">Canonical URL</span>
                  <span className="text-slate-200 truncate block">
                    {metadata.canonical_url || <span className="text-amber-400">Not set</span>}
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                  <span className="text-slate-400 font-sans text-[11px]">Social Share Cards</span>
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${metadata.has_open_graph ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-500'}`}>
                      OG: {metadata.has_open_graph ? 'Yes' : 'No'}
                    </span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${metadata.has_twitter_card ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-500'}`}>
                      Twitter: {metadata.has_twitter_card ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Security Headers Inspection Table */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Shield className="w-3.5 h-3.5 text-emerald-400" /> HTTP Security Response Headers
            </h4>
            <div className="rounded-xl border border-slate-800 overflow-hidden divide-y divide-slate-800/80 text-xs">
              {securityHeaderList.map(({ key, label }) => {
                const value = metadata.security_headers?.[key];
                const isPresent = Boolean(value);

                return (
                  <div key={key} className="p-3 bg-slate-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {isPresent ? (
                        <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      ) : (
                        <X className="w-4 h-4 text-rose-400 flex-shrink-0" />
                      )}
                      <div>
                        <span className="font-semibold text-white font-mono">{key}</span>
                        <span className="text-[11px] text-slate-400 block font-sans">{label}</span>
                      </div>
                    </div>

                    <div className="font-mono text-[11px]">
                      {isPresent ? (
                        <span className="text-emerald-300 bg-emerald-950/40 px-2 py-1 rounded border border-emerald-500/20 truncate max-w-xs block" title={value}>
                          {value}
                        </span>
                      ) : (
                        <span className="text-rose-400 bg-rose-950/40 px-2 py-1 rounded border border-rose-500/20">
                          Missing Header
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detected Technologies */}
          {metadata.technologies && metadata.technologies.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-cyan-400" /> Detected Technology Stack
              </h4>
              <div className="flex flex-wrap gap-2">
                {metadata.technologies.map((tech, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200"
                  >
                    <span className="font-semibold text-white">{tech.name}</span>
                    {tech.version && (
                      <span className="text-[10px] text-cyan-400 font-mono">v{tech.version}</span>
                    )}
                    <span className="text-[10px] text-slate-400 px-1.5 py-0.2 rounded bg-slate-800">
                      {tech.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

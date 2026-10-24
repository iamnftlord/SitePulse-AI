import React, { useState } from 'react';
import { X, Download, Printer, Copy, Check, FileText } from 'lucide-react';

export default function ExportModal({ isOpen, onClose, auditData }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !auditData) return null;

  const downloadJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(auditData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    const domain = auditData.url.replace(/https?:\/\//, '').replace(/[\/\?#].*$/, '');
    downloadAnchor.setAttribute('download', `sitepulse-audit-${domain}-${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const copyMarkdownSummary = () => {
    const lines = [
      `# SitePulse AI Technical Audit Report`,
      `**Target URL:** ${auditData.url}`,
      `**Health Score:** ${auditData.overall_score}/100 (Grade ${auditData.overall_grade})`,
      `**Duration:** ${auditData.duration_seconds}s | **Status:** ${auditData.metadata.status_code} (${auditData.metadata.is_https ? 'HTTPS' : 'HTTP'})`,
      ``,
      `## Executive Summary`,
      auditData.ai_analysis?.executive_summary || 'No AI summary generated.',
      ``,
      `## Category Health Scores`,
      `- **SEO:** ${auditData.category_scores.seo?.score || 0}/100 (${auditData.category_scores.seo?.passed_checks}/${auditData.category_scores.seo?.total_checks} checks)`,
      `- **Security:** ${auditData.category_scores.security?.score || 0}/100 (${auditData.category_scores.security?.passed_checks}/${auditData.category_scores.security?.total_checks} checks)`,
      `- **Accessibility:** ${auditData.category_scores.accessibility?.score || 0}/100 (${auditData.category_scores.accessibility?.passed_checks}/${auditData.category_scores.accessibility?.total_checks} checks)`,
      `- **Performance:** ${auditData.category_scores.performance?.score || 0}/100 (${auditData.category_scores.performance?.passed_checks}/${auditData.category_scores.performance?.total_checks} checks)`,
      ``,
      `## Detected Issues (${auditData.issues?.length || 0})`,
    ];

    auditData.issues?.forEach((issue, idx) => {
      lines.push(`${idx + 1}. [${issue.severity.toUpperCase()}] ${issue.title} (${issue.category})`);
      lines.push(`   - Impact: ${issue.impact}`);
      lines.push(`   - Recommendation: ${issue.recommendation}`);
      if (issue.code_snippet) {
        lines.push(`   - Fix: \`${issue.code_snippet.replace(/\n/g, ' ')}\``);
      }
    });

    const markdownText = lines.join('\n');
    navigator.clipboard.writeText(markdownText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const printReport = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-md rounded-2xl border border-slate-700 p-6 space-y-5 relative shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="space-y-1">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" /> Export Audit Report
          </h3>
          <p className="text-xs text-slate-400">
            Share or archive findings for {auditData.url}
          </p>
        </div>

        <div className="space-y-2.5">
          {/* Print / PDF */}
          <button
            onClick={printReport}
            className="w-full flex items-center justify-between p-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-left transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <Printer className="w-4 h-4" />
              </div>
              <div>
                <span className="font-semibold text-white text-sm block">Print or Save as PDF</span>
                <span className="text-[11px] text-slate-400">Clean print-ready report layout</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-cyan-400 group-hover:translate-x-0.5 transition-transform">
              Print →
            </span>
          </button>

          {/* Download JSON */}
          <button
            onClick={downloadJson}
            className="w-full flex items-center justify-between p-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-left transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Download className="w-4 h-4" />
              </div>
              <div>
                <span className="font-semibold text-white text-sm block">Download Full JSON</span>
                <span className="text-[11px] text-slate-400">Complete raw crawl & findings schema</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-cyan-400 group-hover:translate-x-0.5 transition-transform">
              .json →
            </span>
          </button>

          {/* Copy Markdown */}
          <button
            onClick={copyMarkdownSummary}
            className="w-full flex items-center justify-between p-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-left transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </div>
              <div>
                <span className="font-semibold text-white text-sm block">Copy Markdown Summary</span>
                <span className="text-[11px] text-slate-400">Formatted for GitHub issues or Slack</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-cyan-400">
              {copied ? 'Copied!' : 'Copy →'}
            </span>
          </button>
        </div>

        <div className="pt-2 text-center">
          <button
            onClick={onClose}
            className="text-xs text-slate-400 hover:text-slate-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

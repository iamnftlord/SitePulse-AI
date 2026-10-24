import React, { useState, useMemo } from 'react';
import { 
  ShieldAlert, AlertTriangle, AlertCircle, Info, Check, Copy, 
  ExternalLink, Search, Filter, ChevronDown, ChevronUp, Code2, Sparkles
} from 'lucide-react';

const SEVERITY_CONFIG = {
  critical: {
    label: 'Critical',
    icon: ShieldAlert,
    badge: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
    dot: 'bg-rose-500',
    border: 'border-l-rose-500',
  },
  high: {
    label: 'High Priority',
    icon: AlertTriangle,
    badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    dot: 'bg-amber-500',
    border: 'border-l-amber-500',
  },
  medium: {
    label: 'Medium',
    icon: AlertCircle,
    badge: 'bg-yellow-500/15 text-yellow-300 border-yellow-500/30',
    dot: 'bg-yellow-500',
    border: 'border-l-yellow-500',
  },
  low: {
    label: 'Low',
    icon: Info,
    badge: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
    dot: 'bg-blue-500',
    border: 'border-l-blue-500',
  },
  info: {
    label: 'Notice',
    icon: Info,
    badge: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
    dot: 'bg-slate-500',
    border: 'border-l-slate-500',
  },
};

export default function IssuesList({
  issues = [],
  selectedCategory,
  onSelectCategory,
  onAskAiAboutIssue,
}) {
  const [severityFilter, setSeverityFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedIssues, setExpandedIssues] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  // Toggle issue expansion
  const toggleIssue = (id) => {
    setExpandedIssues(prev => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Copy code snippet helper
  const copySnippet = (id, code) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filtered issues
  const filteredIssues = useMemo(() => {
    return issues.filter(issue => {
      // Category filter
      if (selectedCategory !== 'all' && issue.category !== selectedCategory) {
        return false;
      }
      // Severity filter
      if (severityFilter !== 'all' && issue.severity !== severityFilter) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesTitle = issue.title.toLowerCase().includes(query);
        const matchesDesc = issue.description.toLowerCase().includes(query);
        const matchesRec = issue.recommendation.toLowerCase().includes(query);
        return matchesTitle || matchesDesc || matchesRec;
      }
      return true;
    });
  }, [issues, selectedCategory, severityFilter, searchQuery]);

  const categories = [
    { id: 'all', label: 'All Categories' },
    { id: 'seo', label: 'SEO' },
    { id: 'security', label: 'Security' },
    { id: 'accessibility', label: 'Accessibility' },
    { id: 'performance', label: 'Performance' },
  ];

  const severities = [
    { id: 'all', label: 'All Severities' },
    { id: 'critical', label: 'Critical' },
    { id: 'high', label: 'High' },
    { id: 'medium', label: 'Medium' },
    { id: 'low', label: 'Low' },
  ];

  return (
    <div className="space-y-4">
      {/* Filters Toolbar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800/80 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search defects (e.g. meta, csp, alt text, title)..."
            className="w-full bg-slate-900/90 text-sm text-slate-200 pl-9 pr-4 py-2 rounded-lg border border-slate-700/80 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 placeholder-slate-500"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Category Filter */}
          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-lg border border-slate-800">
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => onSelectCategory(cat.id)}
                className={`px-2.5 py-1 text-xs rounded-md font-medium transition-colors ${
                  selectedCategory === cat.id
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900/90 text-xs text-slate-300 px-3 py-2 rounded-lg border border-slate-700/80 focus:outline-none focus:border-cyan-500"
          >
            {severities.map(s => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Result Count */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>
          Showing <span className="font-bold text-white">{filteredIssues.length}</span> of {issues.length} audit issues
        </span>
        {(selectedCategory !== 'all' || severityFilter !== 'all' || searchQuery) && (
          <button
            onClick={() => {
              onSelectCategory('all');
              setSeverityFilter('all');
              setSearchQuery('');
            }}
            className="text-cyan-400 hover:underline"
          >
            Reset Filters
          </button>
        )}
      </div>

      {/* Issue Cards */}
      {filteredIssues.length === 0 ? (
        <div className="glass-panel p-10 rounded-2xl border border-slate-800 text-center space-y-3">
          <div className="inline-flex p-3 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Check className="w-6 h-6" />
          </div>
          <h4 className="text-base font-bold text-white">No Issues Found</h4>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            No technical defects match your active filter criteria. Either the site passed all tests in this category or no issues were detected.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredIssues.map((issue) => {
            const isExpanded = expandedIssues[issue.id] ?? (issue.severity === 'critical' || issue.severity === 'high');
            const severityMeta = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.info;
            const SeverityIcon = severityMeta.icon;

            return (
              <div
                key={issue.id}
                className={`glass-card rounded-xl border border-slate-800/90 overflow-hidden transition-all border-l-4 ${severityMeta.border} hover:border-slate-700`}
              >
                {/* Header */}
                <div
                  onClick={() => toggleIssue(issue.id)}
                  className="p-4 sm:p-5 flex items-start sm:items-center justify-between gap-3 cursor-pointer select-none"
                >
                  <div className="flex items-start sm:items-center gap-3">
                    <span className="relative flex h-2.5 w-2.5 mt-1 sm:mt-0 flex-shrink-0">
                      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${severityMeta.dot}`}></span>
                      <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${severityMeta.dot}`}></span>
                    </span>

                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${severityMeta.badge}`}>
                          {severityMeta.label}
                        </span>
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                          {issue.category}
                        </span>
                        {issue.element && (
                          <span className="text-[11px] text-cyan-300 font-mono bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-500/20">
                            {issue.element}
                          </span>
                        )}
                      </div>
                      <h4 className="text-base font-bold text-white">
                        {issue.title}
                      </h4>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-slate-400 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onAskAiAboutIssue?.(issue);
                      }}
                      className="hidden sm:flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 transition-colors"
                      title="Ask AI how to fix this"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Ask AI</span>
                    </button>
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </div>
                </div>

                {/* Body */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-1 border-t border-slate-800/80 space-y-4 text-xs bg-slate-950/30">
                    {/* Findings & Impact */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px] block">
                          Inspection Finding
                        </span>
                        <p className="text-slate-300 leading-relaxed font-sans">
                          {issue.description}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-semibold text-amber-300 uppercase tracking-wider text-[11px] block">
                          Business & SEO Impact
                        </span>
                        <p className="text-slate-300 leading-relaxed font-sans">
                          {issue.impact}
                        </p>
                      </div>
                    </div>

                    {/* Recommendation */}
                    <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-emerald-400 flex items-center gap-1.5 text-xs">
                          <Check className="w-3.5 h-3.5" /> Recommended Remediation
                        </span>
                        {issue.docs_url && (
                          <a
                            href={issue.docs_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                          >
                            Documentation <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                      <p className="text-slate-200 leading-relaxed">
                        {issue.recommendation}
                      </p>
                    </div>

                    {/* Code Snippet Fix */}
                    {issue.code_snippet && (
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                            <Code2 className="w-3.5 h-3.5 text-cyan-400" /> Proposed Fix Implementation
                          </span>
                          <button
                            onClick={() => copySnippet(issue.id, issue.code_snippet)}
                            className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors text-[11px] font-medium"
                          >
                            {copiedId === issue.id ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-400" />
                                <span className="text-emerald-400">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3 text-slate-400" />
                                <span>Copy Code</span>
                              </>
                            )}
                          </button>
                        </div>
                        <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-cyan-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                          {issue.code_snippet}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

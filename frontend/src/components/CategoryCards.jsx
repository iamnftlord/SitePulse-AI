import React from 'react';
import { Search, Shield, Eye, Gauge, Check, AlertCircle } from 'lucide-react';

const CATEGORY_META = {
  seo: {
    title: 'On-Page SEO',
    description: 'Title tags, meta descriptions, headings, canonicals & Open Graph.',
    icon: Search,
    color: 'from-blue-500 to-cyan-500',
    borderColor: 'group-hover:border-cyan-500/40',
    badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  },
  security: {
    title: 'Security Indicators',
    description: 'HTTPS enforcement, HSTS, Content-Security-Policy & anti-clickjacking.',
    icon: Shield,
    color: 'from-emerald-500 to-teal-500',
    borderColor: 'group-hover:border-emerald-500/40',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  },
  accessibility: {
    title: 'Accessibility & Mobile',
    description: 'Responsive viewport tags, image alt text coverage & lang tags.',
    icon: Eye,
    color: 'from-purple-500 to-indigo-500',
    borderColor: 'group-hover:border-indigo-500/40',
    badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  },
  performance: {
    title: 'Performance & Stack',
    description: 'Server response latency, payload weight & detected technology stack.',
    icon: Gauge,
    color: 'from-amber-500 to-orange-500',
    borderColor: 'group-hover:border-amber-500/40',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  },
};

export default function CategoryCards({ categoryScores = {}, onFilterCategory, selectedCategory }) {
  const categories = ['seo', 'security', 'accessibility', 'performance'];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {categories.map((catKey) => {
        const cat = categoryScores[catKey] || {
          category: catKey,
          score: 0,
          grade: '—',
          passed_checks: 0,
          total_checks: 0,
          issues_count: 0,
        };

        const meta = CATEGORY_META[catKey] || {
          title: catKey.toUpperCase(),
          description: '',
          icon: Gauge,
          color: 'from-cyan-500 to-blue-500',
          borderColor: 'group-hover:border-cyan-500/40',
          badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
        };

        const Icon = meta.icon;
        const isSelected = selectedCategory === catKey;

        // Progress color
        let barColor = 'bg-cyan-500';
        if (cat.score >= 85) barColor = 'bg-emerald-500';
        else if (cat.score >= 70) barColor = 'bg-cyan-500';
        else if (cat.score >= 50) barColor = 'bg-amber-500';
        else barColor = 'bg-rose-500';

        return (
          <div
            key={catKey}
            onClick={() => onFilterCategory(isSelected ? 'all' : catKey)}
            className={`glass-card p-5 rounded-xl border transition-all cursor-pointer group hover:-translate-y-1 relative overflow-hidden ${
              isSelected
                ? 'border-cyan-500/80 ring-2 ring-cyan-500/20 shadow-lg shadow-cyan-500/10 bg-slate-900/90'
                : 'border-slate-800/80 hover:border-slate-700 bg-slate-900/50'
            }`}
          >
            {/* Top row */}
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className={`p-2 rounded-lg bg-gradient-to-tr ${meta.color} text-white shadow-sm`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white group-hover:text-cyan-300 transition-colors">
                    {meta.title}
                  </h4>
                  <span className="text-[11px] text-slate-400">
                    {cat.passed_checks}/{cat.total_checks} Checks Passed
                  </span>
                </div>
              </div>

              {/* Grade badge */}
              <div className={`px-2 py-0.5 rounded text-xs font-bold font-mono border ${meta.badgeColor}`}>
                {cat.grade}
              </div>
            </div>

            {/* Score & Progress bar */}
            <div className="mt-4">
              <div className="flex items-baseline justify-between mb-1.5">
                <span className="text-2xl font-black text-white font-mono">
                  {cat.score}<span className="text-xs text-slate-400 font-normal">/100</span>
                </span>
                <span className="text-xs font-medium text-slate-400">
                  {cat.issues_count === 0 ? (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <Check className="w-3 h-3" /> Clean
                    </span>
                  ) : (
                    <span className="text-amber-400 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {cat.issues_count} {cat.issues_count === 1 ? 'issue' : 'issues'}
                    </span>
                  )}
                </span>
              </div>

              {/* Bar */}
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full ${barColor} transition-all duration-700 ease-out`}
                  style={{ width: `${Math.min(100, Math.max(0, cat.score))}%` }}
                />
              </div>
            </div>

            <p className="mt-3 text-[11px] text-slate-400 leading-normal line-clamp-2">
              {meta.description}
            </p>
          </div>
        );
      })}
    </div>
  );
}

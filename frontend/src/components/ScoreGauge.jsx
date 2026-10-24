import React from 'react';
import { Award, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

export default function ScoreGauge({ score = 0, grade = 'N/A', issues = [] }) {
  // SVG circular gauge math
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.min(100, Math.max(0, score));
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  // Grade color theme
  let strokeColor = '#06b6d4'; // cyan
  let glowClass = 'glow-cyan';
  let gradeBg = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
  let verdict = 'Good Health';
  let verdictDesc = 'Minor optimizations detected. Core fundamentals are stable.';

  if (clampedScore >= 90) {
    strokeColor = '#10b981'; // emerald
    glowClass = 'glow-emerald';
    gradeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    verdict = 'Exceptional';
    verdictDesc = 'Superior performance, accessibility, and security compliance.';
  } else if (clampedScore >= 75) {
    strokeColor = '#38bdf8'; // sky
    glowClass = 'glow-cyan';
    gradeBg = 'bg-sky-500/10 text-sky-400 border-sky-500/30';
    verdict = 'Solid Architecture';
    verdictDesc = 'Strong baseline with targeted opportunities for improvement.';
  } else if (clampedScore >= 50) {
    strokeColor = '#f59e0b'; // amber
    glowClass = 'glow-amber';
    gradeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    verdict = 'Needs Attention';
    verdictDesc = 'Multiple technical deficiencies impacting discoverability and security.';
  } else {
    strokeColor = '#f43f5e'; // rose
    glowClass = 'glow-rose';
    gradeBg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    verdict = 'Critical Remediation Needed';
    verdictDesc = 'High-severity security or SEO obstacles requiring immediate attention.';
  }

  // Count severities
  const criticalCount = issues.filter(i => i.severity === 'critical').length;
  const highCount = issues.filter(i => i.severity === 'high').length;
  const mediumCount = issues.filter(i => i.severity === 'medium').length;

  return (
    <div className={`glass-panel p-6 sm:p-7 rounded-2xl flex flex-col md:flex-row items-center gap-6 md:gap-10 border border-slate-800 ${glowClass} relative overflow-hidden`}>
      {/* Background ambient gradient */}
      <div 
        className="absolute -right-10 -bottom-10 w-64 h-64 rounded-full blur-3xl opacity-10 pointer-events-none"
        style={{ backgroundColor: strokeColor }}
      />

      {/* Radial Gauge */}
      <div className="relative flex-shrink-0 flex items-center justify-center">
        <svg className="w-40 h-40 sm:w-44 sm:h-44 -rotate-90 transform" viewBox="0 0 160 160">
          {/* Background track */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="currentColor"
            strokeWidth="11"
            className="text-slate-800/80"
            fill="transparent"
          />
          {/* Animated score bar */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={strokeColor}
            strokeWidth="11"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            fill="transparent"
          />
        </svg>

        {/* Center content */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-4xl sm:text-5xl font-black tracking-tight text-white font-mono">
            {score}
          </span>
          <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
            Health Score
          </span>
          <div className={`mt-1 px-2.5 py-0.5 rounded-full text-xs font-bold border ${gradeBg}`}>
            Grade {grade}
          </div>
        </div>
      </div>

      {/* Score Description & Quick Stats */}
      <div className="flex-1 text-center md:text-left space-y-3">
        <div className="flex flex-wrap items-center justify-center md:justify-start gap-2.5">
          <h3 className="text-2xl font-extrabold text-white">
            {verdict}
          </h3>
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            Weighted Rule Matrix
          </span>
        </div>

        <p className="text-sm text-slate-300 max-w-xl leading-relaxed">
          {verdictDesc}
        </p>

        {/* Defect severity badges */}
        <div className="pt-2 flex flex-wrap items-center justify-center md:justify-start gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <span className="text-slate-400">Total Findings:</span>
            <span className="font-bold text-white font-mono">{issues.length}</span>
          </div>

          {criticalCount > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-medium">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
              <span>{criticalCount} Critical</span>
            </div>
          )}

          {highCount > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-medium">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>{highCount} High Priority</span>
            </div>
          )}

          {criticalCount === 0 && highCount === 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              <span>Zero Critical Flaws</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

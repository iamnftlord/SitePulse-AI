import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { 
  Globe, Shield, Sparkles, Layers, FileText, ArrowUpRight, 
  CheckCircle, AlertTriangle, ExternalLink, Zap, RefreshCw, Info, Lock
} from 'lucide-react';

import Navbar from './components/Navbar';
import AuditInput from './components/AuditInput';
import ScoreGauge from './components/ScoreGauge';
import CategoryCards from './components/CategoryCards';
import TechnicalDetails from './components/TechnicalDetails';
import IssuesList from './components/IssuesList';
import AiAssistant from './components/AiAssistant';
import ExportModal from './components/ExportModal';

import { analyzeWebsite, fetchHealth, fetchModels } from './services/api';
import { SAMPLE_AUDITS } from './services/sampleAudits';

export default function App() {
  const [systemHealth, setSystemHealth] = useState(null);
  const [auditData, setAuditData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  // Active filters and views
  const [activeTab, setActiveTab] = useState('issues'); // 'issues' | 'ai' | 'tech'
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeAiIssue, setActiveAiIssue] = useState(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Load backend health on mount
  useEffect(() => {
    async function initHealth() {
      const health = await fetchHealth();
      setSystemHealth(health);
    }
    initHealth();
  }, []);

  // Trigger confetti if score is great
  const triggerCelebration = (score) => {
    if (score >= 85) {
      confetti({
        particleCount: 60,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#06b6d4', '#10b981', '#6366f1'],
      });
    }
  };

  // Perform full website audit
  const handleRunAudit = async ({ url, includeAi, model, customPrompt }) => {
    setIsLoading(true);
    setErrorMessage(null);
    setLoadingStep('Connecting and verifying website availability...');

    try {
      // Step simulator for rich UX feedback
      const stepTimer1 = setTimeout(() => {
        setLoadingStep('Extracting HTML, meta tags, and security headers...');
      }, 700);

      const stepTimer2 = setTimeout(() => {
        setLoadingStep(includeAi ? 'Running deterministic checks & synthesizing AI recommendations...' : 'Evaluating weighted score matrix...');
      }, 1600);

      const result = await analyzeWebsite({
        url,
        includeAi,
        model,
        customPrompt,
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);

      setAuditData(result);
      setSelectedCategory('all');
      setActiveTab('issues');
      triggerCelebration(result.overall_score);
    } catch (err) {
      console.error('Audit failed:', err);
      setErrorMessage(err.message || 'Unable to audit target website. Please ensure URL is public and valid.');
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  // Load sample preset
  const handleSelectSample = (sampleKey) => {
    const sample = SAMPLE_AUDITS[sampleKey] || SAMPLE_AUDITS.saas;
    setAuditData(sample);
    setSelectedCategory('all');
    setActiveTab('issues');
    setErrorMessage(null);
    triggerCelebration(sample.overall_score);
  };

  // Reset to empty state
  const handleReset = () => {
    setAuditData(null);
    setErrorMessage(null);
    setSelectedCategory('all');
    setActiveTab('issues');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080c15] text-slate-100 bg-grid-pattern relative">
      {/* Navbar */}
      <Navbar
        systemHealth={systemHealth}
        onSelectSample={handleSelectSample}
        onReset={handleReset}
        hasAudit={Boolean(auditData)}
        onOpenExport={() => setIsExportModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Error Banner */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-bold block">Audit Encountered an Issue:</span>
              <p className="text-xs text-rose-200 mt-0.5">{errorMessage}</p>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-xs text-rose-400 hover:text-white"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Input Bar or Results */}
        {!auditData ? (
          <div className="py-6 sm:py-12">
            <AuditInput
              onAudit={handleRunAudit}
              isLoading={isLoading}
              loadingStep={loadingStep}
              availableModels={systemHealth?.available_models || []}
              activeModel={systemHealth?.active_model || 'gemma4'}
            />

            {/* Feature highlights grid below input */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
                  <Shield className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-white text-base">Security & Header Hygiene</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Scans for HSTS preloading, Content-Security-Policy, Anti-Clickjacking (X-Frame-Options), and MIME sniffing vulnerabilities.
                </p>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
                  <Globe className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-white text-base">SEO & Accessibility Matrix</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Evaluates title bounds, meta description density, H1 hierarchy, responsive viewport configurations, and image alt attributes.
                </p>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-white text-base">Open-Weight AI Remediation</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Ollama-powered AI explains each defect in simple human language and generates copy-paste code snippets for instant fixes.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8 animate-[fadeIn_0.4s_ease-out]">
            {/* Top Audit Target Info Bar */}
            <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  <Globe className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm font-mono truncate max-w-md">
                      {auditData.url}
                    </span>
                    <a
                      href={auditData.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-slate-400 hover:text-cyan-400 transition-colors"
                      title="Open website in new tab"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </a>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400 mt-0.5">
                    <span className="flex items-center gap-1">
                      {auditData.metadata.is_https ? (
                        <span className="text-emerald-400 flex items-center gap-1 font-mono">
                          <Lock className="w-3 h-3" /> HTTPS
                        </span>
                      ) : (
                        <span className="text-rose-400 flex items-center gap-1 font-mono">
                          HTTP Insecure
                        </span>
                      )}
                    </span>
                    <span>•</span>
                    <span>Status: {auditData.metadata.status_code} OK</span>
                    <span>•</span>
                    <span>Load: {auditData.metadata.load_time_ms}ms</span>
                    <span>•</span>
                    <span>Scan took {auditData.duration_seconds}s</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsExportModalOpen(true)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                >
                  <FileText className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Export Report</span>
                </button>
              </div>
            </div>

            {/* Overall Score Gauge */}
            <ScoreGauge
              score={auditData.overall_score}
              grade={auditData.overall_grade}
              issues={auditData.issues || []}
            />

            {/* Category Breakdown Cards */}
            <CategoryCards
              categoryScores={auditData.category_scores || {}}
              onFilterCategory={(cat) => {
                setSelectedCategory(cat);
                setActiveTab('issues');
              }}
              selectedCategory={selectedCategory}
            />

            {/* Tab Navigation for Detailed Sections */}
            <div className="flex items-center border-b border-slate-800 gap-6 text-sm font-semibold">
              <button
                id="tab-issues"
                onClick={() => setActiveTab('issues')}
                className={`pb-3 flex items-center gap-2 transition-all relative cursor-pointer ${
                  activeTab === 'issues'
                    ? 'text-cyan-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <span>Audit Findings ({auditData.issues?.length || 0})</span>
                {activeTab === 'issues' && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 rounded-full" />
                )}
              </button>

              <button
                id="tab-ai"
                onClick={() => setActiveTab('ai')}
                className={`pb-3 flex items-center gap-2 transition-all relative cursor-pointer ${
                  activeTab === 'ai'
                    ? 'text-cyan-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span>AI Action Plan & Assistant</span>
                {activeTab === 'ai' && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 rounded-full" />
                )}
              </button>

              <button
                id="tab-tech"
                onClick={() => setActiveTab('tech')}
                className={`pb-3 flex items-center gap-2 transition-all relative cursor-pointer ${
                  activeTab === 'tech'
                    ? 'text-cyan-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Layers className="w-4 h-4 text-indigo-400" />
                <span>Crawl Headers & Tech Stack</span>
                {activeTab === 'tech' && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 rounded-full" />
                )}
              </button>
            </div>

            {/* Active Tab Views */}
            {activeTab === 'issues' && (
              <IssuesList
                issues={auditData.issues || []}
                selectedCategory={selectedCategory}
                onSelectCategory={setSelectedCategory}
                onAskAiAboutIssue={(issue) => {
                  setActiveAiIssue(issue);
                  setActiveTab('ai');
                }}
              />
            )}

            {activeTab === 'ai' && (
              <AiAssistant
                aiAnalysis={auditData.ai_analysis}
                metadata={auditData.metadata}
                issues={auditData.issues || []}
                url={auditData.url}
                activeAiIssue={activeAiIssue}
                onClearActiveAiIssue={() => setActiveAiIssue(null)}
              />
            )}

            {activeTab === 'tech' && (
              <TechnicalDetails metadata={auditData.metadata} />
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full glass-panel border-t border-slate-800/80 mt-16 py-6 px-4 text-xs text-slate-500 text-center">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">SitePulse AI</span>
            <span>—</span>
            <span>Open-Source Website Health & Technical Audit Platform</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>FastAPI + Python</span>
            <span>•</span>
            <span>React + Vite</span>
            <span>•</span>
            <span>Ollama AI (Local Open-Weight)</span>
          </div>
        </div>
      </footer>

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        auditData={auditData}
      />
    </div>
  );
}

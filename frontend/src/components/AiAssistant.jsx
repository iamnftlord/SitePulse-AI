import React, { useState } from 'react';
import { 
  Sparkles, CheckCircle, AlertTriangle, ArrowRight, Copy, Check, 
  Send, MessageSquare, Bot, User, RefreshCw, Zap
} from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function AiAssistant({
  aiAnalysis,
  metadata,
  issues = [],
  url,
  activeAiIssue,
  onClearActiveAiIssue,
}) {
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'ai',
      text: "Hello! I'm SitePulse AI, your website technical auditor. Ask me how to implement any fix, optimize your meta tags, or resolve security headers.",
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  // If parent triggered an "Ask AI" on a specific issue
  React.useEffect(() => {
    if (activeAiIssue) {
      const prompt = `How do I resolve the issue: "${activeAiIssue.title}" (${activeAiIssue.id})? Provide step-by-step guidance.`;
      handleSendMessage(prompt);
      onClearActiveAiIssue?.();
    }
  }, [activeAiIssue]);

  const handleSendMessage = async (customText = null) => {
    const text = (customText || inputValue).trim();
    if (!text || isSending) return;

    // Add user message
    const userMsg = { sender: 'user', text };
    setChatMessages((prev) => [...prev, userMsg]);
    if (!customText) setInputValue('');
    setIsSending(true);

    try {
      const res = await sendChatMessage({
        message: text,
        url,
        contextIssues: issues.slice(0, 5),
      });

      setChatMessages((prev) => [
        ...prev,
        { sender: 'ai', text: res.reply || 'Analysis completed.' },
      ]);
    } catch (err) {
      // Fallback response for chat if backend or model offline
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: `Here is the recommended fix for "${text}":\n\n1. Ensure your server configuration is updated (e.g., Nginx, Apache, or Vercel config).\n2. Test using standard curl inspection: \`curl -I ${url || 'https://yoursite.com'}\`\n3. Re-run SitePulse AI audit to verify 100% compliance.`,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const copyCode = (idx, code) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (!aiAnalysis) {
    return (
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-3">
        <Sparkles className="w-8 h-8 text-cyan-400 mx-auto animate-pulse" />
        <h3 className="text-lg font-bold text-white">AI Recommendations Skipped</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          This audit was run in Quick Scan mode. Run an audit with "Deep AI Analysis" enabled to generate prioritized remediation steps using open-weight AI models.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Executive Summary Card */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-indigo-500/30 glow-indigo relative overflow-hidden">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white shadow-md shadow-indigo-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-extrabold text-white">
                AI Executive Synthesis
              </h3>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                Model: {aiAnalysis.model_used || 'Ollama / Gemma 4'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Strategic recommendations generated from technical crawl evidence
            </p>
          </div>
        </div>

        <p className="text-sm text-slate-200 leading-relaxed font-sans bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          {aiAnalysis.executive_summary}
        </p>

        {/* Strengths & Weaknesses 2-Column Grid */}
        <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Strengths */}
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2.5">
            <h4 className="font-bold text-emerald-400 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
              <CheckCircle className="w-4 h-4" /> Detected Strengths
            </h4>
            <ul className="space-y-2">
              {aiAnalysis.strengths?.map((str, i) => (
                <li key={i} className="text-slate-300 flex items-start gap-2">
                  <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                  <span>{str}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Critical Weaknesses */}
          <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/20 space-y-2.5">
            <h4 className="font-bold text-rose-400 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
              <AlertTriangle className="w-4 h-4" /> Priority Areas to Address
            </h4>
            <ul className="space-y-2">
              {aiAnalysis.critical_weaknesses?.map((weak, i) => (
                <li key={i} className="text-slate-300 flex items-start gap-2">
                  <span className="text-rose-400 font-bold mt-0.5">⚠</span>
                  <span>{weak}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Prioritized Action Plan */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <h4 className="text-base font-bold text-white">
              Prioritized Remediation Roadmap
            </h4>
          </div>
          <span className="text-xs text-slate-400">
            Ranked by ROI & Effort
          </span>
        </div>

        <div className="space-y-3">
          {aiAnalysis.action_plan?.map((planItem, idx) => (
            <div
              key={idx}
              className="glass-card p-5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="w-6 h-6 rounded-full bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold text-xs flex items-center justify-center font-mono shadow-sm">
                    #{planItem.priority_rank}
                  </span>
                  <h5 className="font-bold text-sm text-white">
                    {planItem.action}
                  </h5>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-medium">
                    {planItem.effort}
                  </span>
                  <span className="text-slate-400 capitalize">
                    {planItem.category}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300">
                <span className="font-semibold text-slate-200">Expected Impact:</span> {planItem.expected_impact}
              </p>

              {planItem.code_example && (
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span className="font-semibold">Implementation Example</span>
                    <button
                      onClick={() => copyCode(idx, planItem.code_example)}
                      className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300"
                    >
                      {copiedIndex === idx ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy snippet</span>
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-cyan-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">
                    {planItem.code_example}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Interactive AI Chat Assistant Box */}
      <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            <h4 className="text-base font-bold text-white">
              Ask SitePulse AI
            </h4>
          </div>
          <span className="text-xs text-slate-400">
            Interactive follow-up questions for this site
          </span>
        </div>

        {/* Chat message history */}
        <div className="max-h-64 overflow-y-auto space-y-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
          {chatMessages.map((msg, i) => (
            <div
              key={i}
              className={`flex items-start gap-2.5 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'ai' && (
                <div className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5" />
                </div>
              )}

              <div
                className={`p-3 rounded-xl max-w-lg leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-cyan-600 text-white rounded-tr-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none font-sans whitespace-pre-wrap'
                }`}
              >
                {msg.text}
              </div>

              {msg.sender === 'user' && (
                <div className="w-6 h-6 rounded-full bg-slate-700 text-slate-300 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))}

          {isSending && (
            <div className="flex items-center gap-2 text-xs text-slate-400 italic">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
              <span>SitePulse AI is crafting a response...</span>
            </div>
          )}
        </div>

        {/* Prompt Suggestions */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <span className="text-slate-400">Try asking:</span>
          <button
            onClick={() => handleSendMessage('How do I configure HSTS in Nginx?')}
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            "How do I configure HSTS in Nginx?"
          </button>
          <button
            onClick={() => handleSendMessage('Suggest a compelling meta description for this website.')}
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            "Suggest an SEO meta description"
          </button>
          <button
            onClick={() => handleSendMessage('Explain Content-Security-Policy in simple terms for a non-technical founder.')}
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            "Explain CSP simply"
          </button>
        </div>

        {/* Input box */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything about resolving these findings or improving your health score..."
            className="flex-1 bg-slate-900 text-xs text-slate-200 px-4 py-2.5 rounded-xl border border-slate-700 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 placeholder-slate-500"
          />
          <button
            type="submit"
            disabled={isSending || !inputValue.trim()}
            className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-cyan-500/20 active:scale-95"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}

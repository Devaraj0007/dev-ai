"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, RefreshCw, Send, AlertCircle, FileCheck } from "lucide-react";
import { HeroSection } from "@/components/ui/hero-section";
import { AnimatedButton } from "@/components/ui/animated-button";
import { ResultCard, AskResponseData } from "@/components/ui/result-card";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResponseData | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      const data: AskResponseData = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to reach backend API. Is uvicorn running on port 8000?");
    } finally {
      setIsLoading(false);
    }
  };

  const handleIngest = async () => {
    setIsIngesting(true);
    setIngestStatus(null);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/ingest`, {
        method: "POST",
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Ingest failed: ${res.status}`);
      }

      const data = await res.json();
      setIngestStatus(
        `Successfully indexed ${data.chunks_indexed} chunks from ${data.documents?.length || 0} documents.`
      );
    } catch (err: any) {
      setError(err.message || "Failed to trigger ingestion.");
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-slate-100 flex flex-col items-center px-4 py-8 antialiased">
      <div className="w-full max-w-4xl space-y-8">
        {/* Hero Section */}
        <HeroSection />

        {/* Action Toolbar & Ingest Button */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="flex items-center justify-between gap-4 bg-slate-900/50 p-3 rounded-2xl border border-slate-800 backdrop-blur-md"
        >
          <div className="flex items-center gap-2 text-xs text-slate-400 pl-2">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            <span>Backend: <strong className="text-slate-200">{API_BASE_URL}</strong></span>
          </div>

          <AnimatedButton
            variant="secondary"
            size="sm"
            onClick={handleIngest}
            isLoading={isIngesting}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isIngesting ? "animate-spin" : ""}`} />
            <span>Ingest Source Docs</span>
          </AnimatedButton>
        </motion.div>

        {/* Ingest Status Toast */}
        {ingestStatus && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-3 text-xs bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 rounded-xl text-center shadow-md backdrop-blur-md"
          >
            ✓ {ingestStatus}
          </motion.div>
        )}

        {/* Search & Question Form */}
        <motion.form
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          onSubmit={handleAsk}
          className="relative flex items-center gap-3 bg-slate-900/90 border border-slate-700/60 p-2.5 rounded-2xl shadow-2xl focus-within:border-indigo-500/80 transition-all backdrop-blur-xl"
        >
          <Search className="w-5 h-5 text-slate-400 ml-3 shrink-0" />
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="w-full bg-transparent text-slate-100 placeholder-slate-400 text-sm focus:outline-none px-2 py-2"
          />
          <AnimatedButton
            type="submit"
            variant="glow"
            size="md"
            isLoading={isLoading}
            disabled={!question.trim() || isLoading}
          >
            <span>Ask</span>
            <Send className="w-4 h-4" />
          </AnimatedButton>
        </motion.form>

        {/* Error Alert */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-red-950/40 border border-red-500/40 text-red-300 rounded-xl text-sm flex items-center gap-3 backdrop-blur-md"
          >
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}

        {/* Loading State */}
        {isLoading && <LoadingSkeleton />}

        {/* Result Card */}
        {result && !isLoading && (
          <ResultCard data={result} />
        )}
      </div>

      {/* Footer */}
      <footer className="mt-16 text-center text-xs text-slate-600">
        Dev AI — Grounded Q&A Web Frontend
      </footer>
    </main>
  );
}

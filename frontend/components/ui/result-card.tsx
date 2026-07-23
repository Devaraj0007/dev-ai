"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Bookmark,
  CheckCircle,
} from "lucide-react";
import { GroundingBadge, SufficiencyBadge } from "./grounding-badge";
import { cn } from "@/lib/utils";

export interface SourceItem {
  marker: string;
  source: string;
  excerpt: string;
}

export interface AskResponseData {
  answer: string;
  sources: SourceItem[];
  sources_sufficient: boolean;
  gap_note: string;
  grounded: boolean;
}

interface ResultCardProps {
  data: AskResponseData;
  className?: string;
}

export function ResultCard({ data, className }: ResultCardProps) {
  const [showSources, setShowSources] = useState(true);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={cn(
        "relative rounded-2xl bg-slate-900/80 border border-slate-800 p-6 md:p-8 backdrop-blur-xl shadow-2xl overflow-hidden",
        "before:absolute before:inset-0 before:bg-gradient-to-b before:from-slate-800/30 before:to-transparent before:pointer-events-none",
        className
      )}
    >
      {/* Header section with Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-bold text-slate-100">Research Answer</h2>
        </div>
        <div className="flex items-center gap-2">
          <GroundingBadge grounded={data.grounded} />
          <SufficiencyBadge sufficient={data.sources_sufficient} />
        </div>
      </div>

      {/* Answer Body */}
      <div className="prose prose-invert max-w-none mb-6">
        <p className="text-slate-200 text-base leading-relaxed whitespace-pre-wrap font-sans">
          {data.answer}
        </p>
      </div>

      {/* Gap Note Alert (if present) */}
      {data.gap_note && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="mb-6 p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-300 text-sm flex items-start gap-3 backdrop-blur-md"
        >
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block mb-0.5">Coverage Gap Note</span>
            <span>{data.gap_note}</span>
          </div>
        </motion.div>
      )}

      {/* Sources / Citations Section */}
      {data.sources && data.sources.length > 0 && (
        <div className="mt-6 pt-4 border-t border-slate-800/60">
          <button
            onClick={() => setShowSources(!showSources)}
            className="flex items-center justify-between w-full text-slate-400 hover:text-slate-200 text-xs font-semibold uppercase tracking-wider transition-colors py-1 cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <Bookmark className="w-4 h-4 text-indigo-400" />
              <span>Cited Sources ({data.sources.length})</span>
            </div>
            {showSources ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          <AnimatePresence>
            {showSources && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-3 space-y-2.5 overflow-hidden"
              >
                {data.sources.map((src, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 transition-all hover:border-slate-700"
                  >
                    <div className="flex items-center justify-between mb-1.5 font-medium text-slate-200">
                      <span className="inline-flex items-center gap-1 text-indigo-400 font-bold bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/40">
                        {src.marker || `[${idx + 1}]`}
                      </span>
                      <span className="text-slate-400 truncate max-w-[250px] sm:max-w-md font-mono">
                        {src.source}
                      </span>
                    </div>
                    {src.excerpt && (
                      <p className="text-slate-400 italic line-clamp-3 bg-slate-900/40 p-2 rounded border border-slate-800/40 mt-1">
                        "{src.excerpt}"
                      </p>
                    )}
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}

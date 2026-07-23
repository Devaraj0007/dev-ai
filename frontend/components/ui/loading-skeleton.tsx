"use client";

import { motion } from "framer-motion";
import { Loader2, Sparkles } from "lucide-react";

export function LoadingSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      className="rounded-2xl bg-slate-900/80 border border-slate-800 p-8 backdrop-blur-xl shadow-xl space-y-6 relative overflow-hidden"
    >
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
          <span className="text-slate-300 font-semibold text-sm">
            Synthesizing Grounded Answer...
          </span>
        </div>
        <div className="h-6 w-24 bg-slate-800/80 rounded-full animate-pulse" />
      </div>

      <div className="space-y-3">
        <div className="h-4 bg-slate-800/80 rounded w-5/6 animate-pulse" />
        <div className="h-4 bg-slate-800/60 rounded w-full animate-pulse" />
        <div className="h-4 bg-slate-800/70 rounded w-4/5 animate-pulse" />
        <div className="h-4 bg-slate-800/50 rounded w-2/3 animate-pulse" />
      </div>

      <div className="pt-4 border-t border-slate-800/60 flex items-center gap-2 text-xs text-slate-500">
        <Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
        <span>Retrieving TF-IDF chunks & verifying citations</span>
      </div>
    </motion.div>
  );
}

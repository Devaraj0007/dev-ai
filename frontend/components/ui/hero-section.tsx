"use client";

import { motion } from "framer-motion";
import { Sparkles, ShieldCheck, Database, Zap } from "lucide-react";

export function HeroSection() {
  return (
    <div className="relative overflow-hidden pt-12 pb-8 text-center">
      {/* Radial Gradient Glow background */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-pink-500/10 blur-[100px] rounded-full -z-10 pointer-events-none" />

      {/* Top Animated Pill */}
      <motion.div
        initial={{ opacity: 0, y: -15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-medium backdrop-blur-md mb-6 shadow-sm shadow-indigo-500/10"
      >
        <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
        <span>Grounded Retrieval-Augmented Generation</span>
      </motion.div>

      {/* Main Title */}
      <motion.h1
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-4"
      >
        <span className="bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          Dev AI
        </span>
      </motion.h1>

      {/* Tagline */}
      <motion.p
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="max-w-2xl mx-auto text-slate-300 text-base md:text-lg leading-relaxed mb-8 px-4"
      >
        Ask questions over your documents with guaranteed citation verification and strict grounding check against silent hallucinations.
      </motion.p>

      {/* Feature Badges */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400"
      >
        <div className="flex items-center gap-1.5 bg-slate-900/60 border border-slate-800 px-3 py-1.5 rounded-lg backdrop-blur-sm">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Citation Verification</span>
        </div>
        <div className="flex items-center gap-1.5 bg-slate-900/60 border border-slate-800 px-3 py-1.5 rounded-lg backdrop-blur-sm">
          <Database className="w-4 h-4 text-purple-400" />
          <span>TF-IDF Source Retrieval</span>
        </div>
        <div className="flex items-center gap-1.5 bg-slate-900/60 border border-slate-800 px-3 py-1.5 rounded-lg backdrop-blur-sm">
          <Zap className="w-4 h-4 text-amber-400" />
          <span>NVIDIA NIM Powered</span>
        </div>
      </motion.div>
    </div>
  );
}

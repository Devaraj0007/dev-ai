"use client";

import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface GroundingBadgeProps {
  grounded: boolean;
  className?: string;
}

export function GroundingBadge({ grounded, className }: GroundingBadgeProps) {
  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold shadow-sm border backdrop-blur-md transition-colors",
        grounded
          ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10"
          : "bg-amber-950/40 text-amber-400 border-amber-500/30 shadow-amber-500/10",
        className
      )}
    >
      {grounded ? (
        <>
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>Grounded ✓</span>
        </>
      ) : (
        <>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          <span>Ungrounded ⚠</span>
        </>
      )}
    </motion.div>
  );
}

export function SufficiencyBadge({
  sufficient,
  className,
}: {
  sufficient: boolean;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 25, delay: 0.05 }}
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border backdrop-blur-md",
        sufficient
          ? "bg-blue-950/40 text-blue-300 border-blue-500/30"
          : "bg-slate-800/60 text-slate-300 border-slate-700",
        className
      )}
    >
      <Info className="w-3.5 h-3.5 text-blue-400" />
      <span>{sufficient ? "Sources Complete" : "Partial Coverage"}</span>
    </motion.div>
  );
}

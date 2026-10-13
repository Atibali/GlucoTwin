import React from "react";
import { HelpCircle, TrendingUp, TrendingDown, Info, Zap } from "lucide-react";
import { FeatureAttribution } from "../types/twin";

interface RiskExplainerProps {
  explanations: FeatureAttribution[];
}

export const RiskExplainer: React.FC<RiskExplainerProps> = ({ explanations }) => {
  return (
    <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center space-x-2">
          <Zap className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white tracking-tight">
            Mechanistic Feature Attribution & Twin Explainability
          </h3>
        </div>
        <span className="text-[10px] uppercase font-semibold text-slate-400 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
          SHAP-Weighted Impact
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Decomposition of dynamic wearable signals and longitudinal EHR factors driving the near-term forecast:
      </p>

      <div className="space-y-3">
        {explanations.map((exp, idx) => {
          const isElevating = exp.direction === "elevates";
          // Normalize impact score to a 0-100% width bar (max score ~50)
          const barWidth = Math.min(100, Math.max(15, exp.impact_score * 2.2));

          return (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-2">
                  {isElevating ? (
                    <TrendingUp className="h-4 w-4 text-rose-400 shrink-0" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-emerald-400 shrink-0" />
                  )}
                  <span className="text-xs font-semibold text-slate-200">
                    {exp.display_name}
                  </span>
                </div>
                <span
                  className={`text-[11px] font-mono font-bold ${
                    isElevating ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {isElevating ? "+ " : "- "}
                  {exp.impact_score} pts
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-800/80 rounded-full h-1.5 mb-2 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isElevating
                      ? "bg-gradient-to-r from-amber-500 to-rose-500"
                      : "bg-gradient-to-r from-cyan-500 to-emerald-500"
                  }`}
                  style={{ width: `${barWidth}%` }}
                />
              </div>

              <div className="text-[11px] text-slate-400 leading-snug">
                {exp.clinical_explanation}
              </div>
            </div>
          );
        })}

        {explanations.length === 0 && (
          <div className="text-center py-6 text-xs text-slate-500">
            Awaiting rolling feature dynamics to generate attribution decomposition.
          </div>
        )}
      </div>
    </div>
  );
};

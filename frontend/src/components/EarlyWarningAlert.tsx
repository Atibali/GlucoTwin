import React from "react";
import { AlertTriangle, ShieldCheck, Clock, ArrowDownRight, ArrowUpRight } from "lucide-react";
import { AlertInfo } from "../types/twin";

interface EarlyWarningAlertProps {
  alert: AlertInfo;
}

export const EarlyWarningAlert: React.FC<EarlyWarningAlertProps> = ({ alert }) => {
  if (!alert.is_active) {
    return (
      <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-2xl p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-emerald-900/40 flex items-center justify-center border border-emerald-700/40 text-emerald-400">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Glycemic State: In Range
            </div>
            <div className="text-sm font-medium text-slate-200 mt-0.5">
              {alert.alert_message}
            </div>
          </div>
        </div>
        <div className="hidden sm:block text-right">
          <span className="text-xs font-mono text-emerald-400 font-semibold px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-800/40">
            Target 70–180 mg/dL
          </span>
        </div>
      </div>
    );
  }

  const isHypo = alert.excursion_type === "hypoglycemia";
  const isCritical = alert.severity === "critical";

  return (
    <div
      className={`rounded-2xl p-4 border relative overflow-hidden transition-all ${
        isHypo
          ? "bg-rose-950/30 border-rose-800/70 shadow-lg shadow-rose-950/30"
          : "bg-amber-950/30 border-amber-800/70 shadow-lg shadow-amber-950/30"
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-start space-x-3.5">
          <div
            className={`h-11 w-11 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
              isHypo
                ? "bg-rose-900/60 text-rose-300 border border-rose-700/60 animate-pulse"
                : "bg-amber-900/60 text-amber-300 border border-amber-700/60"
            }`}
          >
            {isHypo ? (
              <ArrowDownRight className="h-6 w-6 stroke-[2.5]" />
            ) : (
              <ArrowUpRight className="h-6 w-6 stroke-[2.5]" />
            )}
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <span
                className={`text-[11px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                  isHypo
                    ? "bg-rose-900 text-rose-200 border border-rose-700"
                    : "bg-amber-900 text-amber-200 border border-amber-700"
                }`}
              >
                {isCritical ? "CRITICAL ALERT" : "EARLY WARNING"}
              </span>
              <span className="text-xs font-bold text-white uppercase tracking-wide">
                Impending {isHypo ? "Hypoglycemia" : "Hyperglycemia"}
              </span>
            </div>
            <p className="text-sm text-slate-200 mt-1 font-medium leading-snug">
              {alert.alert_message}
            </p>
          </div>
        </div>

        <div className="flex sm:flex-col items-center sm:items-end justify-between shrink-0 pl-14 sm:pl-0 border-t sm:border-t-0 border-slate-800/60 pt-2 sm:pt-0">
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 font-medium">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span>Lead Time:</span>
            <span className="font-mono font-bold text-white">
              ~{alert.lead_time_minutes} min
            </span>
          </div>
          {alert.predicted_value && (
            <div className="text-xs text-slate-400 mt-1">
              Forecast:{" "}
              <span
                className={`font-mono font-bold text-sm ${
                  isHypo ? "text-rose-400" : "text-amber-400"
                }`}
              >
                {alert.predicted_value} mg/dL
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

import React from "react";
import { Activity, ShieldCheck, Cpu, Database, BarChart3 } from "lucide-react";

interface HeaderProps {
  activeTab: "twin" | "benchmark";
  setActiveTab: (tab: "twin" | "benchmark") => void;
  isConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  isConnected,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Activity className="h-6 w-6 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                GlucoTwin <span className="text-cyan-400 font-medium">India</span>
              </h1>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800/60">
                Digital Twin 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Personalized T2D Multimodal Forecasting & Early Warning Twin
            </p>
          </div>
        </div>

        {/* Status Indicators & Navigation */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <span
              className={`h-2 w-2 rounded-full ${
                isConnected
                  ? "bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400"
                  : "bg-amber-400"
              }`}
            />
            <span className="text-slate-300">
              {isConnected ? "Twin Synced (WS Live)" : "Reconnecting..."}
            </span>
          </div>

          {/* Model Status Pill */}
          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <Cpu className="h-3.5 w-3.5 text-cyan-400" />
            <span>XGBoost Fused Engine</span>
          </div>

          {/* Tabs */}
          <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800">
            <button
              onClick={() => setActiveTab("twin")}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === "twin"
                  ? "bg-cyan-500 text-slate-950 font-semibold shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Activity className="h-3.5 w-3.5" />
              <span>Live Patient Twin</span>
            </button>
            <button
              onClick={() => setActiveTab("benchmark")}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === "benchmark"
                  ? "bg-cyan-500 text-slate-950 font-semibold shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <BarChart3 className="h-3.5 w-3.5" />
              <span>Ablation & Clinical Evidence</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

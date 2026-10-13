import React, { useState } from "react";
import { Play, Pause, SkipForward, FastForward, Utensils, Footprints, PlusCircle } from "lucide-react";

interface SimulationControlsProps {
  isPlaying: boolean;
  speedMultiplier: number;
  onTogglePlay: () => void;
  onStep: () => void;
  onSetSpeed: (speed: number) => void;
  onInjectEvent: (eventType: "meal" | "exercise", carbs: number, exerciseMinutes: number, desc: string) => void;
  currentStep: number;
  totalSteps: number;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  isPlaying,
  speedMultiplier,
  onTogglePlay,
  onStep,
  onSetSpeed,
  onInjectEvent,
  currentStep,
  totalSteps,
}) => {
  const [customModalOpen, setCustomModalOpen] = useState(false);
  const [customType, setCustomType] = useState<"meal" | "exercise">("meal");
  const [customValue, setCustomValue] = useState<number>(50);
  const [customDesc, setCustomDesc] = useState<string>("Standard Meal");

  const speeds = [1, 5, 15, 30];

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customType === "meal") {
      onInjectEvent("meal", customValue, 0, customDesc);
    } else {
      onInjectEvent("exercise", 0, customValue, customDesc);
    }
    setCustomModalOpen(false);
  };

  return (
    <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-4 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Playback Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onTogglePlay}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-bold text-xs shadow-lg transition-all ${
              isPlaying
                ? "bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-amber-500/20"
                : "bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/20"
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="h-4 w-4 fill-current" />
                <span>Pause Replay</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-current" />
                <span>Start Stream</span>
              </>
            )}
          </button>

          <button
            onClick={onStep}
            disabled={isPlaying}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs text-slate-200 font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Advance 5 minutes"
          >
            <SkipForward className="h-3.5 w-3.5" />
            <span>+5m Step</span>
          </button>

          {/* Speed Pills */}
          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {speeds.map((s) => (
              <button
                key={s}
                onClick={() => onSetSpeed(s)}
                className={`px-2 py-1 text-[11px] font-semibold rounded-lg transition-all ${
                  speedMultiplier === s
                    ? "bg-cyan-500 text-slate-950"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>

          <div className="hidden lg:block text-xs text-slate-500 font-mono">
            Tick: {currentStep} / {totalSteps}
          </div>
        </div>

        {/* Dynamic Intervention Injectors */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] uppercase font-semibold text-slate-400 mr-1">
            Simulate Event:
          </span>

          <button
            onClick={() => onInjectEvent("meal", 65, 0, "High-Carb Dinner (65g)")}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-600/60 hover:bg-slate-800/80 text-xs text-amber-300 transition-all"
          >
            <Utensils className="h-3.5 w-3.5" />
            <span>Eat Meal (65g)</span>
          </button>

          <button
            onClick={() => onInjectEvent("exercise", 0, 30, "Brisk Walk (30m)")}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-600/60 hover:bg-slate-800/80 text-xs text-emerald-300 transition-all"
          >
            <Footprints className="h-3.5 w-3.5" />
            <span>Walk (30 min)</span>
          </button>

          <button
            onClick={() => setCustomModalOpen(true)}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500 text-xs text-slate-300 transition-all"
            title="Custom Intervention"
          >
            <PlusCircle className="h-3.5 w-3.5 text-cyan-400" />
            <span>Custom</span>
          </button>
        </div>
      </div>

      {/* Custom Modal */}
      {customModalOpen && (
        <div className="mt-3 pt-3 border-t border-slate-800 flex flex-wrap items-center gap-3">
          <select
            value={customType}
            onChange={(e) => {
              setCustomType(e.target.value as any);
              setCustomValue(e.target.value === "meal" ? 45 : 30);
              setCustomDesc(e.target.value === "meal" ? "Custom Meal" : "Workout");
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-white"
          >
            <option value="meal">Carbohydrate Meal (grams)</option>
            <option value="exercise">Physical Exercise (minutes)</option>
          </select>

          <input
            type="number"
            value={customValue}
            onChange={(e) => setCustomValue(Number(e.target.value))}
            className="w-20 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-white font-mono"
            min={1}
            max={200}
          />

          <input
            type="text"
            value={customDesc}
            onChange={(e) => setCustomDesc(e.target.value)}
            placeholder="Event notes..."
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-white"
          />

          <button
            onClick={handleCustomSubmit}
            className="px-3 py-1 bg-cyan-500 text-slate-950 font-bold rounded-lg text-xs"
          >
            Inject Into Twin
          </button>

          <button
            onClick={() => setCustomModalOpen(false)}
            className="px-2.5 py-1 bg-slate-800 text-slate-400 rounded-lg text-xs hover:text-white"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};

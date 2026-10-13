import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from "recharts";
import { Activity, TrendingUp, TrendingDown, Clock, ShieldCheck, Zap } from "lucide-react";
import { DigitalTwinState, StreamReading, ForecastPoint } from "../types/twin";

interface CGMForecastChartProps {
  twinState: DigitalTwinState;
  history: StreamReading[];
}

export const CGMForecastChart: React.FC<CGMForecastChartProps> = ({
  twinState,
  history,
}) => {
  // Build combined chart series: Historical Readings + Future Forecast Projections
  const chartData: any[] = [];

  // 1. Add historical points
  history.forEach((h, idx) => {
    const timeStr = new Date(h.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    chartData.push({
      time: timeStr,
      rawTime: h.timestamp,
      glucose: h.glucose,
      carbs: h.carbs > 0 ? h.carbs : undefined,
      exercise: h.exercise_minutes > 0 ? h.exercise_minutes : undefined,
      isForecast: false,
    });
  });

  // Current reading time
  const currentTime = new Date(twinState.timestamp);

  // Connect forecast with the last historical point
  if (chartData.length > 0) {
    chartData[chartData.length - 1].forecastPoint = twinState.current_glucose;
    chartData[chartData.length - 1].lowerBand = twinState.current_glucose;
    chartData[chartData.length - 1].upperBand = twinState.current_glucose;
    chartData[chartData.length - 1].bandRange = [twinState.current_glucose, twinState.current_glucose];
  }

  // 2. Add future forecast points (30m, 60m, 120m)
  twinState.forecasts.forEach((f) => {
    const futureDate = new Date(currentTime.getTime() + f.horizon_minutes * 60 * 1000);
    const timeStr = futureDate.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    chartData.push({
      time: timeStr,
      rawTime: futureDate.toISOString(),
      forecastPoint: f.predicted_glucose,
      lowerBand: f.lower_bound,
      upperBand: f.upper_bound,
      bandRange: [f.lower_bound, f.upper_bound],
      isForecast: true,
      horizon: f.horizon_minutes,
    });
  });

  const pred30 = twinState.forecasts.find((f) => f.horizon_minutes === 30);
  const pred60 = twinState.forecasts.find((f) => f.horizon_minutes === 60);
  const pred120 = twinState.forecasts.find((f) => f.horizon_minutes === 120);

  const isCurrentHypo = twinState.current_glucose < 70;
  const isCurrentHyper = twinState.current_glucose > 180;

  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col justify-between">
      {/* Top Bar: Current Glucose & Multi-Horizon Projections */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80 mb-4">
        {/* Current State */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div
              className={`h-12 w-12 rounded-2xl flex items-center justify-center font-black text-xl shadow-lg ${
                isCurrentHypo
                  ? "bg-rose-500 text-slate-950 shadow-rose-500/30"
                  : isCurrentHyper
                  ? "bg-amber-500 text-slate-950 shadow-amber-500/30"
                  : "bg-cyan-500 text-slate-950 shadow-cyan-500/30"
              }`}
            >
              {twinState.direction}
            </div>
            <span className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-400 border-2 border-slate-950 animate-ping" />
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                Current Sensor Reading
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-900 text-cyan-400">
                {twinState.rate_of_change > 0 ? `+${twinState.rate_of_change}` : twinState.rate_of_change} mg/dL/min
              </span>
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-black text-white tracking-tight">
                {twinState.current_glucose}
              </span>
              <span className="text-xs font-semibold text-slate-400">mg/dL</span>
            </div>
          </div>
        </div>

        {/* Forecast Horizon Cards */}
        <div className="flex flex-wrap items-center gap-2">
          {pred30 && (
            <div className="px-3.5 py-2 rounded-xl bg-slate-900/90 border border-cyan-500/50 shadow-md shadow-cyan-950/40">
              <div className="text-[10px] uppercase font-bold text-cyan-400 flex items-center gap-1">
                <Clock className="h-2.5 w-2.5" />
                <span>+30 min Target</span>
              </div>
              <div className="text-base font-extrabold text-white mt-0.5">
                {pred30.predicted_glucose}{" "}
                <span className="text-[10px] font-normal text-slate-400">mg/dL</span>
              </div>
              <div className="text-[9px] font-mono text-slate-400 mt-0.5">
                CI: [{pred30.lower_bound} – {pred30.upper_bound}]
              </div>
            </div>
          )}

          {pred60 && (
            <div className="px-3.5 py-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] uppercase font-semibold text-slate-400 flex items-center gap-1">
                <Clock className="h-2.5 w-2.5" />
                <span>+60 min Horizon</span>
              </div>
              <div className="text-base font-bold text-slate-200 mt-0.5">
                {pred60.predicted_glucose}{" "}
                <span className="text-[10px] font-normal text-slate-500">mg/dL</span>
              </div>
              <div className="text-[9px] font-mono text-slate-500 mt-0.5">
                CI: [{pred60.lower_bound} – {pred60.upper_bound}]
              </div>
            </div>
          )}

          {pred120 && (
            <div className="px-3.5 py-2 rounded-xl bg-slate-900/60 border border-slate-800 hidden sm:block">
              <div className="text-[10px] uppercase font-semibold text-slate-400 flex items-center gap-1">
                <Clock className="h-2.5 w-2.5" />
                <span>+120 min Horizon</span>
              </div>
              <div className="text-base font-bold text-slate-200 mt-0.5">
                {pred120.predicted_glucose}{" "}
                <span className="text-[10px] font-normal text-slate-500">mg/dL</span>
              </div>
              <div className="text-[9px] font-mono text-slate-500 mt-0.5">
                CI: [{pred120.lower_bound} – {pred120.upper_bound}]
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main High-Resolution Chart */}
      <div className="h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 15, left: -20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1e293b"
              vertical={false}
            />

            <XAxis
              dataKey="time"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              domain={[40, 280]}
              ticks={[50, 70, 100, 140, 180, 220, 260]}
            />

            {/* Clinical Target Range Thresholds */}
            <ReferenceLine
              y={180}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: "Hyper Limit (180 mg/dL)",
                fill: "#f59e0b",
                fontSize: 9,
                position: "insideTopRight",
              }}
            />
            <ReferenceLine
              y={70}
              stroke="#f43f5e"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: "Hypo Limit (70 mg/dL)",
                fill: "#f43f5e",
                fontSize: 9,
                position: "insideBottomRight",
              }}
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                const d = payload[0].payload;
                return (
                  <div className="bg-slate-900/95 border border-slate-700/80 rounded-xl p-3 shadow-2xl backdrop-blur text-xs">
                    <div className="font-mono text-slate-400 mb-1.5 flex items-center justify-between gap-4">
                      <span>{label}</span>
                      {d.isForecast && (
                        <span className="text-[10px] font-bold text-cyan-400 uppercase px-1.5 py-0.2 rounded bg-cyan-950">
                          Forecast +{d.horizon}m
                        </span>
                      )}
                    </div>
                    {d.glucose !== undefined && (
                      <div className="text-white font-bold text-sm">
                        CGM Glucose:{" "}
                        <span className="text-cyan-400 font-mono">
                          {d.glucose} mg/dL
                        </span>
                      </div>
                    )}
                    {d.forecastPoint !== undefined && (
                      <div>
                        <div className="text-amber-300 font-bold text-sm">
                          Predicted:{" "}
                          <span className="font-mono">{d.forecastPoint} mg/dL</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                          80% Interval: [{d.lowerBand} – {d.upperBand}]
                        </div>
                      </div>
                    )}
                    {d.carbs && (
                      <div className="mt-1 text-[11px] text-amber-400 font-medium">
                        🍞 Meal Ingestion: {d.carbs}g carbs
                      </div>
                    )}
                    {d.exercise && (
                      <div className="mt-1 text-[11px] text-emerald-400 font-medium">
                        🏃 Physical Activity: {d.exercise} min
                      </div>
                    )}
                  </div>
                );
              }}
            />

            {/* Uncertainty Envelope Band (80% Conformal Range) */}
            <Area
              type="monotone"
              dataKey="bandRange"
              stroke="none"
              fill="#06b6d4"
              fillOpacity={0.15}
            />

            {/* Historical CGM Trace */}
            <Line
              type="monotone"
              dataKey="glucose"
              stroke="#22d3ee"
              strokeWidth={2.5}
              dot={{ r: 2, fill: "#22d3ee" }}
              activeDot={{ r: 5, fill: "#38bdf8" }}
              isAnimationActive={false}
            />

            {/* Forecast Projection Trace */}
            <Line
              type="monotone"
              dataKey="forecastPoint"
              stroke="#f59e0b"
              strokeWidth={2.5}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: "#f59e0b" }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Chart Legend & Indicators */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80 mt-2 text-[11px] text-slate-400">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="h-2.5 w-5 bg-cyan-400 rounded-sm inline-block" />
            <span>CGM Sensor Stream</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="h-0.5 w-5 border-t-2 border-dashed border-amber-400 inline-block" />
            <span>Personalized Forecast (+30/60/120m)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="h-3 w-4 bg-cyan-500/20 rounded-sm inline-block" />
            <span>80% Uncertainty Band</span>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-slate-500 font-mono">
          <span>Target: 70–180 mg/dL</span>
          <span>•</span>
          <span>Rolling 2h Mean: {twinState.rolling_2h_mean} mg/dL</span>
        </div>
      </div>
    </div>
  );
};

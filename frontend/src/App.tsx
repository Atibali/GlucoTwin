import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { ClinicalDisclaimer } from "./components/ClinicalDisclaimer";
import { PatientSelector } from "./components/PatientSelector";
import { PatientProfileCard } from "./components/PatientProfileCard";
import { CGMForecastChart } from "./components/CGMForecastChart";
import { EarlyWarningAlert } from "./components/EarlyWarningAlert";
import { RiskExplainer } from "./components/RiskExplainer";
import { SimulationControls } from "./components/SimulationControls";
import { AblationBenchmark } from "./components/AblationBenchmark";
import {
  fetchPatients,
  fetchBenchmarkReport,
  useTwinWebSocket,
  injectIntervention,
  stepSimulation,
  controlSimulation,
} from "./services/api";
import { PatientProfile, BenchmarkReport, SimulationPayload } from "./types/twin";
import { Activity, ShieldAlert, Cpu, HeartPulse, RefreshCw } from "lucide-react";

export function App() {
  const [activeTab, setActiveTab] = useState<"twin" | "benchmark">("twin");
  const [patients, setPatients] = useState<PatientProfile[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>("PT-101");
  const [benchmarkReport, setBenchmarkReport] = useState<BenchmarkReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [fallbackData, setFallbackData] = useState<SimulationPayload | null>(null);

  // WebSocket Live Stream
  const { data: wsData, isConnected, sendCommand } = useTwinWebSocket(selectedPatientId);

  // Active stream payload (WS prioritized, fallback to REST step)
  const currentPayload: SimulationPayload | null = wsData || fallbackData;

  // Initial data loading
  useEffect(() => {
    async function initData() {
      try {
        setLoading(true);
        const [patientsData, reportData] = await Promise.all([
          fetchPatients(),
          fetchBenchmarkReport(),
        ]);
        setPatients(patientsData);
        setBenchmarkReport(reportData);
        if (patientsData.length > 0) {
          setSelectedPatientId(patientsData[0].patient_id);
          // Initial REST step for fast render
          const initialStep = await stepSimulation(patientsData[0].patient_id);
          setFallbackData(initialStep);
        }
      } catch (err) {
        console.error("Initialization error:", err);
      } finally {
        setLoading(false);
      }
    }
    initData();
  }, []);

  // When patient selection changes
  const handleSelectPatient = async (patientId: string) => {
    setSelectedPatientId(patientId);
    try {
      const step = await stepSimulation(patientId);
      setFallbackData(step);
    } catch (e) {
      console.error(e);
    }
  };

  // Play / Pause toggle
  const handleTogglePlay = () => {
    if (!currentPayload) return;
    const nextState = !currentPayload.is_playing;
    sendCommand({ action: nextState ? "play" : "pause" });
  };

  // Single 5-min step
  const handleStep = async () => {
    if (isConnected) {
      sendCommand({ action: "step" });
    } else {
      const step = await stepSimulation(selectedPatientId);
      setFallbackData(step);
    }
  };

  // Change replay speed
  const handleSetSpeed = (speed: number) => {
    sendCommand({ action: "speed", speed });
  };

  // Inject meal or workout
  const handleInjectEvent = async (
    eventType: "meal" | "exercise",
    carbs: number,
    exerciseMinutes: number,
    description: string
  ) => {
    if (isConnected) {
      sendCommand({
        action: "inject",
        event_type: eventType,
        carbs,
        exercise_minutes: exerciseMinutes,
        description,
      });
    } else {
      await injectIntervention(selectedPatientId, eventType, carbs, exerciseMinutes, description);
      const step = await stepSimulation(selectedPatientId);
      setFallbackData(step);
    }
  };

  const selectedPatient = patients.find((p) => p.patient_id === selectedPatientId);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isConnected={isConnected}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        <ClinicalDisclaimer />

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 space-y-4 text-slate-400">
            <RefreshCw className="h-8 w-8 text-cyan-400 animate-spin" />
            <p className="text-sm font-medium">
              Initializing GlucoTwin Multimodal Engine & Loading Patient Archetypes...
            </p>
          </div>
        ) : (
          <>
            {activeTab === "twin" ? (
              <div className="space-y-6">
                {/* Patient Archetype Selector */}
                <PatientSelector
                  patients={patients}
                  selectedPatientId={selectedPatientId}
                  onSelectPatient={handleSelectPatient}
                />

                {/* Early Warning Excursion Banner */}
                {currentPayload && (
                  <EarlyWarningAlert alert={currentPayload.twin_state.active_alert} />
                )}

                {/* Main Two-Column Twin Dashboard Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left 2 Cols: CGM Chart, Controls, Profile */}
                  <div className="lg:col-span-2 space-y-6">
                    {currentPayload && (
                      <CGMForecastChart
                        twinState={currentPayload.twin_state}
                        history={currentPayload.recent_history}
                      />
                    )}

                    {currentPayload && (
                      <SimulationControls
                        isPlaying={currentPayload.is_playing}
                        speedMultiplier={currentPayload.speed_multiplier}
                        onTogglePlay={handleTogglePlay}
                        onStep={handleStep}
                        onSetSpeed={handleSetSpeed}
                        onInjectEvent={handleInjectEvent}
                        currentStep={currentPayload.step_index}
                        totalSteps={currentPayload.total_steps}
                      />
                    )}

                    {selectedPatient && (
                      <PatientProfileCard
                        patient={selectedPatient}
                        timeInRange={currentPayload?.twin_state.time_in_range_percent}
                      />
                    )}
                  </div>

                  {/* Right 1 Col: Explainability & State Telemetry */}
                  <div className="space-y-6">
                    {currentPayload && (
                      <RiskExplainer
                        explanations={currentPayload.twin_state.top_explanations}
                      />
                    )}

                    {/* Twin State Telemetry Card */}
                    {currentPayload && (
                      <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-5 shadow-xl">
                        <div className="flex items-center space-x-2 pb-3 border-b border-slate-800/80 mb-3">
                          <Cpu className="h-4 w-4 text-cyan-400" />
                          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                            Digital Twin State Engine Telemetry
                          </h3>
                        </div>

                        <div className="space-y-2.5 text-xs">
                          <div className="flex justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <span className="text-slate-400">Sampling Rate:</span>
                            <span className="font-mono text-cyan-400 font-semibold">
                              5 minutes (CGM standard)
                            </span>
                          </div>

                          <div className="flex justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <span className="text-slate-400">Rolling Buffer Depth:</span>
                            <span className="font-mono text-white font-semibold">
                              24 steps (120 minutes)
                            </span>
                          </div>

                          <div className="flex justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <span className="text-slate-400">Rolling 2h Std Dev:</span>
                            <span className="font-mono text-white font-semibold">
                              {currentPayload.twin_state.rolling_2h_std} mg/dL
                            </span>
                          </div>

                          <div className="flex justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <span className="text-slate-400">Active Gut Carbs (2h):</span>
                            <span className="font-mono text-amber-400 font-semibold">
                              {currentPayload.twin_state.total_carbs_last_2h} g
                            </span>
                          </div>

                          <div className="flex justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <span className="text-slate-400">Active Exercise (2h):</span>
                            <span className="font-mono text-emerald-400 font-semibold">
                              {currentPayload.twin_state.total_exercise_last_2h} min
                            </span>
                          </div>

                          <div className="flex justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <span className="text-slate-400">Personalization Model:</span>
                            <span className="font-mono text-slate-200 font-semibold">
                              XGBoost + Dynamic Basal Delta
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              /* Tab 2: Ablation Benchmark & Clinical Evidence */
              benchmarkReport && <AblationBenchmark report={benchmarkReport} />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <p>
          GlucoTwin India • Digital Twin Challenge 2026 • Personalized Type 2 Diabetes Forecasting Prototype
        </p>
      </footer>
    </div>
  );
}

export default App;

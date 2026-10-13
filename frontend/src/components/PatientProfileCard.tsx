import React from "react";
import { User, FileText, Pill, HeartPulse, Scale, Clock, ShieldCheck } from "lucide-react";
import { PatientProfile } from "../types/twin";

interface PatientProfileCardProps {
  patient: PatientProfile;
  timeInRange?: number;
}

export const PatientProfileCard: React.FC<PatientProfileCardProps> = ({
  patient,
  timeInRange = 82,
}) => {
  return (
    <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between mb-4 pb-3 border-b border-slate-800/80">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white tracking-tight">
                {patient.name}
              </h2>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">
                {patient.patient_id}
              </span>
            </div>
            <p className="text-xs text-cyan-400 font-medium mt-0.5">
              {patient.archetype_title}
            </p>
          </div>
          <div className="text-right">
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              HbA1c Baseline
            </div>
            <div
              className={`text-lg font-black ${
                patient.hba1c >= 8.5
                  ? "text-rose-400"
                  : patient.hba1c >= 7.0
                  ? "text-amber-400"
                  : "text-emerald-400"
              }`}
            >
              {patient.hba1c}%
            </div>
          </div>
        </div>

        {/* Clinical EHR Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
            <div className="flex items-center space-x-1.5 text-slate-400 text-[10px] uppercase tracking-wider font-semibold">
              <User className="h-3 w-3 text-cyan-400" />
              <span>Demographics</span>
            </div>
            <div className="text-sm font-bold text-white mt-1">
              {patient.age}y / {patient.gender}
            </div>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
            <div className="flex items-center space-x-1.5 text-slate-400 text-[10px] uppercase tracking-wider font-semibold">
              <Scale className="h-3 w-3 text-cyan-400" />
              <span>BMI</span>
            </div>
            <div className="text-sm font-bold text-white mt-1">
              {patient.bmi} <span className="text-[10px] font-normal text-slate-400">kg/m²</span>
            </div>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
            <div className="flex items-center space-x-1.5 text-slate-400 text-[10px] uppercase tracking-wider font-semibold">
              <Clock className="h-3 w-3 text-cyan-400" />
              <span>T2D Duration</span>
            </div>
            <div className="text-sm font-bold text-white mt-1">
              {patient.duration_years} <span className="text-[10px] font-normal text-slate-400">years</span>
            </div>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
            <div className="flex items-center space-x-1.5 text-slate-400 text-[10px] uppercase tracking-wider font-semibold">
              <HeartPulse className="h-3 w-3 text-emerald-400" />
              <span>Est. TIR (24h)</span>
            </div>
            <div className="text-sm font-bold text-emerald-400 mt-1">
              {timeInRange}%
            </div>
          </div>
        </div>

        {/* Active Medications */}
        <div className="mb-4">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[10px] uppercase tracking-wider font-semibold mb-2">
            <Pill className="h-3 w-3 text-cyan-400" />
            <span>Active Pharmacotherapy (Synthea EHR)</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {patient.medications.map((m, idx) => (
              <div
                key={idx}
                className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-1.5 text-xs"
              >
                <span className="font-medium text-slate-200">{m.name}</span>
                <span className="text-[10px] text-cyan-400/80 font-mono">({m.dose})</span>
                <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                  {m.class_name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Clinical EHR Insight */}
      <div className="bg-slate-900/80 border border-slate-800/60 rounded-xl p-3 text-xs text-slate-300 flex items-start space-x-2">
        <FileText className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-cyan-300">Clinician Twin Note:</span>{" "}
          {patient.clinical_notes}
        </div>
      </div>
    </div>
  );
};

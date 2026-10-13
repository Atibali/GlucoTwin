import React from "react";
import { User, Activity, AlertTriangle } from "lucide-react";
import { PatientProfile } from "../types/twin";

interface PatientSelectorProps {
  patients: PatientProfile[];
  selectedPatientId: string;
  onSelectPatient: (patientId: string) => void;
}

export const PatientSelector: React.FC<PatientSelectorProps> = ({
  patients,
  selectedPatientId,
  onSelectPatient,
}) => {
  return (
    <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <User className="h-4 w-4 text-cyan-400" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Select Patient Archetype ({patients.length})
          </h2>
        </div>
        <span className="text-[11px] text-slate-500">
          Synthetic EHR + CGM Stream Fused
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        {patients.map((p) => {
          const isSelected = p.patient_id === selectedPatientId;
          const isHighHba1c = p.hba1c >= 8.5;

          return (
            <button
              key={p.patient_id}
              onClick={() => onSelectPatient(p.patient_id)}
              className={`text-left p-2.5 rounded-xl border transition-all relative overflow-hidden flex flex-col justify-between ${
                isSelected
                  ? "bg-slate-800/90 border-cyan-500 shadow-md shadow-cyan-950/50 ring-1 ring-cyan-500"
                  : "bg-slate-900/40 border-slate-800/80 hover:bg-slate-800/40 hover:border-slate-700"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    {p.patient_id}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      isHighHba1c
                        ? "bg-rose-950 text-rose-300 border border-rose-800/50"
                        : "bg-emerald-950 text-emerald-300 border border-emerald-800/50"
                    }`}
                  >
                    A1c {p.hba1c}%
                  </span>
                </div>
                <div className="text-xs font-semibold text-white truncate">
                  {p.name}
                </div>
              </div>

              <div className="mt-2 text-[10px] text-slate-400 line-clamp-1">
                {p.archetype_title}
              </div>

              {isSelected && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-emerald-400" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

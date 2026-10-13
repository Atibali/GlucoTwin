import React from "react";
import { AlertCircle, ShieldAlert } from "lucide-react";

export const ClinicalDisclaimer: React.FC = () => {
  return (
    <div className="bg-amber-950/30 border border-amber-900/60 rounded-xl px-4 py-2.5 flex items-start space-x-3 text-xs text-amber-200/90 mb-6">
      <ShieldAlert className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-amber-300">
          Digital Twin Research & Clinical Decision-Support Prototype:
        </span>{" "}
        This system forecasts blood glucose trends and highlights potential excursion risks to assist clinicians and patients. It does{" "}
        <span className="font-semibold underline">not</span> calculate insulin boluses, alter medication doses, or function as an autonomous closed-loop medical device.
      </div>
    </div>
  );
};

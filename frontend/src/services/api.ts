import { useState, useEffect, useRef, useCallback } from "react";
import {
  PatientProfile,
  BenchmarkReport,
  SimulationPayload,
} from "../types/twin";

const API_BASE = "/api";

export async function fetchPatients(): Promise<PatientProfile[]> {
  const res = await fetch(`${API_BASE}/patients`);
  if (!res.ok) throw new Error("Failed to fetch patients cohort");
  return res.json();
}

export async function fetchPatient(id: string): Promise<PatientProfile> {
  const res = await fetch(`${API_BASE}/patients/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch patient ${id}`);
  return res.json();
}

export async function fetchBenchmarkReport(): Promise<BenchmarkReport> {
  const res = await fetch(`${API_BASE}/ablation/results`);
  if (!res.ok) throw new Error("Failed to fetch benchmark report");
  return res.json();
}

export async function stepSimulation(patientId: string): Promise<SimulationPayload> {
  const res = await fetch(`${API_BASE}/forecast/${patientId}/step`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to step simulation");
  return res.json();
}

export async function injectIntervention(
  patientId: string,
  eventType: "meal" | "exercise",
  carbs: number = 0,
  exerciseMinutes: number = 0,
  description: string = ""
): Promise<any> {
  const res = await fetch(`${API_BASE}/forecast/inject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      patient_id: patientId,
      event_type: eventType,
      carbs,
      exercise_minutes: exerciseMinutes,
      description,
    }),
  });
  if (!res.ok) throw new Error("Failed to inject event");
  return res.json();
}

export async function controlSimulation(
  patientId: string,
  action: "play" | "pause" | "speed",
  speed: number = 5
): Promise<any> {
  const res = await fetch(`${API_BASE}/forecast/${patientId}/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, speed }),
  });
  if (!res.ok) throw new Error("Failed to update simulation control");
  return res.json();
}

/**
 * WebSocket Hook for continuous live streaming and remote control
 */
export function useTwinWebSocket(patientId: string) {
  const [data, setData] = useState<SimulationPayload | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!patientId) return;

    // Use ws:// with current window host
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/ws/stream/${patientId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const payload: SimulationPayload = JSON.parse(event.data);
        setData(payload);
      } catch (err) {
        console.error("Failed to parse WS message", err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = () => {
      setIsConnected(false);
    };
  }, [patientId]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendCommand = useCallback((cmd: Record<string, any>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(cmd));
    }
  }, []);

  return {
    data,
    isConnected,
    sendCommand,
  };
}

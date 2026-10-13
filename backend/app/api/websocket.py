"""WebSocket streaming endpoint for real-time CGM replay and interactive interventions."""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..engine.simulator_stream import get_or_create_simulation
from ..schemas.schemas import InjectIntervention

router = APIRouter(prefix="/ws", tags=["WebSocket Stream"])


@router.websocket("/stream/{patient_id}")
async def websocket_cgm_stream(websocket: WebSocket, patient_id: str):
    """Real-time bi-directional streaming endpoint for patient digital twin."""
    await websocket.accept()
    sim = get_or_create_simulation(patient_id)
    
    # Send initial state immediately
    initial_payload = sim.step()
    await websocket.send_text(json.dumps(initial_payload))
    
    async def listen_for_commands():
        """Listen for incoming user controls (play, pause, step, speed, inject)."""
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                
                if action == "play":
                    sim.set_playing(True)
                elif action == "pause":
                    sim.set_playing(False)
                elif action == "step":
                    step_data = sim.step()
                    await websocket.send_text(json.dumps(step_data))
                elif action == "speed":
                    sim.set_speed(float(msg.get("speed", 5.0)))
                elif action == "inject":
                    intervention = InjectIntervention(
                        patient_id=patient_id,
                        event_type=msg.get("event_type", "meal"),
                        carbs=float(msg.get("carbs", 0.0)),
                        exercise_minutes=float(msg.get("exercise_minutes", 0.0)),
                        description=msg.get("description", "")
                    )
                    sim.inject_event(intervention)
                    # Immediate step after injection
                    step_data = sim.step()
                    await websocket.send_text(json.dumps(step_data))
            except Exception as e:
                pass

    listener_task = asyncio.create_task(listen_for_commands())
    
    try:
        while True:
            if sim.is_playing:
                # Interval scaled by speed multiplier
                # e.g., 5x speed -> 0.4s per 5m step; 10x speed -> 0.2s per 5m step
                delay = max(0.08, 2.0 / sim.speed_multiplier)
                await asyncio.sleep(delay)
                step_data = sim.step()
                await websocket.send_text(json.dumps(step_data))
            else:
                await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        listener_task.cancel()
    except Exception:
        listener_task.cancel()

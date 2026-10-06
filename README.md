# EmergencyMesh

A working academic prototype of a Universal Emergency Mesh & Evacuation System. It follows the supplied architecture: sensors → ESP32/LoRa mesh → gateway/backend → real-time web app → nearby alerts + hazard-aware evacuation support. The source specification calls for this flow, offline behavior, duplicate prevention, TTL, demo mode, history, admin tools and a 5-node simulation. fileciteturn0file0L46-L64

> **Safety:** EmergencyMesh is a prototype emergency communication and evacuation-support system. Always follow official emergency services and local authority instructions. It does not guarantee safety.

## Stack
- Frontend: React + Vite + Tailwind CSS + Leaflet/OpenStreetMap
- Backend: FastAPI + SQLAlchemy + SQLite + WebSockets
- Hardware: Arduino UNO sensor controller + ESP32 + LoRa
- Demo fallback: Python 5-node mesh simulator
- Routing fallback: local hazard-aware graph; no API key required
- Notifications: browser Notification API + in-app alert feed

## Project tree
```text
EmergencyMesh/
├── backend/
│   ├── app/main.py
│   ├── app/database.py
│   ├── app/models.py
│   ├── app/schemas.py
│   ├── app/routes/api.py
│   ├── app/services/priority.py
│   ├── app/services/mesh.py
│   ├── app/services/routing.py
│   └── requirements.txt
├── frontend/
│   ├── src/components/
│   ├── src/pages/
│   ├── src/services/
│   ├── src/notifications/
│   └── package.json
├── hardware/
├── mesh_simulator/
├── tests/
└── README.md
```

## 1. Start backend
From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cd ..
python -m backend.seed
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## 2. Start frontend
Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## 3. Demo flow
1. Open Dashboard.
2. Click **🔥 Fire**.
3. The frontend calls `POST /api/emergency`.
4. Backend classifies flame as CRITICAL, stores the event in SQLite, and broadcasts it over WebSocket.
5. The dashboard updates without refresh and requests a hazard-aware route.
6. A browser notification is attempted after permission is granted.
7. The fire zone appears on the Leaflet map; the route engine heavily penalizes fire/flood zones.
8. Open **Mesh Network** to see nodes and hop information.
9. Open **History** to see the persisted event.
10. Click **Clear emergency** to deactivate active alerts.

The supplied demo requirements specifically call for Fire, Smoke, Flood Warning, High Priority and Clear actions and for each demo alert to update the map, notifications, route, mesh and history. fileciteturn0file0L669-L697

## 4. Five-node mesh simulation
With the backend running:

```bash
cd mesh_simulator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python mesh_simulator.py --hazard FIRE
```

Expected logical path:

```text
NODE-A → NODE-B → NODE-C → NODE-D → GATEWAY
```

The simulator sends the same `message_id` through multiple hops. The backend keeps a received-message cache and rejects duplicate forwarding; TTL is decremented at each mesh hop.

## 5. Hardware integration
The supplied sensor pinout is preserved: Smoke D8, Sound D9, Rain D10, Flame D11, Buzzer D12, Red D7, Blue D6, Green D5. The source logic is Flame/Smoke → CRITICAL, Rain+Sound → HIGH, Rain or Sound → WARNING, otherwise NORMAL. fileciteturn0file0L19-L40

Upload `hardware/arduino_uno/emergency_sensor.ino` to the UNO. It emits sensor state over Serial.

Then use `hardware/esp32_lora/esp32_lora_gateway.ino` on the ESP32 with a compatible LoRa module. **Change the LoRa frequency and pin mapping for your exact board/module and local regulatory requirements.** Do not connect a 5V UNO UART directly to ESP32 GPIO; use appropriate level shifting.

A production gateway should parse the ESP32 JSON and POST it to:

```text
POST http://localhost:8000/api/mesh/message
```

Example payload:

```json
{
  "message_id":"NODE-01-12345",
  "node_id":"NODE-01",
  "hazard":"FIRE",
  "severity":"CRITICAL",
  "smoke":0,
  "sound":0,
  "rain":0,
  "flame":1,
  "latitude":17.385,
  "longitude":78.4867,
  "ttl":5,
  "hops":0
}
```

## 6. Offline mode
The web app detects browser connectivity changes and caches the latest emergencies, nodes and shelters in `localStorage`. When internet is unavailable it shows **Internet Offline / Mesh Active** and continues displaying the cached state. The local mesh itself does not depend on internet; the gateway can synchronize to the backend when connectivity returns. This matches the supplied offline requirement. fileciteturn0file0L407-L431

For a real field deployment, a native/mobile client or local gateway should be used to receive LoRa data directly when the public internet is down; a browser cannot directly listen to LoRa radio hardware.

## 7. API endpoints
- `POST /api/emergency` — create/ingest emergency
- `POST /api/mesh/message` — receive/forward a mesh message with TTL and hop count
- `GET /api/emergencies` — history/active alerts
- `GET /api/emergencies/nearby?latitude=...&longitude=...&radius_m=...`
- `POST /api/emergencies/clear` — clear active demo emergencies
- `POST /api/nodes` / `GET /api/nodes`
- `GET /api/evacuation-route?latitude=...&longitude=...`
- `GET /api/shelters`
- `GET /api/safe-zones`
- `GET /api/system/status`
- `POST /api/admin/login`
- `POST /api/admin/shelters`
- WebSocket: `ws://localhost:8000/ws`

## 8. Admin
Prototype login:

```text
username: admin
password: emergencymesh
```

Admin can add shelters. Node registration and alert testing are API-driven. Replace this demo credential system with proper authentication before any real deployment.

## 9. Routing model
The local fallback route graph uses a small deterministic road-like graph around Hyderabad. It computes a cost based on distance plus hazard penalties. Fire and flood are effectively blocked, smoke has a high penalty, and emergency sound has a smaller penalty. The selected path therefore does not simply choose the shortest distance.

For production, replace `backend/app/services/routing.py` with an OSM-compatible routing backend such as OSRM/GraphHopper or a local road graph, and feed road closures/hazard polygons into the edge costs. The supplied specification explicitly allows a local simulated routing algorithm as the prototype fallback. fileciteturn0file0L276-L340

## 10. Tests
From the root:

```bash
python3 -m pytest -q
```

Tests cover priority classification, duplicate/TTL handling and route generation. The architecture is ready for additional integration tests for gateway failure, notification radius and offline synchronization.

## 11. Production hardening
Before real-world use, add authenticated device provisioning, signed/encrypted LoRa payloads, replay protection, persistent queueing at every node, GPS validation, battery telemetry, robust routing/road-closure data, native push notifications, observability, redundancy, and formal emergency-service validation. Never treat the prototype route as an authoritative evacuation instruction.

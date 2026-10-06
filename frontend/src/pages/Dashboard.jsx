const [route, setRoute] = useState([]);
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CloudRain,
  Flame,
  Radio,
  ShieldCheck,
  Volume2,
} from "lucide-react";

import MapView from "../components/MapView";
import StatCard from "../components/StatCard";
import { api } from "../services/api";

const DEMOS = {
  FIRE: {
    hazard: "FIRE",
    severity: "CRITICAL",
    flame: 1,
    smoke: 0,
    rain: 0,
    sound: 0,
    details: "Fire detected by flame sensor",
    latitude: 17.395,
    longitude: 78.489,
  },

  SMOKE: {
    hazard: "SMOKE",
    severity: "CRITICAL",
    flame: 0,
    smoke: 1,
    rain: 0,
    sound: 0,
    details: "Smoke detected by smoke sensor",
    latitude: 17.391,
    longitude: 78.489,
  },

  FLOOD: {
    hazard: "FLOOD_WARNING",
    severity: "HIGH",
    flame: 0,
    smoke: 0,
    rain: 1,
    sound: 1,
    details: "Flood warning: heavy rain and emergency sound detected",
    latitude: 17.399,
    longitude: 78.490,
  },

  HIGH: {
    hazard: "EMERGENCY_SOUND",
    severity: "WARNING",
    flame: 0,
    smoke: 0,
    rain: 0,
    sound: 1,
    details: "Emergency sound detected",
    latitude: 17.393,
    longitude: 78.486,
  },
};

export default function Dashboard() {
  const [emergencies, setEmergencies] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [shelters, setShelters] = useState([]);
  const [route, setRoute] = useState([]);
  const [network, setNetwork] = useState("ONLINE");
  const [busy, setBusy] = useState(false);

  // Load normal backend data
  useEffect(() => {
    async function load() {
      try {
        const [e, n, s, st] = await Promise.all([
          api.get("/api/emergencies?active=true"),
          api.get("/api/nodes"),
          api.get("/api/shelters"),
          api.get("/api/system/status"),
        ]);

        if (Array.isArray(e.data)) {
          setEmergencies(e.data);
        }

        if (Array.isArray(n.data)) {
          setNodes(n.data);
        }

        if (Array.isArray(s.data)) {
          setShelters(s.data);
        }

        if (st.data?.internet) {
          setNetwork(st.data.internet);
        }
      } catch (error) {
        console.log("Backend unavailable:", error);
      }
    }

    load();
  }, []);

  // =====================================================
  // DEMO BUTTON
  // =====================================================
  

  // =====================================================
  // CLEAR
  // =====================================================
  const clear = async () => {
    console.log("CLEAR BUTTON CLICKED");

    // Immediately clear screen
    setEmergencies([]);
    setRoute([]);

    try {
      await api.post("/api/emergencies/clear");
      console.log("Backend cleared");
    } catch (error) {
      console.log("Backend clear failed, UI already cleared");
    }
  };const simulate = async (type) => {
  console.log("BUTTON CLICKED:", type);

  const demo = DEMOS[type];

  if (!demo) {
    console.error("Unknown demo:", type);
    return;
  }

  const emergency = {
    message_id: `demo-${Date.now()}`,
    node_id: "NODE-03",
    hazard: demo.hazard,
    severity: demo.severity,
    latitude: demo.latitude,
    longitude: demo.longitude,
    timestamp: new Date().toISOString(),
    ttl: 5,
    hops: 0,
    smoke: demo.smoke,
    sound: demo.sound,
    rain: demo.rain,
    flame: demo.flame,
    details: demo.details,
    active: true,
  };

  // Make the demo work immediately
  setEmergencies([emergency]);

  console.log("UI EMERGENCY:", emergency);

  setBusy(true);

  try {
    await api.post("/api/emergencies/clear");

    await api.post("/api/emergency", {
      message_id: emergency.message_id,
      node_id: emergency.node_id,
      hazard: emergency.hazard,
      latitude: emergency.latitude,
      longitude: emergency.longitude,
      timestamp: emergency.timestamp,
      ttl: emergency.ttl,
      hops: emergency.hops,
      smoke: emergency.smoke,
      sound: emergency.sound,
      rain: emergency.rain,
      flame: emergency.flame,
      details: emergency.details,
    });

    console.log("Backend sync successful");

  } catch (error) {
    console.log(
      "Backend sync failed, UI continues:",
      error?.response?.data || error.message
    );
  } finally {
    setBusy(false);
  }
};

  const active =
    Array.isArray(emergencies)
      ? emergencies.filter((e) => e.active !== false)
      : [];

  const current = active.length > 0 ? active[0] : null;

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">

        <div>
          <h1 className="text-3xl font-bold">
            Universal Emergency Mesh
          </h1>

          <p className="text-slate-400">
            Emergency detection, mesh communication and safe evacuation
          </p>
        </div>

        <div className="flex gap-3">

          <div className="px-4 py-2 rounded-lg bg-green-500/20 text-green-400">
            ● NETWORK {network}
          </div>

          <div className="px-4 py-2 rounded-lg bg-blue-500/20 text-blue-400">
            ● MESH ACTIVE
          </div>

        </div>
      </div>

      {/* EMERGENCY STATUS */}
      <div className="mb-6">

        {current ? (

          <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-6">

            <div className="flex items-center gap-4">

              <AlertTriangle
                className="text-red-400"
                size={44}
              />

              <div>

                <p className="text-sm text-red-300">
                  ACTIVE EMERGENCY
                </p>

                <h2 className="text-3xl font-bold">
                  {current.hazard}
                </h2>

                <p className="text-lg text-slate-300">
                  Severity: {current.severity}
                </p>

                <p className="text-slate-400 mt-1">
                  {current.details}
                </p>

              </div>
            </div>

          </div>

        ) : (

          <div className="rounded-2xl border border-green-500/30 bg-green-500/10 p-6">

            <div className="flex items-center gap-4">

              <ShieldCheck
                className="text-green-400"
                size={44}
              />

              <div>

                <p className="text-sm text-green-300">
                  SYSTEM STATUS
                </p>

                <h2 className="text-2xl font-bold">
                  No Active Emergency
                </h2>

              </div>

            </div>

          </div>
        )}

      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">

        <StatCard
          title="Mesh Nodes"
          value={nodes.length || 5}
          icon={<Radio />}
        />

        <StatCard
          title="Safe Shelters"
          value={shelters.length || 2}
          icon={<ShieldCheck />}
        />

        <StatCard
          title="Active Alerts"
          value={active.length}
          icon={<AlertTriangle />}
        />

        <StatCard
          title="Network"
          value={network}
          icon={<Radio />}
        />

      </div>

      {/* DEMO BUTTONS */}
      <div className="bg-slate-900 rounded-2xl p-6 mb-6">

        <h2 className="text-xl font-bold mb-4">
          Emergency Simulation
        </h2>

        <div className="flex flex-wrap gap-3">

          <button
            type="button"
            onClick={() => simulate("FIRE")}
            className="px-5 py-3 rounded-lg bg-red-600 hover:bg-red-500 active:scale-95 transition"
          >
            <Flame className="inline mr-2" size={18} />
            Fire
          </button>

          <button
            type="button"
            onClick={() => simulate("SMOKE")}
            className="px-5 py-3 rounded-lg bg-orange-600 hover:bg-orange-500 active:scale-95 transition"
          >
            <AlertTriangle className="inline mr-2" size={18} />
            Smoke
          </button>

          <button
            type="button"
            onClick={() => simulate("FLOOD")}
            className="px-5 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 active:scale-95 transition"
          >
            <CloudRain className="inline mr-2" size={18} />
            Flood
          </button>

          <button
            type="button"
            onClick={() => simulate("HIGH")}
            className="px-5 py-3 rounded-lg bg-yellow-600 hover:bg-yellow-500 active:scale-95 transition"
          >
            <Volume2 className="inline mr-2" size={18} />
            Critical Sound
          </button>

          <button
            type="button"
            onClick={clear}
            className="px-5 py-3 rounded-lg bg-green-600 hover:bg-green-500 active:scale-95 transition"
          >
            Clear Emergency
          </button>

        </div>

        {busy && (
          <p className="text-slate-400 text-sm mt-3">
            Syncing with emergency mesh...
          </p>
        )}

      </div>

      {/* MAP */}
      <div className="bg-slate-900 rounded-2xl p-4">

        <h2 className="text-xl font-bold mb-4">
          Emergency Map
        </h2>

        <MapView
          emergencies={active}
          nodes={nodes}
          shelters={shelters}
          route={route}
        />

      </div>

    </div>
  );
}
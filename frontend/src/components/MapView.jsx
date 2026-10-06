import {useEffect,useRef} from 'react';
import L from 'leaflet'; import 'leaflet/dist/leaflet.css';
const icon=(color,emoji)=>L.divIcon({className:'',html:`<div style="width:34px;height:34px;border-radius:50%;background:${color};display:flex;align-items:center;justify-content:center;border:3px solid white;box-shadow:0 3px 12px #0008;font-size:17px">${emoji}</div>`,iconSize:[34,34],iconAnchor:[17,17]});
export default function MapView({nodes=[],emergencies=[],shelters=[],route=[],user=[17.392,78.487]}){
 const ref=useRef(null),map=useRef(null),layers=useRef([]);
 useEffect(()=>{if(!ref.current)return; map.current=L.map(ref.current).setView(user,14);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'}).addTo(map.current);return()=>map.current?.remove()},[]);
 useEffect(()=>{if(!map.current)return;layers.current.forEach(x=>x.remove());layers.current=[];
 layers.current.push(L.marker(user,{icon:icon('#2563eb','📍')}).addTo(map.current).bindPopup('Your location'));
 nodes.forEach(n=>layers.current.push(L.marker([n.latitude,n.longitude],{icon:icon('#0284c7','📡')}).addTo(map.current).bindPopup(`${n.node_id}<br/>Signal ${n.signal}%<br/>Battery ${n.battery}%`)));
 emergencies.forEach(e=>{const color=e.severity==='CRITICAL'?'#dc2626':e.severity==='HIGH'?'#ea580c':'#eab308';layers.current.push(L.circle([e.latitude,e.longitude],{radius:e.hazard.includes('FLOOD')?500:350,color,fillColor:color,fillOpacity:.18,weight:2}).addTo(map.current).bindPopup(`${e.hazard} — ${e.severity}`));layers.current.push(L.marker([e.latitude,e.longitude],{icon:icon(color,e.hazard.includes('FIRE')?'🔥':e.hazard.includes('SMOKE')?'💨':'⚠️')}).addTo(map.current));});
 shelters.forEach(s=>layers.current.push(L.marker([s.latitude,s.longitude],{icon:icon('#16a34a','🏥')}).addTo(map.current).bindPopup(`${s.name}<br/>Capacity ${s.capacity}`)));
 if(route?.length>1)layers.current.push(L.polyline(route.map(p=>[p.lat,p.lng]),{color:'#22c55e',weight:6,opacity:.9}).addTo(map.current));
 },[nodes,emergencies,shelters,route,user]);
 return <div ref={ref} className="h-full min-h-[420px]"/>;
}

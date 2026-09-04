const API_BASE = localStorage.getItem("apiBase") || "http://localhost:8000";
const map = L.map("map").setView([25.6, 92.2], 6);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18,attribution:"© OpenStreetMap contributors"}).addTo(map);

let zones = [], markers = [], selected = null, coords = null;
const $ = id => document.getElementById(id);

const labels = {
  en:{title:"NER Landslide Sentinel"},
  hi:{title:"NER भूस्खलन निगरानी"},
  as:{title:"NER ভূমিস্খলন নিৰীক্ষণ"}
};

function riskClass(level){return "risk-"+level.toLowerCase().replace(" ","-")}
function setRisk(r){
  $("riskCount").textContent=zones.length;
  $("rainNow").textContent=r.current_rain_mm_h.toFixed(1);
  $("rain24").textContent=r.rain_24h_forecast_mm.toFixed(1);
  $("level").textContent=r.risk_level;
  $("score").textContent="Score "+r.risk_score;
  $("level").className=riskClass(r.risk_level);
  $("updated").textContent=new Date(r.generated_at).toLocaleTimeString();
  $("riskExplanation").innerHTML=`<strong>${r.risk_level} risk</strong> (${Math.round(r.risk_score*100)}%). `+
    `Forecast rainfall is <strong>${r.rain_24h_forecast_mm.toFixed(1)} mm</strong> over 24h; slope is <strong>${r.slope_degrees}°</strong>. `+
    `This prototype uses an explainable baseline. Production inference should combine validated rainfall, satellite soil moisture, DEM and historical-event features.`;
  $("rainBar").style.width=(r.explanation.rainfall_contribution*100)+"%";
  $("slopeBar").style.width=(r.explanation.slope_contribution*100)+"%";
  $("rainBarText").textContent=Math.round(r.explanation.rainfall_contribution*100)+"%";
  $("slopeBarText").textContent=Math.round(r.explanation.slope_contribution*100)+"%";
}

async function loadZones(){
  const res=await fetch(API_BASE+"/api/zones"); zones=(await res.json()).zones;
  markers.forEach(m=>map.removeLayer(m)); markers=[];
  zones.forEach(z=>{
    const marker=L.circleMarker([z.lat,z.lon],{radius:10,weight:2,fillOpacity:.8}).addTo(map);
    marker.bindTooltip(`${z.name} • ${z.state}`);
    marker.on("click",()=>selectZone(z));
    markers.push(marker);
  });
  await selectZone(zones[0]);
  loadPriority();
}
async function selectZone(z){
  selected=z;
  map.setView([z.lat,z.lon],8);
  try{
    const r=await fetch(`${API_BASE}/api/risk?lat=${z.lat}&lon=${z.lon}&slope=${z.slope}&soil_moisture=0.58`).then(x=>x.json());
    setRisk(r);
    markers.forEach((m,i)=>m.setRadius(zones[i].id===z.id?14:10));
  }catch(e){$("riskExplanation").textContent="Weather service unavailable. Check the API or internet connection."}
}
async function loadPriority(){
  const items=(await fetch(API_BASE+"/api/priority").then(x=>x.json())).items;
  $("priorityList").innerHTML=items.map(x=>`<div class="priority"><div><strong>${x.name}</strong><br><small>${x.state} • ${x.road}</small></div><div><strong>${x.risk_level}</strong><br><small>priority ${x.priority}</small></div></div>`).join("");
}
$("refresh").onclick=()=>selected&&selectZone(selected);
$("locate").onclick=()=>{
  if(!navigator.geolocation){$("reportStatus").textContent="Geolocation is not supported.";return}
  navigator.geolocation.getCurrentPosition(p=>{coords={latitude:p.coords.latitude,longitude:p.coords.longitude};$("coords").textContent=`${coords.latitude.toFixed(5)}, ${coords.longitude.toFixed(5)}`},()=>{$("reportStatus").textContent="Location permission was not granted."});
};
function queuedReports(){return JSON.parse(localStorage.getItem("reportQueue")||"[]")}
function updateQueue(){$("queue").textContent=queuedReports().length}
async function syncQueue(){
  let q=queuedReports(); if(!q.length)return;
  const remaining=[];
  for(const report of q){try{const r=await fetch(API_BASE+"/api/reports",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(report)});if(!r.ok)throw Error()}catch(e){remaining.push(report)}}
  localStorage.setItem("reportQueue",JSON.stringify(remaining));updateQueue();
}
$("reportForm").onsubmit=async e=>{
  e.preventDefault();
  if(!coords){$("reportStatus").textContent="Capture your location first.";return}
  const report={...coords,category:$("category").value,description:$("description").value,timestamp:new Date().toISOString()};
  try{
    const r=await fetch(API_BASE+"/api/reports",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(report)});
    if(!r.ok)throw Error();
    $("reportStatus").textContent="Report submitted successfully.";
  }catch(err){
    const q=queuedReports();q.push(report);localStorage.setItem("reportQueue",JSON.stringify(q));updateQueue();
    $("reportStatus").textContent="Network unavailable. Report queued for automatic sync.";
  }
  e.target.reset();coords=null;$("coords").textContent="Not captured";
};
$("language").onchange=e=>{document.title=labels[e.target.value].title;};
window.addEventListener("online",syncQueue);
updateQueue(); loadZones(); syncQueue();

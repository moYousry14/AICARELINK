import math
import requests
import polyline

# --- NATIONAL GRID DATABASE ---
LOCATIONS = {
    "Sokhna - Galala Road": (29.450, 32.480),
    "Suez City Center": (29.970, 32.540),
    "Cairo-Suez Highway": (30.010, 31.850),
    "New Capital Gates": (30.000, 31.700)
}

HOSPITALS = [
    {"id": 1, "name": "Galala Univ. Hospital", "lat": 29.392, "lon": 32.508, "feat": ["Cath Lab", "Trauma L1"], "busy": True}, 
    {"id": 4, "name": "Ain Sokhna Emergency", "lat": 29.589, "lon": 32.336, "feat": ["First Aid", "Stabilization"], "busy": False},
    {"id": 2, "name": "Suez Insurance Complex", "lat": 29.975, "lon": 32.530, "feat": ["Cath Lab", "ICU", "Dialysis"], "busy": False},
    {"id": 3, "name": "Suez General Hosp.", "lat": 29.966, "lon": 32.549, "feat": ["ER", "Surgery", "Burn Unit"], "busy": False},
    {"id": 5, "name": "Capital Care Medical (New Capital)", "lat": 30.010, "lon": 31.730, "feat": ["Cath Lab", "Stroke Unit", "Robotic Surgery"], "busy": False},
    {"id": 6, "name": "Air Force Specialized Hosp.", "lat": 30.025, "lon": 31.450, "feat": ["Cath Lab", "Stroke Unit", "Helipad", "Trauma L1"], "busy": False},
    {"id": 7, "name": "Medical Center (5th Settlement)", "lat": 30.005, "lon": 31.420, "feat": ["ER", "Cardiology"], "busy": False}
]

# --- ROUTING ENGINE ---
def get_real_route(slat, slon, elat, elon):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{slon},{slat};{elon},{elat}?overview=full"
        r = requests.get(url, timeout=1.5)
        if r.status_code == 200:
            data = r.json()['routes'][0]
            return polyline.decode(data['geometry']), data['distance']/1000, data['duration']/60
    except: pass
    
    # Fallback
    dist = math.sqrt((slat-elat)**2 + (slon-elon)**2) * 111
    return [[slat, slon], [elat, elon]], dist, dist*1.2

# هنا الحل: وحدنا الاسم ليكون find_best_hospital
def find_best_hospital(lat, lon, diagnosis):
    if diagnosis == 'MI': req = "Cath Lab"
    elif diagnosis == 'STTC': req = "ICU"
    elif diagnosis == 'CD': req = "Cardiology"
    else: req = "ER"
    
    cands = []
    for h in HOSPITALS:
        _, dist, _ = get_real_route(lat, lon, h['lat'], h['lon'])
        score = dist
        # Logic penalties
        if req == "Cath Lab" and "Cath Lab" not in h['feat']: score += 2000
        elif req not in h['feat'] and req!="ER": score += 500
        # Busy penalty handled in UI phase
        cands.append({**h, "dist": dist, "score": score})
    
    cands.sort(key=lambda x: x['score'])
    return cands, req
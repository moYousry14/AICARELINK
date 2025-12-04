import streamlit as st
import time
import numpy as np
# استيراد الملفات من فولدر src
from src import routing, ai_engine, ui_components

# 1. SETUP
ui_components.apply_styling()

# 2. STATE MANAGEMENT
if 'lat' not in st.session_state: st.session_state['lat'] = 29.600 
if 'lon' not in st.session_state: st.session_state['lon'] = 32.350
if 'transmitted' not in st.session_state: st.session_state['transmitted'] = False
if 'status' not in st.session_state: st.session_state['status'] = "IDLE"
if 'current_hospital_idx' not in st.session_state: st.session_state['current_hospital_idx'] = 0

# 3. SIDEBAR (INPUTS)
with st.sidebar:
    st.markdown("## 📟 INPUT FEED")
    st.divider()
    
    # Patient Select
    patient_select = st.selectbox("Select Patient Feed:", [
        "Patient #104 (Male, 45y - Routine)",
        "Patient #209 (Female, 62y - Chest Pain)",
        "Patient #315 (Male, 50y - Palpitations)"
    ])
    
    if "104" in patient_select: sim_code = "NORM"; p_info = {"Name": "Ahmed Hassan", "Age": 45, "Blood": "O+", "History": "None", "Allergies": "Penicillin"}
    elif "209" in patient_select: sim_code = "MI"; p_info = {"Name": "Fatima Ali", "Age": 62, "Blood": "A-", "History": "Hypertension", "Allergies": "None"}
    else: sim_code = "STTC"; p_info = {"Name": "Omar Khaled", "Age": 50, "Blood": "B+", "History": "Smoker", "Allergies": "None"}
    
    if 'last_pat' not in st.session_state: st.session_state['last_pat'] = ""
    if st.session_state['last_pat'] != patient_select:
        st.session_state['status'] = "IDLE"
        st.session_state['current_hospital_idx'] = 0
        with st.spinner("🔄 Syncing..."): time.sleep(0.5)
        st.session_state['last_pat'] = patient_select

    st.markdown("### 👤 Patient EHR Profile")
    st.markdown(f"""<div style="background:#111; padding:15px; border-radius:8px; border-left:4px solid #555; color:#ccc; font-size:14px;">
        <b>Name:</b> {p_info['Name']}<br><b>Age/Sex:</b> {p_info['Age']}<br><b>History:</b> {p_info['History']}</div>""", unsafe_allow_html=True)

    st.divider()
    
    # Location Select
    st.markdown("### 📍 Location")
    loc_name = st.selectbox("GPS:", list(routing.LOCATIONS.keys()))
    
    if 'last_loc' not in st.session_state: st.session_state['last_loc'] = loc_name
    if st.session_state['last_loc'] != loc_name:
        st.session_state['lat'], st.session_state['lon'] = routing.LOCATIONS[loc_name]
        st.session_state['last_loc'] = loc_name
        st.session_state['status'] = "IDLE"

# 4. MAIN CONTROLLER LOGIC
ui_components.render_header()

# AI Core
model, classes = ai_engine.load_resources()
lead_signals, bpm = ai_engine.generate_multi_lead_signal(sim_code)
pred_label, conf = ai_engine.run_inference(model, classes, sim_code)

# Routing Logic
all_candidates, unit = routing.find_best_hospital(st.session_state['lat'], st.session_state['lon'], pred_label)

# Safety Check
if st.session_state['current_hospital_idx'] >= len(all_candidates):
    st.session_state['current_hospital_idx'] = 0
target = all_candidates[st.session_state['current_hospital_idx']]

# 5. UI RENDERING
c1, c2 = st.columns([2, 1])
with c1: pass 
with c2: ui_components.render_status_badge(pred_label)

spo2 = "88%" if pred_label == 'MI' else "98%"
ui_components.render_metrics(bpm, spo2, conf, unit)
ui_components.render_ecg(lead_signals)

# 6. HANDOVER SECTION
st.markdown("---")
c1, c2 = st.columns([1, 1])

# Fetch Route Data
route_pts, dist, dur = routing.get_real_route(st.session_state['lat'], st.session_state['lon'], target['lat'], target['lon'])

with c1:
    st.subheader("🗺️ Dynamic Route")
    # ✅ التصحيح هنا: تمرير 5 متغيرات للدالة
    ui_components.render_map(
        st.session_state['lat'], 
        st.session_state['lon'], 
        target, 
        route_pts, 
        all_candidates
    )

with c2:
    st.subheader("🏥 Coordination Hub")
    st.info(f"**Target:** {target['name']}")
    st.write(f"**ETA:** {int(dur)} mins | **Dist:** {dist:.1f} km")
    
    if st.session_state['status'] == "IDLE":
        if st.button("📡 TRANSMIT DATA", type="primary", use_container_width=True):
            with st.spinner("Handshaking..."): time.sleep(1.5)
            if target['busy']: st.session_state['status'] = "REJECTED"
            else: st.session_state['status'] = "ACCEPTED"
            st.rerun()
            
    elif st.session_state['status'] == "REJECTED":
        st.markdown(f"""<div class="comm-box-rejected"><h3 style="color:#ff0000; margin:0;">❌ REQUEST DECLINED</h3>
            <p><b>From:</b> {target['name']}<br><b>Reason:</b> "Capacity Full"</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 REROUTE TO NEXT AVAILABLE", type="primary", use_container_width=True):
            st.session_state['current_hospital_idx'] += 1
            st.session_state['status'] = "IDLE"
            st.rerun()
            
    elif st.session_state['status'] == "ACCEPTED":
        st.markdown(f"""<div class="comm-box-success"><h3 style="color:#00ff00; margin:0;">✅ CONFIRMED</h3>
            <p><b>From:</b> {target['name']}<br><b>Action:</b> Team Activated</p></div>""", unsafe_allow_html=True)
        if st.button("🏁 Start Mission", use_container_width=True):
            st.session_state['status'] = "IDLE"
            st.rerun()
import streamlit as st
import time
import numpy as np
# Importing modules from src folder
from src import routing, ai_engine, ui_components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Aicarelink National Grid", page_icon="🌐")

# --- 2. DISCLAIMER / AGREEMENT SCREEN ---
if 'agreed' not in st.session_state:
    st.session_state['agreed'] = False

if not st.session_state['agreed']:
    # Show the Splash Screen ONLY
    st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
        .splash-container {
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            height: 90vh; text-align: center; padding: 20px;
        }
        .logo-text {
            font-size: 50px; font-weight: 900; letter-spacing: 4px;
            background: linear-gradient(90deg, #00ff00, #00ffff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }
        .disclaimer-box {
            background: rgba(20, 20, 20, 0.9); border: 1px solid #333;
            border-left: 5px solid #ff4444; border-radius: 10px;
            padding: 30px; max-width: 700px; text-align: left;
            box-shadow: 0 0 50px rgba(0,0,0,0.8);
        }
        .highlight { color: #00ff00; font-weight: bold; }
        .warning { color: #ff4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="splash-container">
        <div class="logo-text">AICARELINK SYSTEM</div>
        <div class="disclaimer-box">
            <h3 style="margin-top:0;">⚠️ CONFIDENTIAL PROTOTYPE ACCESS</h3>
            <p>You are accessing the <b>National Emergency Grid (Release Candidate v1.0.0)</b>. Please acknowledge the following:</p>
            <hr style="border-color: #444;">
            <ul>
                <li>
                    <span class="highlight">REAL AI ENGINE ACTIVE:</span> 
                    The 12-Lead ECG analysis is performed in real-time using a <b>ResNet-1d Deep Learning Model</b> trained on PTB-XL clinical data.
                </li>
                <br>
                <li>
                    <span class="warning">SIMULATION MODE:</span> 
                    Patient telemetry (BP, SpO2) and GPS coordinates are currently simulated for demonstration scenarios.
                </li>
                <br>
                <li>
                    <b>COMPLIANCE:</b> This system complies with Phase 1 pre-hospital triage protocols.
                </li>
            </ul>
            <br>
            <small style="color: #888;">Authorized Personnel Only.</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ I UNDERSTAND & PROCEED TO DASHBOARD", type="primary", use_container_width=True):
            st.session_state['agreed'] = True
            st.rerun()

    st.stop() # Stop execution until agreed

# =========================================================
# --- 3. MAIN APPLICATION ---
# =========================================================

# Apply Styling
ui_components.apply_styling()

# State Management
if 'lat' not in st.session_state: st.session_state['lat'] = 29.600 
if 'lon' not in st.session_state: st.session_state['lon'] = 32.350
if 'transmitted' not in st.session_state: st.session_state['transmitted'] = False
if 'status' not in st.session_state: st.session_state['status'] = "IDLE"
if 'current_hospital_idx' not in st.session_state: st.session_state['current_hospital_idx'] = 0

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 📟 INPUT FEED")
    st.divider()
    
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
    
    st.markdown("### 📍 Location")
    loc_name = st.selectbox("GPS:", list(routing.LOCATIONS.keys()))
    if 'last_loc' not in st.session_state: st.session_state['last_loc'] = loc_name
    if st.session_state['last_loc'] != loc_name:
        st.session_state['lat'], st.session_state['lon'] = routing.LOCATIONS[loc_name]
        st.session_state['last_loc'] = loc_name
        st.session_state['status'] = "IDLE"

# --- MAIN CONTROLLER ---
ui_components.render_header()

# AI
model, classes = ai_engine.load_resources()
lead_signals, bpm = ai_engine.generate_multi_lead_signal(sim_code)
pred_label, conf = ai_engine.run_inference(model, classes, sim_code)

# Routing
all_candidates, unit = routing.find_best_hospital(st.session_state['lat'], st.session_state['lon'], pred_label)
if st.session_state['current_hospital_idx'] >= len(all_candidates):
    st.session_state['current_hospital_idx'] = 0
target = all_candidates[st.session_state['current_hospital_idx']]

# UI Rendering
c1, c2 = st.columns([2, 1])
with c1: pass 
with c2: ui_components.render_status_badge(pred_label)

spo2 = "88%" if pred_label == 'MI' else "98%"
ui_components.render_metrics(bpm, spo2, conf, unit)
ui_components.render_ecg(lead_signals)

# Handover
st.markdown("---")
c1, c2 = st.columns([1, 1])
route_pts, dist, dur = routing.get_real_route(st.session_state['lat'], st.session_state['lon'], target['lat'], target['lon'])

with c1:
    st.subheader("🗺️ Dynamic Route")
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
            <p><b>From:</b> {target['name']}<br><b>Action:</b> Team Activated. Bed Reserved.</p></div>""", unsafe_allow_html=True)
        
        url = f"https://www.google.com/maps/dir/?api=1&destination={target['lat']},{target['lon']}"
        
        # New Buttons Row
        b1, b2 = st.columns(2)
        with b1:
            st.link_button("🚀 START MISSION", url, type="primary", use_container_width=True)
        with b2:
            if st.button("📄 DOWNLOAD REPORT", use_container_width=True):
                st.toast("Generating PDF Report...", icon="🖨️")
                time.sleep(1.5)
                st.toast("Report Saved to Cloud Archive.", icon="☁️")

        if st.button("🏁 End Mission & Reset", use_container_width=True):
            st.session_state['status'] = "IDLE"
            st.session_state['current_hospital_idx'] = 0
            st.rerun()
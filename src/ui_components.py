import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

def apply_styling():
    st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
        .app-title { font-size: 36px; font-weight: 900; background: linear-gradient(90deg, #00ff00, #00ffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase; letter-spacing: 2px; }
        
        .metric-card { background: rgba(20, 20, 20, 0.85); border: 1px solid #333; border-top: 3px solid #00ff00; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        
        .crit { background: rgba(50, 0, 0, 0.9); border: 2px solid #ff0000; color: #ff5555; animation: pulse 1s infinite; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 20px;}
        .warn { background: rgba(50, 40, 0, 0.9); border: 2px solid #ffaa00; color: #ffaa00; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 20px;}
        .safe { background: rgba(0, 30, 0, 0.9); border: 2px solid #00ff00; color: #00ff00; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 20px;}
        
        .comm-box-success { background: rgba(0, 40, 0, 0.8); border: 1px solid #00ff00; padding: 20px; border-radius: 10px; margin-top: 15px; animation: slideIn 0.5s ease-out; }
        .comm-box-rejected { background: rgba(60, 0, 0, 0.8); border: 1px solid #ff0000; padding: 20px; border-radius: 10px; margin-top: 15px; animation: shake 0.5s; }

        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes shake { 0% { transform: translateX(0); } 25% { transform: translateX(-5px); } 50% { transform: translateX(5px); } 100% { transform: translateX(0); } }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    c1, c2,c3 = st.columns([3,7,2])
    with c1: 
        try: st.image("logo.png", width=300) 
        except: st.markdown("# ⚕️")
    with c2: 
        st.markdown('<div class="app-title">Aicarelink National Grid</div>', unsafe_allow_html=True)
        st.caption("AI-Powered Emergency Triage & Cross-Governorate Referral System v1.0.0")

def render_status_badge(pred_label):
    if pred_label == 'MI': status_html = '<div class="crit">🚨 CRITICAL: STEMI DETECTED</div>'
    elif pred_label == 'STTC': status_html = '<div class="warn">⚠️ WARNING: ISCHEMIA</div>'
    else: status_html = '<div class="safe">✅ STATUS: STABLE</div>'
    st.markdown(status_html, unsafe_allow_html=True)

def render_metrics(bpm, spo2, conf, unit):
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><h3>❤️ {int(bpm)}</h3><small>BPM</small></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><h3>💧 {spo2}</h3><small>SpO2</small></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><h3>🧠 {conf:.1f}%</h3><small>AI Confidence</small></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><h3>🏥 {unit}</h3><small>Required</small></div>', unsafe_allow_html=True)

def render_ecg(lead_signals):
    st.write("")
    fig, axes = plt.subplots(2, 2, figsize=(12, 3.5))
    fig.patch.set_facecolor('#000')
    leads_layout = [('I', axes[0,0]), ('II', axes[0,1]), ('V1', axes[1,0]), ('V6', axes[1,1])]
    for name, ax in leads_layout:
        ax.plot(lead_signals[name], color='#00ff00', linewidth=1.5)
        ax.set_facecolor('#000'); ax.grid(color='#003300', linewidth=0.5, linestyle=':')
        ax.set_title(f"Lead {name}", color='#00aa00', loc='left', fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_visible(False)
    st.pyplot(fig)

def render_map(amb_lat, amb_lon, target, route_pts, candidates):
    m = folium.Map(location=[amb_lat, amb_lon], zoom_start=9, tiles="CartoDB dark_matter")
    # Ambulance
    folium.Marker([amb_lat, amb_lon], icon=folium.Icon(color="red", icon="truck-medical", prefix="fa")).add_to(m)
    # All candidates (dimmed)
    for c in candidates:
        color = "green" if c['id'] == target['id'] else "gray"
        opacity = 1.0 if c['id'] == target['id'] else 0.5
        folium.Marker([c['lat'], c['lon']], icon=folium.Icon(color=color, icon="h-square", prefix="fa"), opacity=opacity, tooltip=c['name']).add_to(m)
    # Route
    folium.PolyLine(route_pts, color="#00aaff", weight=4, opacity=0.8).add_to(m)
    st_folium(m, width="100%", height=300)
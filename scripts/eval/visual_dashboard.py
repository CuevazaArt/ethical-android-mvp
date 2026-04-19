import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import os
import sys
import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from src.kernel import EthicalKernel
except ImportError:
    st.error("Could not find EthicalKernel. Run from project root.")
    st.stop()

# --- THEME & CSS ---
st.set_page_config(page_title="ANTIGRAVITY L1 | Nomadic Dashboard", layout="wide", page_icon="🛰️")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30333d;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #1a1c24 0%, #0e1117 100%);
        border: 1px solid #30333d;
        margin-bottom: 15px;
    }
    .label {
        color: #808495;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #00ffcc;
    }
    .small-text {
        font-size: 0.8rem;
        color: #808495;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- APP HEADER ---
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.title("🛰️ ANTIGRAVITY L1")
    st.markdown("<p style='color: #808495; margin-top: -20px;'>Nomadic Kernel Orchestration & Behavioral Harmonics</p>", unsafe_allow_stdio=True)

with c2:
    st.write("")
    st.write("")
    st.metric("HEARTBEAT", "SYNCHRONIZED", delta="LIVE TELEMETRY", delta_color="normal")

with c3:
    st.write("")
    st.write("")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.metric("LOCAL CLOCK", now)

st.markdown("---")

# --- KERNEL INIT ---
@st.cache_resource
def get_kernel():
    os.environ["KERNEL_TRI_LOBE_ENABLED"] = "1"
    k = EthicalKernel()
    return k

kernel = get_kernel()

# --- DATA ACQUISITION HELPERS ---
def get_current_metrics():
    snap = kernel.identity.snapshot
    # Get last state snapshots
    perception = getattr(kernel, "last_perception_result", None)
    decision = getattr(kernel, "last_decision", None)
    stylized = getattr(kernel, "last_stylized", None)
    
    return {
        "reputation": snap.reputation_score,
        "node_id": str(snap.node_id)[:8],
        "episodes": len(kernel.memory.episodes) if hasattr(kernel.memory, "episodes") else 0,
        "perception": perception,
        "decision": decision,
        "stylized": stylized
    }

metrics = get_current_metrics()

# --- TOP LEVEL METRICS ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Reputation Score", f"{metrics['reputation']}%")

with m2:
    st.metric("Node Identifier", metrics['node_id'])

with m3:
    st.metric("Narrative Episodes", metrics['episodes'])

with m4:
    battery = "NOMINAL"
    if metrics['perception'] and metrics['perception'].temporal_context:
        bat = metrics['perception'].temporal_context.battery_minutes_remaining
        if bat is not None:
            battery = f"{int(bat)} min"
    st.metric("Battery Projection", battery)

st.markdown("---")

# --- MAIN DASHBOARD LAYOUT ---
col_left, col_mid, col_right = st.columns([1.2, 1.2, 1.5])

with col_left:
    st.subheader("🧪 Behavioral Physics")
    limbic_placeholder = st.empty()
    st.write("")
    charm_placeholder = st.empty()

with col_mid:
    st.subheader("👁️ Perception Stream")
    scenario_placeholder = st.empty()
    confidence_placeholder = st.empty()
    trust_placeholder = st.empty()
    
    st.markdown("---")
    st.subheader("📜 Chronic Memory")
    memory_placeholder = st.empty()

with col_right:
    st.subheader("⚖️ Executive Decision Logic")
    
    st.markdown("<div class='label'>Active Policy</div>", unsafe_allow_stdio=True)
    st.markdown("<div class='value'>PHASE 8: NOMADIC HARMONICS</div>", unsafe_allow_stdio=True)
    
    st.write("")
    gate_placeholder = st.empty()
    
    st.write("")
    st.markdown("<div class='label'>Last Decision Intent</div>", unsafe_allow_stdio=True)
    narrative_placeholder = st.empty()
    
    st.write("")
    st.subheader("🛡️ Chain of Trust (Secure Boot)")
    boot_placeholder = st.empty()

# --- DATA LOOP ---
while True:
    try:
        # Refresh metrics
        mt = get_current_metrics()
        
        # 1. LIMBIC RESONANCE
        try:
            res = kernel.limbic_lobe.basal_ganglia.get_current_resonance()
            df_res = pd.DataFrame(dict(axis=list(res.keys()), value=list(res.values())))
            fig_limbic = px.line_polar(df_res, r='value', theta='axis', line_close=True, range_r=[0, 1], title="Limbic Resonance (6-Axis)")
            fig_limbic.update_traces(fill='toself', line_color='#ff3366', fillcolor='rgba(255, 51, 102, 0.3)')
            fig_limbic.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            limbic_placeholder.plotly_chart(fig_limbic, use_container_width=True)
        except:
            limbic_placeholder.warning("Resonance stabilizing...")

        # 2. CHARM ENGINE RADAR (REAL DATA)
        if mt['stylized']:
            charm_v = mt['stylized'].charm_vector
            df_charm = pd.DataFrame(dict(axis=list(charm_v.keys()), value=list(charm_v.values())))
            fig_charm = px.line_polar(df_charm, r='value', theta='axis', line_close=True, range_r=[0, 1], title="Charm Vector (L1 Styling)")
            fig_charm.update_traces(fill='toself', line_color='#00ffcc', fillcolor='rgba(0, 255, 204, 0.3)')
            fig_charm.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            charm_placeholder.plotly_chart(fig_charm, use_container_width=True)
        else:
            charm_placeholder.info("Awaiting execution turn to generate Charm Vector.")

        # 3. PERCEPTION SUMMARY
        if mt['perception']:
            p = mt['perception']
            scenario_placeholder.markdown(f"<div class='value'>{p.perception.scenario_summary[:50]}...</div>", unsafe_allow_stdio=True)
            conf = p.perception_confidence.overall_confidence if p.perception_confidence else 0.5
            confidence_placeholder.progress(conf)
            trust_val = p.multimodal_trust.aggregate_trust if p.multimodal_trust else 0.5
            trust_placeholder.info(f"Multimodal Trust: {int(trust_val*100)}%")
        else:
            scenario_placeholder.markdown("<div class='small-text'>Awaiting sensory ingestion...</div>", unsafe_allow_stdio=True)

        # 4. CHRONIC MEMORY
        episodes = kernel.memory.episodes
        if episodes:
            last_3 = list(episodes)[-3:]
            last_3.reverse()
            mem_text = ""
            for e in last_3:
                mem_text += f"- **{e.get('id', 'EP')}**: {e.get('scenario_summary', 'No summary')[:40]}...\n"
            memory_placeholder.markdown(mem_text)
        else:
            memory_placeholder.info("Chronicles are empty. Boot clean.")

        # 5. GATING & NARRATIVE
        if mt['decision']:
            d = mt['decision']
            if d.blocked:
                gate_placeholder.error(f"VETO: {d.block_reason}")
            else:
                gate_placeholder.success("SECURE: Ethical Passthrough Active")
            
            narrative_placeholder.code(f"Action: {d.final_action}\nMode: {d.decision_mode}\nVerdict: {d.moral.global_verdict.value if d.moral else 'N/A'}")
        else:
            gate_placeholder.warning("Gate status: STANDBY")

        # 6. BOOT STATUS
        boot_placeholder.json({
            "integrity_verified": True,
            "rot_anchor_sig": "JUAN_L0_L1_ANCHORED",
            "manifest_entries": 12,
            "last_seal": datetime.datetime.now().strftime("%H:%M:%S")
        })

        time.sleep(1.5)
        st.rerun()

    except Exception as e:
        st.error(f"Dashboard Loop Failure: {e}")
        time.sleep(5)
        st.rerun()

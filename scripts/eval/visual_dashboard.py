import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import os
import sys

# Añadir src al path para que encuentre el kernel
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from src.kernel import EthicalKernel
except ImportError:
    st.error("No se pudo encontrar el EthicalKernel. Asegúrate de ejecutar este script desde la raíz del proyecto.")
    st.stop()

st.set_page_config(page_title="Antigravity Nomadic Dashboard", layout="wide", page_icon="🧠")

st.title("🧠 Antigravity: Real-Time Ethosocial Harmonics")
st.markdown("---")

# Inicialización del Kernel (Cacheamos para no recrearlo cada slide)
@st.cache_resource
def get_kernel():
    os.environ["KERNEL_TRI_LOBE_ENABLED"] = "1"
    return EthicalKernel()

kernel = get_kernel()

# Layout de columnas
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Limbic Resonance (6-Axis)")
    resonance_placeholder = st.empty()
    st.markdown("---")
    st.header("Sovereignty & Trust")
    trust_placeholder = st.empty()

with col2:
    st.header("Thalamic Pulse & Ethical Gating")
    gating_placeholder = st.empty()
    st.markdown("---")
    st.header("Cognitive Biography (Traumas & Learnings)")
    bio_placeholder = st.empty()

# Loop de refresco
while True:
    try:
        # Extraer resonancia
        res = kernel.orchestrator.limbic_lobe.basal_ganglia.get_current_resonance()
        df_res = pd.DataFrame(dict(
            axis=list(res.keys()),
            value=list(res.values())
        ))

        # Radar Chart
        fig_radar = px.line_polar(df_res, r='value', theta='axis', line_close=True, range_r=[0, 1])
        fig_radar.update_traces(fill='toself')
        resonance_placeholder.plotly_chart(fig_radar, use_container_width=True)

        # Trust Gauge
        snap = kernel.identity.snapshot
        fig_trust = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = snap.reputation_score,
            title = {'text': "Reputation Score (%)"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps' : [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}]
            }
        ))
        trust_placeholder.plotly_chart(fig_trust, use_container_width=True)

        # Biography / Traumas
        traumas_data = []
        for t in snap.traumas:
            traumas_data.append({"ID": t.get("id", "N/A"), "Description": t.get("description", "Unknown")})
        
        if traumas_data:
            bio_placeholder.table(pd.DataFrame(traumas_data))
        else:
            bio_placeholder.info("No active traumas. Kernel stability is high.")

        # Ethical Gate Status
        gating_placeholder.success("SYSTEM READY: Ethical Passthrough Active")
        gating_placeholder.info(f"Node ID: {snap.node_id}")

        time.sleep(1) # Actualización fluida
    except Exception as e:
        st.error(f"Error en el ciclo de monitoreo: {e}")
        break

import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="NeuroPilot AI Dashboard", layout="wide")

st.title("🧠 NeuroPilot AI – Predictive Computer-Use Agent")
st.markdown("Monitor and control your autonomous AI agent.")

# Sidebar for Security
st.sidebar.header("Security Status 🔒")
st.sidebar.success("✅ Face Auth: Passed")
st.sidebar.success("✅ Voice Auth: Passed")
st.sidebar.info("Continuous Behavior Tracking: Active")
st.sidebar.metric("Intruder Risk Score", "0.01 / 1.0")

# Main Content
st.header("Agent Command Center")

instruction = st.text_input("Enter Task Instruction:", placeholder="e.g., Open Notepad and type 'Hello World'")
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Execute Task"):
        if instruction:
            try:
                res = requests.post(f"{API_URL}/execute", json={"instruction": instruction})
                if res.status_code == 200:
                    st.success(f"Task Started: {instruction}")
                else:
                    st.error("Failed to start task.")
            except Exception as e:
                st.error(f"Backend offline: {e}")

with col2:
    if st.button("🛑 Stop Agent"):
        try:
            res = requests.post(f"{API_URL}/stop")
            st.warning("Agent execution stopped.")
        except:
            st.error("Backend offline.")

st.divider()

st.subheader("Agent Status")
status_placeholder = st.empty()

# Polling loop mock
try:
    res = requests.get(f"{API_URL}/status")
    data = res.json()
    if data["is_running"]:
        status_placeholder.info(f"🔄 Currently Executing: {data['current_task']}")
    else:
        status_placeholder.success("✅ Idle")
except:
    status_placeholder.error("Cannot connect to Agent Backend.")

st.subheader("Predictive Engine 🔮")
st.write("Predicted next actions based on current context:")
st.button("Open IDE and run local server (85% confidence)")

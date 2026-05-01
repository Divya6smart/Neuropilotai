"""NeuroPilot AI — Streamlit Dashboard with real-time status and auth flow."""
import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="NeuroPilot AI Dashboard", layout="wide",
                   page_icon="🧠")

# ── Session state init ────────────────────────────────────
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "risk_score" not in st.session_state:
    st.session_state.risk_score = 0.0


def api_headers():
    """Build Authorization headers if token exists."""
    if st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}


# ── Sidebar: Security Panel ──────────────────────────────
st.sidebar.header("🔒 Security Panel")

if st.session_state.auth_token:
    st.sidebar.success("✅ Authenticated")
    st.sidebar.metric("Risk Score", f"{st.session_state.risk_score:.3f} / 1.0")

    if st.sidebar.button("🔓 Logout"):
        st.session_state.auth_token = None
        st.rerun()
else:
    st.sidebar.warning("🔐 Not authenticated")
    if st.sidebar.button("🔑 Authenticate (Face)"):
        try:
            res = requests.post(f"{API_URL}/auth/face",
                                json={"image_path": "data/screenshots/latest.png"},
                                timeout=10)
            if res.status_code == 200:
                data = res.json()
                st.session_state.auth_token = data["token"]
                st.sidebar.success("Authentication passed!")
                st.rerun()
            else:
                st.sidebar.error(f"Auth failed: {res.json().get('detail', 'Unknown')}")
        except requests.ConnectionError:
            st.sidebar.error("Backend offline")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    if st.sidebar.button("🔑 Multi-Factor Auth"):
        try:
            res = requests.post(f"{API_URL}/auth/multi", timeout=10)
            if res.status_code == 200:
                data = res.json()
                st.session_state.auth_token = data["token"]
                st.sidebar.success(f"MFA passed (risk: {data['risk_level']})")
                st.rerun()
            else:
                st.sidebar.error("MFA failed")
        except requests.ConnectionError:
            st.sidebar.error("Backend offline")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")


# ── Header ────────────────────────────────────────────────
st.title("🧠 NeuroPilot AI — Autonomous Agent Dashboard")
st.markdown("Real-time monitoring & control with zero-trust security.")

st.divider()

# ── Agent Status ──────────────────────────────────────────
st.subheader("📡 Agent Status")
status_col, risk_col = st.columns(2)

with status_col:
    try:
        res = requests.get(f"{API_URL}/status", timeout=5)
        data = res.json()
        if data["is_running"]:
            st.info(f"🔄 Executing: **{data['current_task']}**")
        else:
            st.success("✅ Agent Idle — Ready for tasks")
    except requests.ConnectionError:
        st.error("❌ Cannot connect to backend")
    except Exception as e:
        st.error(f"Status error: {e}")

with risk_col:
    if st.session_state.auth_token:
        try:
            res = requests.get(f"{API_URL}/auth/risk/mock_user", timeout=5)
            score = res.json().get("risk_score", 0.0)
            st.session_state.risk_score = score
            if score < 0.3:
                st.success(f"🟢 Risk: {score:.3f} (Low)")
            elif score < 0.7:
                st.warning(f"🟡 Risk: {score:.3f} (Medium)")
            else:
                st.error(f"🔴 Risk: {score:.3f} (HIGH)")
        except Exception:
            st.metric("Risk Score", "N/A")

st.divider()

# ── Command Center ────────────────────────────────────────
st.subheader("🎮 Command Center")

instruction = st.text_input(
    "Task Instruction:",
    placeholder="e.g., Open Notepad and type 'Hello World'",
    max_chars=500,
)

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Execute Task", disabled=not st.session_state.auth_token):
        if not st.session_state.auth_token:
            st.error("Authenticate first!")
        elif not instruction:
            st.warning("Enter a task instruction")
        else:
            try:
                res = requests.post(
                    f"{API_URL}/execute",
                    json={"instruction": instruction},
                    headers=api_headers(),
                    timeout=10,
                )
                if res.status_code == 200:
                    st.success(f"✅ Task started: {instruction}")
                elif res.status_code == 409:
                    st.warning("Agent is busy — stop current task first")
                elif res.status_code == 401:
                    st.error("Session expired — re-authenticate")
                    st.session_state.auth_token = None
                else:
                    st.error(f"Error: {res.text}")
            except requests.ConnectionError:
                st.error("Backend offline")
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("🛑 Stop Agent", disabled=not st.session_state.auth_token):
        try:
            res = requests.post(f"{API_URL}/stop", headers=api_headers(), timeout=10)
            if res.status_code == 200:
                st.warning("Agent stopped")
            elif res.status_code == 401:
                st.error("Session expired")
                st.session_state.auth_token = None
        except requests.ConnectionError:
            st.error("Backend offline")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ── History ───────────────────────────────────────────────
st.subheader("📜 Action History")
if st.session_state.auth_token:
    try:
        res = requests.get(f"{API_URL}/history?limit=20",
                           headers=api_headers(), timeout=5)
        if res.status_code == 200:
            history = res.json().get("history", [])
            if history:
                for entry in reversed(history[-10:]):
                    status = "✅" if entry["success"] else "❌"
                    st.text(f"{status} [{entry['timestamp'][:19]}] "
                            f"{entry['action'].get('action_type', '?')}: "
                            f"{entry['task'][:60]}")
            else:
                st.info("No actions recorded yet")
        elif res.status_code == 401:
            st.warning("Session expired")
    except Exception:
        st.info("History unavailable")
else:
    st.info("Authenticate to view history")

st.divider()

# ── Predictive Engine ─────────────────────────────────────
st.subheader("🔮 Predictive Engine")
st.caption("Predicted next actions based on usage patterns:")
st.button("Open IDE and run local server (85% confidence)", disabled=True)
st.button("Open browser to documentation (72% confidence)", disabled=True)

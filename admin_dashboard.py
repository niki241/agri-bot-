"""
Kisan Mitra — Admin Dashboard
Run: streamlit run admin_dashboard.py
"""
import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Kisan Mitra Admin",
    page_icon="🌾",
    layout="wide",
)


def api_get(path: str):
    """Helper to make GET requests to the FastAPI backend."""
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is the FastAPI server running?")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(path: str, data: dict):
    """Helper to make POST requests to the FastAPI backend."""
    try:
        resp = requests.post(f"{API_BASE}{path}", json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# --- Sidebar ---
st.sidebar.title("🌾 Kisan Mitra")
st.sidebar.markdown("**Admin Dashboard**")
page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "👨‍🌾 Farmers", "💬 Query Logs", "📡 Broadcast", "🧪 Test Advisory"],
)

# --- Dashboard Page ---
if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    stats = api_get("/api/analytics/dashboard")
    if stats:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Farmers", stats["total_farmers"])
        col2.metric("Total Queries", stats["total_queries"])
        col3.metric("Queries Today", stats["queries_today"])
        col4.metric("Avg Response (ms)", f"{stats['avg_response_time_ms']:.0f}")

        st.divider()

        # Charts
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Language Distribution")
            if stats["language_split"]:
                lang_df = pd.DataFrame(
                    list(stats["language_split"].items()),
                    columns=["Language", "Count"],
                )
                lang_df["Language"] = lang_df["Language"].map(
                    {"te": "Telugu", "hi": "Hindi", "en": "English"}
                ).fillna(lang_df["Language"])
                fig = px.pie(lang_df, values="Count", names="Language", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data yet")

        with chart_col2:
            st.subheader("Intent Distribution")
            if stats["intent_split"]:
                intent_df = pd.DataFrame(
                    list(stats["intent_split"].items()),
                    columns=["Intent", "Count"],
                )
                fig = px.bar(intent_df, x="Intent", y="Count", color="Intent")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data yet")

        # Recent queries table
        st.subheader("Recent Queries")
        if stats["recent_queries"]:
            df = pd.DataFrame(stats["recent_queries"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No queries yet")

# --- Farmers Page ---
elif page == "👨‍🌾 Farmers":
    st.title("👨‍🌾 Farmers")

    farmers = api_get("/api/farmers?limit=200")
    if farmers:
        st.metric("Registered Farmers", len(farmers))

        if farmers:
            df = pd.DataFrame(farmers)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
            df["language"] = df["language"].map(
                {"te": "Telugu", "hi": "Hindi", "en": "English"}
            ).fillna(df["language"])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Farmer detail
            st.divider()
            st.subheader("Farmer Query History")
            phone = st.text_input("Enter phone number (e.g., 919876543210)")
            if phone:
                queries = api_get(f"/api/farmers/{phone}/queries")
                if queries:
                    qdf = pd.DataFrame(queries)
                    st.dataframe(qdf, use_container_width=True, hide_index=True)
                elif queries is not None:
                    st.info("No queries found for this farmer")
    else:
        st.info("No farmers registered yet")

# --- Query Logs Page ---
elif page == "💬 Query Logs":
    st.title("💬 Query Logs")

    stats = api_get("/api/analytics/dashboard")
    if stats and stats["recent_queries"]:
        df = pd.DataFrame(stats["recent_queries"])
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            lang_filter = st.selectbox("Language", ["All", "te", "hi", "en"])
        with col2:
            intent_filter = st.selectbox(
                "Intent", ["All"] + list(df["intent"].dropna().unique())
            )

        if lang_filter != "All":
            df = df[df["language"] == lang_filter]
        if intent_filter != "All":
            df = df[df["intent"] == intent_filter]

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No query logs yet")

# --- Broadcast Page ---
elif page == "📡 Broadcast":
    st.title("📡 Broadcast Message")
    st.warning("⚠️ This will send a WhatsApp message to all matching farmers.")

    with st.form("broadcast_form"):
        message = st.text_area("Message", height=150, placeholder="Type your broadcast message...")
        col1, col2, col3 = st.columns(3)
        with col1:
            language = st.selectbox("Language Filter", [None, "te", "hi", "en"])
        with col2:
            state = st.text_input("State Filter", placeholder="e.g., Telangana")
        with col3:
            crop = st.text_input("Crop Filter", placeholder="e.g., Rice")

        submitted = st.form_submit_button("🚀 Send Broadcast")

        if submitted and message:
            payload = {"message": message}
            if language:
                payload["language"] = language
            if state:
                payload["state"] = state
            if crop:
                payload["crop"] = crop

            result = api_post("/api/broadcast", payload)
            if result:
                st.success(f"✅ Sent: {result['sent']} | Failed: {result['failed']}")

# --- Test Advisory Page ---
elif page == "🧪 Test Advisory":
    st.title("🧪 Test Advisory")
    st.markdown("Test the AI advisory pipeline without WhatsApp.")

    with st.form("advisory_form"):
        query = st.text_area(
            "Farmer Query",
            height=100,
            placeholder="e.g., నా వరి పంటలో ఆకులు పసుపు రంగుకు మారుతున్నాయి",
        )
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox("Language", [None, "te", "hi", "en"])
            district = st.text_input("District", value="Warangal")
        with col2:
            state = st.text_input("State", value="Telangana")
            crops = st.text_input("Crops (comma-separated)", value="Rice")

        submitted = st.form_submit_button("🔍 Get Advisory")

        if submitted and query:
            payload = {
                "query": query,
                "district": district,
                "state": state,
                "crops": [c.strip() for c in crops.split(",") if c.strip()],
            }
            if language:
                payload["language"] = language

            with st.spinner("🌾 Getting advisory from Ollama..."):
                result = api_post("/api/advisory/query", payload)

            if result:
                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric("Language", result["language_detected"])
                col2.metric("Intent", result["intent"])
                col3.metric("KB Matches", result["kb_matches"])

                st.subheader("AI Response")
                st.markdown(result["response"])

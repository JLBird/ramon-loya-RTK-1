"""
RTK-1 Self-Service Portal — Streamlit UI.
Customers initiate campaigns, view ASR trends, download reports.
Run with: streamlit run streamlit_app.py
"""

import pandas as pd
import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="RTK-1 AI Red Teaming",
    page_icon="🛡️",
    layout="wide",
)

# Header
st.title("🛡️ RTK-1 AI Red Teaming Platform")
st.caption("Autonomous adversarial testing • EU AI Act compliance • 24/7 protection")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select",
        ["🚀 Run Campaign", "📊 ASR Trends", "📋 History", "📦 Delivery Bundle"],
    )
    st.divider()
    st.caption("RTK-1 v0.3.0")
    st.caption("Claude Sonnet 4.6 + LangGraph")

# ========================
# PAGE 1: RUN CAMPAIGN
# ========================
if page == "🚀 Run Campaign":
    st.header("Launch Red Team Campaign")

    col1, col2 = st.columns(2)

    with col1:
        target_model = st.text_input(
            "Target Model",
            value="claude-sonnet-4-6",
            help="The model or endpoint you want to red team",
        )
        goal = st.text_area(
            "Attack Goal",
            value="Test for prompt injection vulnerabilities in a customer support chatbot",
            height=100,
        )

    with col2:
        attack_type = st.selectbox(
            "Attack Type",
            ["crescendo", "single-turn", "tap", "agent-tool-calling"],
        )
        customer_success_metrics = st.text_area(
            "Customer Success Metrics",
            value="Demonstrate resilience to multi-turn prompt injection. Success means ASR below 20%.",
            height=100,
        )

    customer_id = st.text_input("Customer ID", value="default")

    st.divider()

    if st.button("🚀 Launch Campaign", type="primary", use_container_width=True):
        with st.spinner(
            "Running red team campaign... This takes 3-25 minutes depending on configuration."
        ):
            try:
                response = requests.post(
                    f"{API_BASE}/redteam/crescendo-with-report",
                    json={
                        "target_model": target_model,
                        "goal": goal,
                        "attack_type": attack_type,
                        "customer_success_metrics": customer_success_metrics,
                    },
                    params={"customer_id": customer_id},
                    timeout=1800,
                )

                if response.status_code == 200:
                    result = response.json()
                    asr = result.get("asr", 0)

                    st.success(f"Campaign completed — ASR: {asr}%")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Attack Success Rate", f"{asr}%")
                    with col2:
                        st.metric("Sequences Run", result.get("sequences_run", 0))
                    with col3:
                        st.metric("Status", result.get("status", "completed"))

                    st.divider()

                    if result.get("report_link"):
                        st.markdown(
                            f"📄 **[Download PDF Report]({result['report_link']})**"
                        )
                    if result.get("grafana_link"):
                        st.markdown(
                            f"📊 **[Open Grafana Dashboard]({result['grafana_link']})**"
                        )

                    with st.expander("View Report Markdown"):
                        st.markdown(result.get("final_report_markdown", ""))

                    st.session_state["last_job_id"] = result.get("job_id")
                    st.session_state["last_asr"] = asr
                    st.session_state["last_sequences"] = result.get("sequences_run", 0)
                    st.session_state["last_target"] = target_model
                    st.session_state["last_goal"] = goal
                    st.session_state["last_metrics"] = customer_success_metrics

                elif response.status_code == 429:
                    st.error(
                        "Rate limit exceeded. Please wait before running another campaign."
                    )
                else:
                    st.error(f"Campaign failed: {response.text}")

            except requests.exceptions.Timeout:
                st.error(
                    "Request timed out. Campaign may still be running — check History."
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ========================
# PAGE 2: ASR TRENDS
# ========================
elif page == "📊 ASR Trends":
    st.header("ASR Trend Analysis")

    target_model = st.text_input("Target Model", value="claude-sonnet-4-6")
    days = st.slider("Days to show", min_value=7, max_value=90, value=30)

    if st.button("Load Trends"):
        try:
            response = requests.get(
                f"{API_BASE}/redteam/trend/{target_model}",
                params={"days": days},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                trend = data.get("trend", [])
                delta = data.get("delta", {})

                if trend:
                    df = pd.DataFrame(trend)
                    df["completed_at"] = pd.to_datetime(df["completed_at"])
                    df = df.sort_values("completed_at")

                    st.line_chart(df.set_index("completed_at")["asr"])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Current ASR",
                            f"{delta.get('current_asr', 0)}%",
                            delta=f"{delta.get('delta', 0):+.1f}%",
                        )
                    with col2:
                        st.info(delta.get("framing", "No trend data"))

                    st.caption(delta.get("business_value", ""))
                    st.dataframe(
                        df[["completed_at", "asr", "robustness_rating", "git_commit"]]
                    )
                else:
                    st.info("No campaign data found for this model and time range.")
        except Exception as e:
            st.error(f"Error loading trends: {str(e)}")

# ========================
# PAGE 3: HISTORY
# ========================
elif page == "📋 History":
    st.header("Campaign History")

    limit = st.slider("Number of campaigns", 5, 50, 20)

    if st.button("Load History"):
        try:
            response = requests.get(
                f"{API_BASE}/redteam/history",
                params={"limit": limit},
                timeout=10,
            )
            if response.status_code == 200:
                campaigns = response.json()
                if campaigns:
                    df = pd.DataFrame(campaigns)
                    st.dataframe(
                        df,
                        column_config={
                            "asr": st.column_config.ProgressColumn(
                                "ASR %", min_value=0, max_value=100
                            ),
                        },
                        use_container_width=True,
                    )
                else:
                    st.info("No campaign history found.")
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")

# ========================
# PAGE 4: DELIVERY BUNDLE
# ========================
elif page == "📦 Delivery Bundle":
    st.header("One-Click Delivery Bundle")
    st.caption("Generate all client-facing content from the last campaign.")

    job_id = st.text_input(
        "Job ID",
        value=st.session_state.get("last_job_id", ""),
    )
    asr = st.number_input(
        "ASR %",
        value=float(st.session_state.get("last_asr", 0.0)),
        min_value=0.0,
        max_value=100.0,
    )
    total_sequences = st.number_input(
        "Total Sequences",
        value=int(st.session_state.get("last_sequences", 3)),
        min_value=1,
    )
    target_model = st.text_input(
        "Target Model",
        value=st.session_state.get("last_target", "claude-sonnet-4-6"),
    )
    goal = st.text_area(
        "Goal",
        value=st.session_state.get("last_goal", ""),
    )
    customer_success_metrics = st.text_area(
        "Customer Success Metrics",
        value=st.session_state.get("last_metrics", ""),
    )
    recipient_name = st.text_input("Recipient Name", value="Team")

    if st.button(
        "📦 Generate Delivery Bundle", type="primary", use_container_width=True
    ):
        if not job_id:
            st.error("Job ID is required. Run a campaign first.")
        else:
            try:
                response = requests.post(
                    f"{API_BASE}/redteam/delivery-bundle",
                    json={
                        "target_model": target_model,
                        "goal": goal,
                        "attack_type": "crescendo",
                        "customer_success_metrics": customer_success_metrics,
                    },
                    params={
                        "job_id": job_id,
                        "asr": asr,
                        "total_sequences": total_sequences,
                        "recipient_name": recipient_name,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    bundle = response.json()
                    st.success("Delivery bundle generated!")

                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "💼 Business Value",
                        "📧 Executive Email",
                        "📊 Slide Deck",
                        "💼 LinkedIn Post",
                        "📋 Weekly Summary",
                    ])

                    with tab1:
                        st.text_area(
                            "Business Value Statement",
                            value=bundle.get("business_value_statement", ""),
                            height=300,
                        )

                    with tab2:
                        email = bundle.get("executive_email", {})
                        st.text_input("Subject", value=email.get("subject", ""))
                        st.text_area("Body", value=email.get("body", ""), height=400)

                    with tab3:
                        deck = bundle.get("slide_deck", {})
                        st.subheader(deck.get("deck_title", ""))
                        for slide in deck.get("slides", []):
                            with st.expander(
                                f"Slide {slide['number']}: {slide['title']}"
                            ):
                                st.markdown(f"**{slide['headline']}**")
                                for bullet in slide.get("bullets", []):
                                    if bullet:
                                        st.markdown(f"- {bullet}")

                    with tab4:
                        st.text_area(
                            "LinkedIn Post",
                            value=bundle.get("linkedin_post", ""),
                            height=300,
                        )

                    with tab5:
                        st.markdown(bundle.get("weekly_summary", ""))

                else:
                    st.error(f"Failed: {response.text}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="PCI DSS Security Dashboard", layout="wide")

st.title("🛡️ PCI DSS Compliance Dashboard")
st.markdown("Automated scan results for Credit Card Data Discovery.")

@st.cache_data(ttl=60)
def load_data():
    try:
        conn = sqlite3.connect("outputs/findings.db")
        df = pd.read_sql_query("SELECT * FROM findings", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No findings database found or database is empty. Please run `python main.py` and `python create_db.py` first.")
else:
    # Top Level Metrics
    total_findings = len(df)
    critical_count = len(df[df["risk_level"] == "Critical"])
    high_count = len(df[df["risk_level"] == "High"])
    medium_count = len(df[df["risk_level"] == "Medium"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Findings", total_findings)
    col2.metric("Critical Risk", critical_count)
    col3.metric("High Risk", high_count)
    col4.metric("Medium Risk", medium_count)

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Detailed Context", "📄 Executive Report"])

    with tab1:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Risk Distribution")
            risk_counts = df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            
            # Color mapping tailored for severity
            color_discrete_map = {
                "Critical": "#FF4B4B",
                "High": "#FFA421",
                "Medium": "#FFD166",
                "Low": "#06D6A0",
                "False Positive": "#118AB2"
            }
            
            fig = px.pie(risk_counts, values="Count", names="Risk Level", 
                        color="Risk Level", color_discrete_map=color_discrete_map, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Results Table")
            
            # Add basic filtering
            search_file = st.text_input("Search by File Path")
            filter_risk = st.multiselect("Filter by Risk Level", df["risk_level"].unique(), default=df["risk_level"].unique())
            
            filtered_df = df[df["risk_level"].isin(filter_risk)]
            if search_file:
                filtered_df = filtered_df[filtered_df["file"].str.contains(search_file, case=False)]
                
            st.dataframe(
                filtered_df[["file", "card_number", "risk_level", "remediated", "scan_date"]],
                use_container_width=True,
                hide_index=True
            )
            
    with tab2:
        st.subheader("AI Analysis per Finding")
        st.markdown("Deep dive into the LLM's reasoning for risk and security conditions.")
        
        for index, row in df.iterrows():
            with st.expander(f"📁 **{row['file']}** | Risk: {row['risk_level']}"):
                st.markdown(f"**Card Number:** `{row['card_number']}`")
                st.markdown("**AI Context Analysis:**")
                st.info(row.get("context_analysis", "No context provided."))
                
    with tab3:
        st.subheader("Compliance Report")
        try:
            with open("outputs/report.txt", "r") as f:
                report_content = f.read()
            st.markdown(report_content)
        except Exception as e:
            st.error("Report could not be loaded. Please ensure the main AI scan has generated `outputs/report.txt`.")


import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import re

st.set_page_config(page_title="PCI DSS Security Dashboard", layout="wide")

st.title("PCI DSS Compliance Dashboard")
st.markdown("Autonomous Credit Card Data Discovery & Remediation System")

@st.cache_data(ttl=60)
def load_data():
    try:
        conn = sqlite3.connect("outputs/findings.db")
        df = pd.read_sql_query("SELECT * FROM findings", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def clean_context_analysis(text):
    """Clean up context analysis by removing unwanted parts"""
    if not text:
        return "No context analysis available"
    
    # Remove "Finding X:" patterns
    text = re.sub(r'Finding \d+:.*?\n', '', text)
    text = re.sub(r'\*\*Finding \d+.*?\*\*', '', text)
    
    # Remove JSON blocks
    text = re.sub(r'\{[^}]*"file_type"[^}]*\}', '', text)
    text = re.sub(r'```json[\s\S]*?```', '', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Remove "Here's my answer in JSON format:" and similar
    text = re.sub(r'Here[\s\S]*?JSON format:?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Here is my answer[\s\S]*?:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'My answer in JSON format:?', '', text, flags=re.IGNORECASE)
    
    # Remove "Explanation:" headers
    text = re.sub(r'Explanation:', '**Analysis:**', text)
    
    # Remove "File Type:" and "Security Status:" lines completely including the bold markers
    text = re.sub(r'\*\*File Type\*\*:.*?\n', '', text)
    text = re.sub(r'\*\*Security Status\*\*:.*?\n', '', text)
    
    # Remove any leftover empty bold markers
    text = re.sub(r'\*\* \*\*', '', text)
    text = re.sub(r'\*\*\s*\*\*', '', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

df = load_data()

# Create tabs
col1, col2, col3 = st.columns(3)

# Tab names and their indices
tabs = ["Overview", "Detailed Context", "Executive Report"]

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

for i, (col, tab_name) in enumerate(zip([col1, col2, col3], tabs)):
    with col:
        is_active = st.session_state.active_tab == i
        button_type = "primary" if is_active else "secondary"
        
        if st.button(tab_name, use_container_width=True, key=f"tab_{i}", type=button_type):
            st.session_state.active_tab = i
            st.rerun()

st.markdown("---")

if df.empty:
    if st.session_state.active_tab == 0:
        st.warning("No findings database found. Please run `python main.py` and `python create_db.py` first.")
    elif st.session_state.active_tab == 1:
        st.info("No data available. Please run a scan first to see detailed analysis.")
    elif st.session_state.active_tab == 2:
        st.info("No report available. Please run a scan first to generate the executive report.")
else:
    # Top Level Metrics
    total_findings = len(df)
    critical_count = len(df[df["risk_level"] == "Critical"])
    high_count = len(df[df["risk_level"] == "High"])
    medium_count = len(df[df["risk_level"] == "Medium"])
    low_count = len(df[df["risk_level"] == "Low"])
    
    # Remediation metrics
    if "remediation" in df.columns:
        remediated_count = len(df[df["remediation"].str.contains("Masked and saved", na=False)])
    else:
        remediated_count = 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Findings", total_findings)
    col2.metric("Critical Risk", critical_count)
    col3.metric("High Risk", high_count)
    col4.metric("Medium Risk", medium_count)
    col5.metric("Low Risk", low_count)
    col6.metric("Remediated", remediated_count)

    st.markdown("---")

    if st.session_state.active_tab == 0:
        # Risk Distribution Chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Distribution")
            risk_counts = df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            
            color_discrete_map = {
                "Critical": "#FF4B4B",
                "High": "#FFA421", 
                "Medium": "#FFD166",
                "Low": "#06D6A0"
            }
            
            fig = px.pie(risk_counts, values="Count", names="Risk Level", 
                        color="Risk Level", color_discrete_map=color_discrete_map, hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Top File Extensions with Findings")
            # Extract file extensions
            df['extension'] = df['file'].str.extract(r'\.([^.]+)$')
            df['extension'] = df['extension'].fillna('no extension')
            
            ext_counts = df['extension'].value_counts().head(8).reset_index()
            ext_counts.columns = ['Extension', 'Count']
            
            fig2 = px.bar(ext_counts, x='Extension', y='Count', 
                         color='Count', color_continuous_scale='Viridis')
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Sources Chart
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Sources")
            df['source'] = df['file'].apply(lambda x: 'Cloud Files' if x.startswith('gdrive://') else 'Local Files')
            source_counts = df['source'].value_counts().reset_index()
            source_counts.columns = ['Source', 'Count']
            
            fig3 = px.bar(source_counts, x='Source', y='Count', 
                         color='Source', color_discrete_map={'Local Files': '#1f77b4', 'Cloud Files': '#ff7f0e'})
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("File Type Risk Analysis")
            # Categorize file types
            def categorize_file_type(file_path):
                file_lower = file_path.lower()
                if 'config' in file_lower or file_lower.endswith(('.env', '.ini', '.conf')):
                    return 'Configuration Files'
                elif 'log' in file_lower:
                    return 'Log Files'
                elif 'backup' in file_lower or file_lower.endswith('.sql'):
                    return 'Backup Files'
                elif file_lower.endswith(('.csv', '.json', '.xml')):
                    return 'Data Files'
                else:
                    return 'Other Files'
            
            df['file_type'] = df['file'].apply(categorize_file_type)
            
            # Create risk breakdown by file type
            file_type_risk = df.groupby(['file_type', 'risk_level']).size().reset_index(name='count')
            
            fig4 = px.bar(file_type_risk, x='file_type', y='count', color='risk_level',
                         color_discrete_map=color_discrete_map,
                         title="Risk Distribution by File Type")
            fig4.update_layout(xaxis_title="File Type", yaxis_title="Number of Findings")
            st.plotly_chart(fig4, use_container_width=True)

        # Results Table
        st.subheader("Findings Summary")
        search_file = st.text_input("Search by File Path")
        filter_risk = st.multiselect("Filter by Risk Level", df["risk_level"].unique(), default=df["risk_level"].unique())
        
        filtered_df = df[df["risk_level"].isin(filter_risk)]
        if search_file:
            filtered_df = filtered_df[filtered_df["file"].str.contains(search_file, case=False)]
            
        # Display summary table
        display_df = filtered_df[["file", "card_number", "risk_level"]].copy()
        if "remediation" in filtered_df.columns:
            display_df["remediation_status"] = filtered_df["remediation"].apply(
                lambda x: "Remediated" if "Masked and saved" in str(x) else "Not remediated"
            )
        display_df["card_number"] = display_df["card_number"].apply(lambda x: f"{x[:4]}****{x[-4:]}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    elif st.session_state.active_tab == 1:
        st.subheader("AI Analysis per Finding")
        st.markdown("Deep dive into the LLM's reasoning for risk and security conditions.")
        
        # Sidebar filters for detailed context
        with st.sidebar:
            st.header("Filters")
            risk_filter = st.multiselect("Risk Level", df["risk_level"].unique(), default=df["risk_level"].unique())
            source_filter = st.multiselect("Source", ["Local", "Cloud"], default=["Local", "Cloud"])
        
        # Apply filters
        filtered_df = df[df["risk_level"].isin(risk_filter)]
        if "Local" not in source_filter:
            filtered_df = filtered_df[filtered_df["file"].str.startswith("gdrive://")]
        if "Cloud" not in source_filter:
            filtered_df = filtered_df[~filtered_df["file"].str.startswith("gdrive://")]
        
        for index, row in filtered_df.iterrows():
            with st.expander(f"{row['file']} | Risk: {row['risk_level']}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**Card Number:** {row['card_number'][:4]}****{row['card_number'][-4:]}")
                    st.markdown(f"**Risk Level:** {row['risk_level']}")
                    st.markdown(f"**Source:** {'Cloud' if row['file'].startswith('gdrive://') else 'Local'}")
                    if 'remediation' in row and row['remediation']:
                        if "Masked and saved" in str(row['remediation']):
                            st.markdown("**Status:** Remediated")
                        else:
                            st.markdown("**Status:** Not Remediated")
                
                with col2:
                    st.markdown("**AI Context Analysis:**")
                    cleaned_analysis = clean_context_analysis(row.get("context_analysis", ""))
                    st.markdown(cleaned_analysis)
                    
                    if 'remediation' in row and row['remediation'] and "Masked and saved" in str(row['remediation']):
                        st.markdown("**Remediation:**")
                        st.success(row['remediation'])
    elif st.session_state.active_tab == 2:
        st.subheader("Executive Compliance Report")
        try:
            with open("outputs/report.txt", "r", encoding='utf-8') as f:
                report_content = f.read()
            
            # Remove the overview section from executive report since it's now in Overview tab
            lines = report_content.split('\n')
            filtered_lines = []
            skip_section = False
            
            for line in lines:
                if line.strip().startswith('## Overview'):
                    skip_section = True
                elif line.strip().startswith('## Detailed Findings'):
                    break
                elif line.strip().startswith('---') and skip_section:
                    skip_section = False
                    continue
                elif not skip_section:
                    filtered_lines.append(line)
            
            cleaned_report = '\n'.join(filtered_lines)
            st.markdown(cleaned_report)
            
        except Exception as e:
            st.error("Report could not be loaded. Please run a scan first to generate the executive report.")

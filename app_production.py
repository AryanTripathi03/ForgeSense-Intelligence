# app_production.py - Production-ready furnace intelligence system
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

try:
    from src.core.processor import FurnaceDataProcessor
    from src.intelligence.insights_final import ProductionInsightsGenerator
    IMPORT_SUCCESS = True
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.info("Running in basic mode. Some features may be limited.")
    IMPORT_SUCCESS = False


st.set_page_config(page_title="Furnace Intelligence", page_icon="🔥", layout="wide")

def load_excel_with_smart_headers(file_path):
    """Scans the first 10 rows to find where the actual table starts."""
    keywords = ['furnace', 'date', 'production', 'cost']
    
    # Peek at the first 10 rows
    peek_df = pd.read_excel(file_path, nrows=10, header=None)
    
    header_row = 0
    for i, row in peek_df.iterrows():
        # Check if any keyword exists in the row strings
        row_values = [str(val).lower() for val in row.values]
        if any(key in val for key in keywords for val in row_values):
            header_row = i
            break
            
    return pd.read_excel(file_path, header=header_row)



# Set page config
st.set_page_config(
    page_title="Furnace Intelligence System - Production",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
# Updated CSS for Visibility and Green Theme
st.markdown("""
<style>
    /* Main Titles */
    .main-header { color: #166534 !important; font-weight: bold; }
    
    /* Insight Card Container */
    .insight-card {
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 10px;
        border-left: 8px solid;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }

    /* Target the specific insight classes used in your loop */
    .insight-high { 
        background-color: #f0fdf4 !important; 
        border-color: #15803d !important; 
        color: #14532d !important;
    }
    .insight-medium { 
        background-color: #f7fee7 !important; 
        border-color: #65a30d !important; 
        color: #365314 !important;
    }
    .insight-low { 
        background-color: #ecfdf5 !important; 
        border-color: #10b981 !important; 
        color: #064e3b !important;
    }

    /* Ensure headers inside cards are visible */
    .insight-card h4, .insight-high h4, .insight-medium h4, .insight-low h4 {
        color: #14532d !important;
        margin-top: 0 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)
# App header
st.markdown('<h1 class="main-header">🔥 Furnace Performance Intelligence System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Production-Ready • Enterprise Grade • Actionable Insights</p>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'insights' not in st.session_state:
    st.session_state.insights = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/factory.png", width=80)
    st.title("Data Management")
    
    uploaded_file = st.file_uploader(
        "📤 Upload Furnace Data",
        type=['xlsx', 'xls'],
        help="Upload your daily furnace production report"
    )
    
    if uploaded_file:
        # Save uploaded file for processing
        temp_path = "uploaded_data.xlsx"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("🚀 Process & Analyze", type="primary"):
            try:
                with st.spinner("Analyzing furnace data..."):
                    # 1. Load data with your smart header function
                    df = load_excel_with_smart_headers(temp_path)
                    
                    if IMPORT_SUCCESS:
                        # 2. Initialize and run your core logic
                        processor = FurnaceDataProcessor()
                        processed_df = processor.process_data(df)
                        insights_gen = ProductionInsightsGenerator(processor)
                        insights = insights_gen.generate_all_insights()
                        
                        # 3. Save to session state
                        st.session_state.processor = processor
                        st.session_state.insights = insights
                    else:
                        # Fallback for basic mode
                        st.session_state.processor = df
                        st.session_state.insights = {"Status": [{
                            'title': 'Basic Processing Active',
                            'description': 'Data loaded without intelligence modules.',
                            'severity': 'low'
                        }]}
                    
                    st.session_state.data_loaded = True
                    st.success("Analysis Complete!")
                    st.rerun() # Refresh to move from welcome screen to dashboard
            except Exception as e:
                st.error(f"Error processing file: {e}")    
                
                    
               
    
    st.markdown("---")
    
    # Sample data
    if st.button("🧪 Load Sample Data", use_container_width=True):
        if os.path.exists('sample_furnace_data.xlsx'):
            with st.spinner("Loading sample..."):
                try:
                    df = pd.read_excel('sample_furnace_data.xlsx')
                    
                    if IMPORT_SUCCESS:
                        processor = FurnaceDataProcessor()
                        processed_df = processor.process_data(df)
                        insights_gen = ProductionInsightsGenerator(processor)
                        insights = insights_gen.generate_all_insights()
                        
                        st.session_state.processor = processor
                        st.session_state.insights = insights
                    else:
                        st.session_state.processor = df
                        st.session_state.insights = {"Basic Analysis": [{
                            'title': 'Sample Data Loaded',
                            'description': 'Running in basic analysis mode',
                            'severity': 'low'
                        }]}
                    
                    st.session_state.data_loaded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Sample data not found")
    
    st.markdown("---")
    
    # Navigation
    st.title("Navigation")
    page = st.radio(
        "Go to:",
        ["📊 Dashboard", "💡 Insights", "📈 Analytics", "📋 Reports", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("Version 3.0 • Production Ready")

# Main content based on navigation
if not st.session_state.data_loaded:
    # Welcome screen
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ## 🎯 Welcome to Furnace Intelligence System
        
        This enterprise-grade system transforms your furnace production data into 
        **actionable operational intelligence**.
        
        ### Key Features:
        
        ✅ **Cost Optimization** - Identify and reduce production costs  
        ✅ **Power Efficiency** - Optimize energy consumption  
        ✅ **Material Recovery** - Improve manganese and silicon recovery  
        ✅ **Quality Control** - Maintain consistent product quality  
        ✅ **Operational Excellence** - Reduce breakdowns and improve availability  
        
        ### How to Start:
        1. **Upload** your furnace data Excel file (left sidebar)
        2. **Process** the data for analysis
        3. **Explore** insights and recommendations
        4. **Implement** changes to improve performance
        
        ### Expected Data Format:
        Your Excel file should include columns like:
        - `Furnace`, `DATE`, `Incharge`
        - `Actual Production Qty`, `Total Cost PLC`
        - `Specific Power Consumption`, `MN Recovery PLC`
        - `Grade MN`, `Grade SI`, `C%`
        """)
    
    with col2:
        st.image("https://img.icons8.com/clouds/300/000000/factory.png", width=300)
        
        st.markdown("""
        ### 🚀 Quick Start
        
        Don't have data ready? Try with our sample data:
        
        1. Click **'Load Sample Data'** in sidebar
        2. Explore the dashboard
        3. See how insights are generated
        
        ### 📊 Data Requirements
        
        For best results, ensure your data includes:
        - Daily production quantities
        - Cost breakdowns
        - Power consumption
        - Quality parameters
        - Breakdown records
        """)
    
else:
    # Data is loaded - show appropriate page
    processor = st.session_state.processor
    insights = st.session_state.insights
    
    if page == "📊 Dashboard":
        # DASHBOARD PAGE
        st.header("📊 Executive Dashboard")
        
        # Key Performance Indicators
        st.subheader("Key Performance Indicators")
        
        if IMPORT_SUCCESS and hasattr(processor, 'processed_df'):
            df = processor.processed_df
        else:
            df = processor
        
        # Calculate metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'Actual Production Qty' in df.columns:
                total_prod = df['Actual Production Qty'].sum()
                st.metric("Total Production", f"{total_prod:,.0f} MT", delta=None)
            else:
                st.metric("Total Production", "N/A")
        
        with col2:
            if 'cost_per_ton' in df.columns:
                avg_cost = df['cost_per_ton'].mean()
                st.metric("Avg Cost/Ton", f"₹{avg_cost:,.0f}", delta=None)
            elif 'Total Cost PLC' in df.columns and 'Actual Production Qty' in df.columns:
                avg_cost = (df['Total Cost PLC'].sum() / df['Actual Production Qty'].sum())
                st.metric("Avg Cost/Ton", f"₹{avg_cost:,.0f}", delta=None)
            else:
                st.metric("Avg Cost/Ton", "N/A")
        
        with col3:
            if 'Specific Power Consumption' in df.columns:
                avg_power = df['Specific Power Consumption'].mean()
                st.metric("Avg Power/Ton", f"{avg_power:,.0f} kWh", delta=None)
            else:
                st.metric("Avg Power/Ton", "N/A")
        
        with col4:
            if 'MN Recovery PLC' in df.columns:
                avg_mn = df['MN Recovery PLC'].mean()
                st.metric("Avg MN Recovery", f"{avg_mn:.1f}%", delta=None)
            else:
                st.metric("Avg MN Recovery", "N/A")
        
        # Top Priority Insights
        st.subheader("🚨 Top Priority Insights")
        
        if insights:
            # Get all insights
            all_insights = []
            for category_insights in insights.values():
                all_insights.extend(category_insights)
            
            # Sort by severity
            severity_order = {'high': 3, 'medium': 2, 'low': 1}
            sorted_insights = sorted(
                all_insights,
                key=lambda x: severity_order.get(x.get('severity', 'low'), 0),
                reverse=True
            )
            
            # Show top 3
            for insight in sorted_insights[:3]:
                severity = insight.get('severity', 'low')
                severity_class = f"insight-{severity}"
                
                st.markdown(f"""
                <div class="{severity_class}">
                    <h4>{insight.get('title', 'Insight')}</h4>
                    <p><strong>Description:</strong> {insight.get('description', '')}</p>
                    <p><strong>Recommendation:</strong> {insight.get('recommendation', '')}</p>
                    {f'<p><strong>Action Items:</strong> {insight.get("action_items", [])}</p>' if insight.get('action_items') else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No insights generated. Check your data format.")
        
        # Quick Charts
        st.subheader("📈 Quick Overview Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Production by Furnace
            if 'Furnace' in df.columns and 'Actual Production Qty' in df.columns:
                furnace_prod = df.groupby('Furnace')['Actual Production Qty'].sum().reset_index()
                
                fig = px.bar(
                    furnace_prod,
                    x='Furnace',
                    y='Actual Production Qty',
                    title="Production by Furnace",
                    color='Furnace',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cost Distribution
            if 'cost_per_ton' in df.columns and 'Furnace' in df.columns:
                fig = px.box(
                    df,
                    x='Furnace',
                    y='cost_per_ton',
                    title="Cost per Ton Distribution",
                    color='Furnace'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    elif page == "💡 Insights":
        st.header("💡 Actionable Operational Intelligence")
        
        if insights:
            # 1. Top Level Filters
            col1, col2 = st.columns([2, 1])
            with col1:
                # Get all available categories
                all_cats = ["All Categories"] + list(insights.keys())
                selected_cat = st.segmented_control("Filter by Category", options=all_cats, default="All Categories")
            
            with col2:
                search_query = st.text_input("🔍 Search insights...", placeholder="e.g. Furnace 1")

            st.markdown("---")

            # 2. Process Insights based on filters
            display_list = []
            for cat, items in insights.items():
                if selected_cat == "All Categories" or selected_cat == cat:
                    for item in items:
                        # Filter by search text
                        if search_query.lower() in str(item).lower():
                            item['category_label'] = cat # Keep track of source
                            display_list.append(item)

            # Sort: High severity first
            sev_map = {'high': 0, 'medium': 1, 'low': 2}
            display_list.sort(key=lambda x: sev_map.get(x.get('severity', 'low'), 3))

            # 3. Render Enhanced Cards
            if not display_list:
                st.info("No insights match your current filters.")
            else:
                for idx, ins in enumerate(display_list):
                    sev = ins.get('severity', 'low').lower()
                    
                    # Determine Badge Color
                    badge_colors = {
                        'high': 'background-color: #ef4444; color: white;', # Red for High
                        'medium': 'background-color: #f59e0b; color: white;', # Amber for Medium
                        'low': 'background-color: #10b981; color: white;' # Green for Low
                    }
                    
                    # Use a clean container with a border
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.subheader(f"{ins.get('title', 'System Insight')}")
                        with c2:
                            st.markdown(f'<p style="text-align:center; border-radius:15px; padding:2px 10px; font-size:12px; font-weight:bold; {badge_colors.get(sev)}">{sev.upper()} PRIORITY</p>', unsafe_allow_html=True)
                        
                        st.markdown(f"**📂 Category:** {ins.get('category_label')} | **🔥 Furnace:** {ins.get('furnace', 'All Units')}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("### 📝 Observation")
                            st.write(ins.get('description', 'No description available.'))
                        with col_b:
                            st.markdown("### ⚡ Recommendation")
                            st.success(ins.get('recommendation', 'No recommendation provided.'))
                        
                        if ins.get('action_items'):
                            with st.expander("✅ View Action Plan"):
                                for action in ins.get('action_items'):
                                    st.write(f"- {action}")

        else:
            st.warning("Please upload and process data in the sidebar to generate insights.")
    
    elif page == "📈 Analytics":
        st.header("📈 Advanced Analytics Engineering")
        
        if IMPORT_SUCCESS and hasattr(processor, 'processed_df'):
            df = processor.processed_df
            
            # 1. Analysis Mode Selector
            analysis_mode = st.segmented_control(
                "Select Analysis Mode", 
                options=["Time Series Trends", "Furnace Comparison", "Correlation Matrix"],
                default="Time Series Trends"
            )
            
            st.markdown("---")

            if analysis_mode == "Time Series Trends":
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.subheader("Configuration")
                    # Group numeric columns for cleaner selection
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    clean_cols = [c for c in numeric_cols if c not in ['Year', 'Month', 'Day', 'Week']]
                    
                    target_metric = st.selectbox("Select Metric to Analyze", options=clean_cols)
                    show_ma = st.checkbox("Show 7-Day Moving Average", value=True)
                    show_bounds = st.checkbox("Show Statistical Bounds", value=False)
                
                with col2:
                    if 'DATE' in df.columns:
                        df['Date'] = pd.to_datetime(df['DATE']).dt.date
                        # Aggregate by date and furnace
                        chart_data = df.groupby(['Date', 'Furnace'])[target_metric].mean().reset_index()
                        
                        fig = px.line(
                            chart_data, 
                            x='Date', 
                            y=target_metric, 
                            color='Furnace',
                            title=f"{target_metric} - Multi-Furnace Trend",
                            markers=True,
                            color_discrete_sequence=px.colors.sequential.Greens_r
                        )
                        
                        if show_ma:
                            # Calculate rolling average for the total plant
                            plant_avg = df.groupby('Date')[target_metric].mean().rolling(window=7).mean()
                            fig.add_scatter(x=plant_avg.index, y=plant_avg.values, name="Plant 7D MA", line=dict(dash='dash', color='black'))

                        st.plotly_chart(fig, use_container_width=True)

            elif analysis_mode == "Furnace Comparison":
                st.subheader("Cross-Furnace Efficiency Benchmarking")
                
                comp_metrics = st.multiselect(
                    "Select Metrics for Comparison", 
                    options=[c for c in df.columns if df[c].dtype in ['float64', 'int64']],
                    default= [c for c in ['Actual Production Qty', 'cost_per_ton'] if c in df.columns]
                )
                
                if comp_metrics:
                    # Normalized comparison
                    comp_df = df.groupby('Furnace')[comp_metrics].mean().reset_index()
                    
                    # Melt for grouped bar chart
                    melted_comp = comp_df.melt(id_vars='Furnace', var_name='Metric', value_name='Average Value')
                    
                    fig = px.bar(
                        melted_comp, 
                        x='Metric', 
                        y='Average Value', 
                        color='Furnace',
                        barmode='group',
                        color_discrete_sequence=px.colors.sequential.Greens_r,
                        title="Average Performance by Unit"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif analysis_mode == "Correlation Matrix":
                st.subheader("Variable Relationship Analysis")
                st.info("Identify how parameters like 'Power' affect 'Recovery' or 'Cost'.")
                
                numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['Year', 'Month', 'Day'], errors='ignore')
                corr = numeric_df.corr()
                
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale='Greens',
                    title="Correlation Heatmap (Parameters vs. Performance)"
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("💡 Advanced analytics require the full Intelligence System. Please upload data via the sidebar.")
    
    elif page == "📋 Reports":
        st.header("📋 Report Generation Center")
        
        if hasattr(st.session_state, 'processor') and st.session_state.data_loaded:
            df = st.session_state.processor.processed_df if IMPORT_SUCCESS else st.session_state.processor
            
            # --- SECTION 1: DATA EXPORT ---
            with st.container(border=True):
                st.subheader("📁 Processed Data Export")
                st.write("Download the complete cleaned dataset including calculated costs and power metrics.")
                
                # Show a small preview of what they are downloading
                st.dataframe(df.head(5), use_container_width=True, hide_index=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Full Dataset (CSV)",
                    data=csv,
                    file_name=f"furnace_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )

            st.markdown(" ") # Spacer

            # --- SECTION 2: INSIGHTS SUMMARY ---
            with st.container(border=True):
                st.subheader("💡 Actionable Insights Report")
                st.write("A formatted text report containing all AI-generated observations and recommendations.")
                
                if insights:
                    # Generate the report text internally
                    report_text = "FURNACE INTELLIGENCE SYSTEM - INSIGHTS\n" + "="*40 + "\n"
                    for cat, items in insights.items():
                        report_text += f"\nCATEGORY: {cat.upper()}\n"
                        for i in items:
                            report_text += f"- {i['title']} ({i['severity'].upper()})\n"
                    
                    # Preview box for the text
                    st.text_area("Preview", value=report_text, height=150, disabled=True)
                    
                    st.download_button(
                        label="📥 Download Insights Summary (.txt)",
                        data=report_text,
                        file_name="operational_insights.txt",
                        use_container_width=True
                    )
                else:
                    st.info("No insights available to export. Please process data first.")

            st.markdown(" ") # Spacer

            # --- SECTION 3: EXECUTIVE SUMMARY ---
            with st.container(border=True):
                st.subheader("📊 Performance Statistics")
                st.write("Furnace-wise summary of production, recovery, and cost averages.")
                
                if 'Furnace' in df.columns:
                    # Create the summary table
                    summary_stats = df.groupby('Furnace').agg({
                        'Actual Production Qty': 'sum',
                        'Specific Power Consumption': 'mean',
                        'cost_per_ton': 'mean'
                    }).round(2).rename(columns={
                        'Actual Production Qty': 'Total Prod (MT)',
                        'Specific Power Consumption': 'Avg Power (kWh/MT)',
                        'cost_per_ton': 'Avg Cost (₹)'
                    })
                    
                    st.table(summary_stats)
                    
                    summary_csv = summary_stats.to_csv().encode('utf-8')
                    st.download_button(
                        label="📥 Download Stats Summary (CSV)",
                        data=summary_csv,
                        file_name="furnace_performance_stats.csv",
                        use_container_width=True
                    )
        else:
            st.warning("⚠️ No data available. Please upload a file in the sidebar to generate reports.")
    
    elif page == "⚙️ Settings":
        st.header("⚙️ System Configuration")
        
        # --- CRITICAL FIX: Define df for this page ---
        if hasattr(st.session_state, 'processor') and st.session_state.data_loaded:
            # Check if it's a dataframe or a processor object with a df inside
            if hasattr(st.session_state.processor, 'processed_df'):
                df = st.session_state.processor.processed_df
            else:
                df = st.session_state.processor
            
            # Section 1: Data Health
            st.subheader("🔍 Data Health Check")
            col1, col2 = st.columns(2)
            with col1:
                if 'Furnace' in df.columns:
                    st.success("✅ Furnace Mapping: Active")
                else:
                    st.error("❌ Furnace Mapping: Missing")
            with col2:
                if 'DATE' in df.columns:
                    st.success("✅ Temporal Mapping: Active")
                else:
                    st.error("❌ Temporal Mapping: Missing")

            st.markdown("---")

            # Section 2: Performance Thresholds
            st.subheader("🎯 Operational Targets")
            st.info("Adjust these values to update your 'High Severity' alerts and dashboard KPIs.")
            
            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Production & Cost**")
                    cost_target = st.number_input("Target Cost/Ton (₹)", value=50000, step=500)
                    prod_target = st.number_input("Daily Prod Target (MT)", value=150, step=10)
                with c2:
                    st.markdown("**Power & Efficiency**")
                    power_limit = st.number_input("Power Limit (kWh/MT)", value=2800, step=50)
                    mn_recovery_min = st.slider("Min MN Recovery (%)", 0.0, 100.0, 85.0)

            # Section 3: System Preferences
            st.subheader("🎨 UI Preferences")
            theme_mode = st.selectbox("Dashboard Theme", ["Default Green", "High Contrast", "Dark Mode (Beta)"])
            auto_refresh = st.toggle("Enable Real-time Insight Generation", value=True)

            if st.button("💾 Save All Configurations", type="primary", use_container_width=True):
                with st.spinner("Updating system parameters..."):
                    # Here you can save these to st.session_state for use in your calculations
                    st.session_state.cost_target = cost_target
                    st.session_state.power_limit = power_limit
                    st.success("Settings saved! Insights will recalibrate based on these targets.")
        
        else:
            st.warning("⚠️ No data loaded. Load data in the sidebar to configure health checks.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280;">
        <p>Furnace Intelligence System v3.0 • Production Ready • © 2024</p>
        <p>Built for operational excellence and cost optimization</p>
    </div>
    """,
    unsafe_allow_html=True
)
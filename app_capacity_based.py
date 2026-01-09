# app_capacity_based.py - Capacity-based furnace intelligence system
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config - SIMPLE AND CLEAN
st.set_page_config(
    page_title="Furnace Intelligence - Capacity Based",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .insight-critical {
        border-left: 6px solid #EF4444;
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
    }
    .insight-high {
        border-left: 5px solid #F59E0B;
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
    }
    .insight-medium {
        border-left: 4px solid #10B981;
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
    }
    .furnace-tag {
        background: #3B82F6;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .confidence-high {
        color: #10B981;
        font-weight: 600;
    }
    .confidence-medium {
        color: #F59E0B;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-title">🔥 FURNACE PERFORMANCE INTELLIGENCE SYSTEM</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Capacity-Based Analysis • APEX Reduction • Quality Maintenance</p>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'capacity_data' not in st.session_state:
    st.session_state.capacity_data = {}
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'insights' not in st.session_state:
    st.session_state.insights = None

# Sidebar - Data Upload and Capacity Input
with st.sidebar:
    st.markdown("### 📁 DATA UPLOAD")
    
    uploaded_file = st.file_uploader(
        "Upload Furnace Production Data",
        type=['xlsx', 'xls'],
        help="Upload daily furnace production report"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = "temp_furnace_data.xlsx"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load data
        try:
            df = pd.read_excel(temp_path)
            st.session_state.df = df
            
            # Get unique furnaces
            furnace_cols = [col for col in df.columns if 'furnace' in str(col).lower()]
            if furnace_cols:
                furnace_col = furnace_cols[0]
                furnaces = sorted(df[furnace_col].unique())
                
                st.markdown("---")
                st.markdown("### ⚙️ FURNACE CAPACITY SETUP")
                st.info(f"Found {len(furnaces)} furnaces: {', '.join(furnaces)}")
                
                # Capacity input for each furnace
                capacity_data = {}
                for furnace in furnaces:
                    with st.expander(f"Capacity Settings - {furnace}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            mva = st.number_input(
                                f"MVA Capacity",
                                min_value=1.0,
                                max_value=100.0,
                                value=12.5,
                                step=0.5,
                                key=f"mva_{furnace}"
                            )
                            
                            design_capacity = st.number_input(
                                f"Design Capacity (MT/day)",
                                min_value=10.0,
                                max_value=500.0,
                                value=100.0,
                                step=5.0,
                                key=f"design_{furnace}"
                            )
                        
                        with col2:
                            target_cost = st.number_input(
                                f"Target Cost (₹/MT)",
                                min_value=10000.0,
                                max_value=100000.0,
                                value=50000.0,
                                step=1000.0,
                                key=f"cost_{furnace}"
                            )
                            
                            optimal_power = st.number_input(
                                f"Optimal Power (kWh/MT)",
                                min_value=1000.0,
                                max_value=5000.0,
                                value=2500.0,
                                step=100.0,
                                key=f"power_{furnace}"
                            )
                        
                        target_mn = st.slider(
                            f"Target MN Recovery (%)",
                            min_value=50.0,
                            max_value=95.0,
                            value=80.0,
                            step=1.0,
                            key=f"mn_{furnace}"
                        )
                        
                        capacity_data[furnace] = {
                            'mva_capacity': mva,
                            'design_capacity_mt': design_capacity,
                            'target_cost_mt': target_cost,
                            'optimal_power_kwh_mt': optimal_power,
                            'target_mn_recovery': target_mn,
                            'target_si_recovery': 45.0,
                        }
                
                st.session_state.capacity_data = capacity_data
                
                # Process button
                if st.button("🚀 ANALYZE PERFORMANCE", type="primary", use_container_width=True):
                    with st.spinner("🔄 Analyzing with capacity parameters..."):
                        try:
                            # Import and use the capacity-based system
                            try:
                                from src.core.capacity_calculator import CapacityCalculator, FurnaceCapacity
                                from src.intelligence.advanced_insights import AdvancedInsightsEngine
                                
                                # Create capacity objects
                                capacities = {}
                                for furnace_id, cap_data in capacity_data.items():
                                    capacities[furnace_id] = FurnaceCapacity(
                                        furnace_id=furnace_id,
                                        mva_capacity=cap_data['mva_capacity'],
                                        design_capacity_mt=cap_data['design_capacity_mt'],
                                        optimal_power_kwh_mt=cap_data['optimal_power_kwh_mt'],
                                        target_mn_recovery=cap_data['target_mn_recovery'],
                                        target_si_recovery=cap_data['target_si_recovery'],
                                        target_cost_mt=cap_data['target_cost_mt']
                                    )
                                
                                # Clean data
                                df_clean = df.copy()
                                df_clean.columns = [str(col).strip() for col in df_clean.columns]
                                
                                # Convert numeric columns
                                numeric_cols = [
                                    'Actual Production Qty', 'Total Cost PLC', 
                                    'Specific Power Consumption', 'MN Recovery PLC',
                                    'Grade MN', 'Grade SI', 'C%', 'Basicity',
                                    'Total Breakdown Mins', 'Load Factor'
                                ]
                                
                                for col in numeric_cols:
                                    if col in df_clean.columns:
                                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                                
                                # Calculate cost per ton
                                if 'Total Cost PLC' in df_clean.columns and 'Actual Production Qty' in df_clean.columns:
                                    df_clean['cost_per_ton'] = df_clean['Total Cost PLC'] / df_clean['Actual Production Qty']
                                
                                # Create calculator and insights
                                calculator = CapacityCalculator(df_clean, capacities)
                                insights_engine = AdvancedInsightsEngine(calculator, capacity_data)
                                insights = insights_engine.generate_all_insights()
                                
                                st.session_state.processor = calculator
                                st.session_state.insights = insights
                                st.session_state.data_loaded = True
                                
                                st.success("✅ Analysis Complete!")
                                
                            except ImportError:
                                # Fallback to simple analysis
                                st.session_state.processor = df_clean
                                st.session_state.insights = {"Analysis": [{
                                    'title': 'Simple Analysis Complete',
                                    'description': f'Analyzed {len(df_clean)} records',
                                    'severity': 'medium'
                                }]}
                                st.session_state.data_loaded = True
                                st.success("✅ Basic Analysis Complete!")
                            
                        except Exception as e:
                            st.error(f"❌ Analysis Error: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    
    else:
        st.info("👆 Upload your furnace data Excel file to begin")
        
        # Sample data option
        if st.button("🧪 Try with Sample Data", use_container_width=True):
            if os.path.exists('sample_furnace_data.xlsx'):
                with st.spinner("Loading sample..."):
                    try:
                        df = pd.read_excel('sample_furnace_data.xlsx')
                        st.session_state.df = df
                        
                        # Set default capacities for sample
                        capacity_data = {
                            'F1': {'mva_capacity': 12.5, 'design_capacity_mt': 100, 'target_cost_mt': 50000, 'optimal_power_kwh_mt': 2500, 'target_mn_recovery': 80},
                            'F2': {'mva_capacity': 12.5, 'design_capacity_mt': 100, 'target_cost_mt': 50000, 'optimal_power_kwh_mt': 2500, 'target_mn_recovery': 80},
                            'F3': {'mva_capacity': 12.5, 'design_capacity_mt': 100, 'target_cost_mt': 50000, 'optimal_power_kwh_mt': 2500, 'target_mn_recovery': 80},
                            'F4': {'mva_capacity': 12.5, 'design_capacity_mt': 100, 'target_cost_mt': 50000, 'optimal_power_kwh_mt': 2500, 'target_mn_recovery': 80},
                        }
                        
                        st.session_state.capacity_data = capacity_data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Sample data not found")
    
    st.markdown("---")
    st.markdown("### 🎯 SYSTEM FEATURES")
    st.markdown("""
    - **Capacity-Based Analysis**
    - **APEX Cost Reduction**
    - **Quality Standard Maintenance**
    - **Actionable Insights**
    - **Performance Benchmarking**
    """)

# Main Content Area
if not st.session_state.data_loaded:
    # Welcome screen
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 CAPACITY-BASED FURNACE ANALYSIS")
        
        st.markdown("""
        This system analyzes furnace performance **based on actual capacity** to provide:
        
        #### **Key Differentiators:**
        
        ✅ **MVA Capacity-Based Metrics** - Not generic averages  
        ✅ **Design vs Actual Comparison** - True performance measurement  
        ✅ **Target-Based Analysis** - Compare against engineering targets  
        ✅ **APEX Focus** - Reduce cost while maintaining quality  
        ✅ **Actionable Insights** - Specific, implementable recommendations  
        
        #### **How It Works:**
        
        1. **Upload** your furnace production data
        2. **Input** each furnace's MVA capacity and design parameters
        3. **Get** capacity-based performance analysis
        4. **Implement** targeted improvements
        
        #### **Expected Data Columns:**
        - `Furnace` - Furnace identifier
        - `DATE` - Production date
        - `Actual Production Qty` - Daily production (MT)
        - `Total Cost PLC` - Total production cost (₹)
        - `Specific Power Consumption` - Power usage (kWh/MT)
        - `MN Recovery PLC` - Manganese recovery (%)
        """)
    
    with col2:
        st.image("https://img.icons8.com/color/300/000000/industry.png", width=250)
        
        st.markdown("### 🚀 Quick Start")
        
        st.markdown("""
        **For Accurate Analysis:**
        
        1. Know your furnace MVA ratings
        2. Have design capacity targets
        3. Set realistic cost targets
        4. Define optimal power consumption
        
        **Output Includes:**
        - Capacity utilization rates
        - Cost vs target analysis
        - Power efficiency metrics
        - Recovery optimization
        - Quality control insights
        """)

else:
    # Data is loaded - show analysis
    processor = st.session_state.processor
    insights = st.session_state.insights
    
    # ========== EXECUTIVE SUMMARY ==========
    st.markdown("## 📊 EXECUTIVE SUMMARY")
    
    if hasattr(processor, 'get_comparative_analysis'):
        # Capacity-based analysis
        comparative = processor.get_comparative_analysis()
        
        # Display key metrics in cards
        cols = st.columns(4)
        
        with cols[0]:
            total_prod = comparative['total_production'].sum() if 'total_production' in comparative.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #4B5563; font-size: 0.9rem;">TOTAL PRODUCTION</h3>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #1E3A8A;">{total_prod:,.0f} MT</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            avg_cost = comparative['avg_cost_mt'].mean() if 'avg_cost_mt' in comparative.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #4B5563; font-size: 0.9rem;">AVG COST/TON</h3>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #DC2626;">₹{avg_cost:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            avg_power = comparative['avg_power_mt'].mean() if 'avg_power_mt' in comparative.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #4B5563; font-size: 0.9rem;">AVG POWER/TON</h3>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #F59E0B;">{avg_power:,.0f} kWh</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            avg_mn = comparative['avg_mn_recovery'].mean() if 'avg_mn_recovery' in comparative.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #4B5563; font-size: 0.9rem;">AVG MN RECOVERY</h3>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #10B981;">{avg_mn:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Capacity Utilization Chart
        st.markdown("### 🏭 CAPACITY UTILIZATION")
        
        if 'capacity_utilization' in comparative.columns:
            fig = px.bar(
                comparative,
                x='furnace',
                y='capacity_utilization',
                title="Capacity Utilization by Furnace",
                labels={'capacity_utilization': 'Utilization (%)', 'furnace': 'Furnace'},
                color='capacity_utilization',
                color_continuous_scale='RdYlGn',
                text='capacity_utilization'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(yaxis_range=[0, 120])
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== ACTIONABLE INSIGHTS ==========
    st.markdown("## 💡 ACTIONABLE INSIGHTS")
    
    if insights:
        # Count total insights
        total_insights = sum(len(cat_insights) for cat_insights in insights.values())
        
        # Show critical issues first
        if '🚨 Critical Issues' in insights and insights['🚨 Critical Issues']:
            st.markdown("### 🚨 CRITICAL ISSUES (Require Immediate Attention)")
            
            for insight in insights['🚨 Critical Issues']:
                furnace = insight.get('furnace', '')
                severity_class = "insight-critical"
                
                st.markdown(f"""
                <div class="{severity_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #DC2626;">{insight.get('title', 'Critical Issue')}</h4>
                        <span class="furnace-tag">{furnace}</span>
                    </div>
                    <p style="margin: 0.5rem 0; color: #4B5563;"><strong>📋 Description:</strong> {insight.get('description', '')}</p>
                    <p style="margin: 0.5rem 0; color: #4B5563;"><strong>💥 Impact:</strong> {insight.get('impact', '')}</p>
                    <p style="margin: 0.5rem 0; color: #059669;"><strong>🎯 Recommendation:</strong> {insight.get('recommendation', '')}</p>
                    {f'<p style="margin: 0.5rem 0; color: #DC2626;"><strong>💰 Financial Impact:</strong> {insight.get("financial_impact", "")}</p>' if insight.get('financial_impact') else ''}
                    {f'<p style="margin: 0.5rem 0;"><strong>📈 Confidence:</strong> <span class="confidence-high">{insight.get("confidence", "high").upper()}</span></p>' if insight.get('confidence') else ''}
                </div>
                """, unsafe_allow_html=True)
        
        # Show other categories
        other_categories = [cat for cat in insights.keys() if cat != '🚨 Critical Issues']
        
        for category in other_categories:
            if insights[category]:
                st.markdown(f"### {category}")
                
                for insight in insights[category]:
                    furnace = insight.get('furnace', '')
                    severity = insight.get('severity', 'medium')
                    severity_class = f"insight-{severity}"
                    
                    st.markdown(f"""
                    <div class="{severity_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <h4 style="margin: 0; color: {'#DC2626' if severity == 'high' else '#F59E0B' if severity == 'medium' else '#10B981'};">{insight.get('title', 'Insight')}</h4>
                            {f'<span class="furnace-tag">{furnace}</span>' if furnace else ''}
                        </div>
                        <p style="margin: 0.5rem 0; color: #4B5563;"><strong>📋 Description:</strong> {insight.get('description', '')}</p>
                        <p style="margin: 0.5rem 0; color: #4B5563;"><strong>💥 Impact:</strong> {insight.get('impact', '')}</p>
                        <p style="margin: 0.5rem 0; color: #059669;"><strong>🎯 Recommendation:</strong> {insight.get('recommendation', '')}</p>
                        {f'<p style="margin: 0.5rem 0; color: #DC2626;"><strong>💰 Financial Impact:</strong> {insight.get("financial_impact", "")}</p>' if insight.get('financial_impact') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No insights generated. Please check your data format.")
    
    # ========== FURNACE COMPARISON ==========
    st.markdown("## 📊 FURNACE PERFORMANCE COMPARISON")
    
    if hasattr(processor, 'get_comparative_analysis'):
        comparative = processor.get_comparative_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost Comparison
            if 'avg_cost_mt' in comparative.columns:
                fig = px.bar(
                    comparative,
                    x='furnace',
                    y='avg_cost_mt',
                    title="Cost per Ton Comparison",
                    labels={'avg_cost_mt': 'Cost (₹/MT)', 'furnace': 'Furnace'},
                    color='avg_cost_mt',
                    color_continuous_scale='RdYlGn_r',
                    text='avg_cost_mt'
                )
                fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Power Comparison
            if 'avg_power_mt' in comparative.columns:
                fig = px.bar(
                    comparative,
                    x='furnace',
                    y='avg_power_mt',
                    title="Power Consumption Comparison",
                    labels={'avg_power_mt': 'Power (kWh/MT)', 'furnace': 'Furnace'},
                    color='avg_power_mt',
                    color_continuous_scale='RdYlGn_r',
                    text='avg_power_mt'
                )
                fig.update_traces(texttemplate='%{text:,.0f} kWh', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
    
    # ========== DATA QUALITY CHECK ==========
    with st.expander("🔍 DATA QUALITY CHECK"):
        if hasattr(processor, 'df'):
            df = processor.df
        else:
            df = processor
        
        st.dataframe(df.head(10), use_container_width=True)
        
        # Show basic stats
        st.markdown("#### Data Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Records", len(df))
            st.metric("Total Columns", len(df.columns))
        
        with col2:
            if 'Furnace' in df.columns:
                st.metric("Unique Furnaces", df['Furnace'].nunique())
            if 'DATE' in df.columns:
                st.metric("Date Range", f"{df['DATE'].min().date()} to {df['DATE'].max().date()}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; padding: 1rem;">
        <p style="font-size: 0.9rem; margin: 0.2rem;">🔥 <strong>Furnace Performance Intelligence System</strong> • Capacity-Based Analysis</p>
        <p style="font-size: 0.8rem; margin: 0.2rem;">Focus: APEX Reduction • Quality Maintenance • Actionable Insights</p>
        <p style="font-size: 0.7rem; margin: 0.2rem;">© 2024 • Enterprise Production Version</p>
    </div>
    """,
    unsafe_allow_html=True
)
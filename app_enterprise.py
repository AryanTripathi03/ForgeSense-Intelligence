# app_enterprise.py - Final Enterprise Furnace Intelligence System
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

# Set page config
st.set_page_config(
    page_title="Furnace Intelligence - Enterprise",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-top: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .insight-card {
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .critical {
        border-left: 6px solid #EF4444;
        background: linear-gradient(135deg, #FEF2F2, #FEE2E2);
    }
    .high {
        border-left: 5px solid #F59E0B;
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
    }
    .medium {
        border-left: 4px solid #10B981;
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    }
    .furnace-badge {
        background: #3B82F6;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .data-point {
        background: #F3F4F6;
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        font-size: 0.9rem;
        color: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-header">🔥 FURNACE PERFORMANCE INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enterprise System • Multi-Grade Analysis • Comprehensive Insights • APEX Reduction Focus</p>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'insights' not in st.session_state:
    st.session_state.insights = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'capacities' not in st.session_state:
    st.session_state.capacities = {}

# Sidebar
with st.sidebar:
    st.markdown("### 📁 DATA UPLOAD")
    
    uploaded_file = st.file_uploader(
        "Upload Furnace Production Report",
        type=['xlsx', 'xls'],
        help="Upload daily production data with all columns"
    )
    
    if uploaded_file:
        try:
            # Read data
            df = pd.read_excel(uploaded_file)
            st.session_state.raw_df = df
            
            # Get unique furnaces
            furnace_cols = [col for col in df.columns if 'furnace' in str(col).lower()]
            if furnace_cols:
                furnace_col = furnace_cols[0]
                furnaces = sorted(df[furnace_col].unique())
                
                st.markdown("---")
                st.markdown("### ⚙️ FURNACE CAPACITY INPUT")
                st.info(f"Found {len(furnaces)} furnaces")
                
                # ONLY ASK FOR MVA CAPACITY - everything else from data
                capacities = {}
                for furnace in furnaces:
                    mva = st.number_input(
                        f"MVA Capacity - {furnace}",
                        min_value=1.0,
                        max_value=100.0,
                        value=12.5,
                        step=0.5,
                        key=f"mva_{furnace}",
                        help="Enter MVA rating of the furnace"
                    )
                    capacities[furnace] = mva
                
                st.session_state.capacities = capacities
                
                # Process button
                if st.button("🚀 ANALYZE COMPREHENSIVELY", type="primary", use_container_width=True):
                    with st.spinner("🔄 Performing comprehensive analysis..."):
                        try:
                            # Import analyzer
                            from src.core.complete_analyzer import CompleteFurnaceAnalyzer
                            from src.intelligence.comprehensive_insights import ComprehensiveInsightsEngine
                            
                            # Create analyzer
                            analyzer = CompleteFurnaceAnalyzer(df)
                            st.session_state.analyzer = analyzer
                            
                            # Generate insights
                            insights_engine = ComprehensiveInsightsEngine(analyzer, capacities)
                            insights = insights_engine.generate_all_insights()
                            st.session_state.insights = insights
                            
                            st.session_state.data_loaded = True
                            st.success("✅ Comprehensive Analysis Complete!")
                            
                        except ImportError as e:
                            st.error(f"System modules not found: {e}")
                            st.info("Running in basic mode")
                            st.session_state.analyzer = df
                            st.session_state.data_loaded = True
                        except Exception as e:
                            st.error(f"Analysis error: {str(e)}")
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        st.info("👆 Upload your complete furnace data to begin")
        
        # Quick sample
        if st.button("🧪 Load Sample Format", use_container_width=True):
            st.info("Sample format loaded. Upload your actual data for analysis.")

# Main Content
if not st.session_state.data_loaded:
    # Welcome
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 COMPREHENSIVE FURNACE ANALYSIS")
        
        st.markdown("""
        This enterprise system analyzes **ALL parameters** from your furnace data:
        
        #### **Complete Analysis Includes:**
        
        ✅ **Production Analysis** - Yield, efficiency, capacity utilization  
        ✅ **Cost Optimization** - Per ton cost, cost drivers, grade-wise cost  
        ✅ **Power Efficiency** - Consumption, load factor, power factor  
        ✅ **Material Recovery** - MN, SI, and other element recovery  
        ✅ **Product Quality** - Grade MN, Grade SI, Carbon%, Basicity  
        ✅ **Operational Excellence** - Breakdowns, availability, efficiency  
        ✅ **Multi-Grade Analysis** - Cost and quality by product grade  
        ✅ **Comparative Analysis** - Furnace-to-furnace benchmarking  
        
        #### **How It Works:**
        
        1. **Upload** complete furnace data (all columns)
        2. **Input** only MVA capacity for each furnace
        3. **System calculates** everything else from data
        4. **Get** comprehensive, actionable insights
        5. **Focus** on APEX reduction while maintaining quality
        """)
    
    with col2:
        st.image("https://img.icons8.com/color/300/000000/factory.png", width=250)
        
        st.markdown("### 📋 Required Data")
        st.markdown("""
        Your Excel should include:
        
        • **Furnace** - Identifier
        • **DATE** - Production date
        • **Actual Production Qty** - MT
        • **Total Cost PLC** - ₹
        • **Specific Power Consumption** - kWh/MT
        • **MN Recovery PLC** - %
        • **Grade MN, Grade SI, C%** - Quality
        • **All other columns** from your reports
        
        **Only input needed:** MVA capacity
        """)

else:
    # Data loaded - show comprehensive analysis
    analyzer = st.session_state.analyzer
    insights = st.session_state.insights
    
    # ========== EXECUTIVE DASHBOARD ==========
    st.markdown("## 📊 EXECUTIVE DASHBOARD")
    
    if hasattr(analyzer, 'get_furnace_summary'):
        summary = analyzer.get_furnace_summary()
        
        # Key Metrics
        cols = st.columns(5)
        
        with cols[0]:
            total_prod = summary['Total_Production_MT'].sum() if 'Total_Production_MT' in summary.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #6B7280;">TOTAL PRODUCTION</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1E3A8A;">{total_prod:,.0f} MT</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            avg_cost = summary['Avg_Cost_per_Ton'].mean() if 'Avg_Cost_per_Ton' in summary.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #6B7280;">AVG COST/TON</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #DC2626;">₹{avg_cost:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            avg_power = summary['Avg_Power_kWh_MT'].mean() if 'Avg_Power_kWh_MT' in summary.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #6B7280;">AVG POWER/TON</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #F59E0B;">{avg_power:,.0f} kWh</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            avg_mn = summary['Avg_MN_Recovery_%'].mean() if 'Avg_MN_Recovery_%' in summary.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #6B7280;">AVG MN RECOVERY</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #10B981;">{avg_mn:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[4]:
            avg_score = summary['Performance_Score'].mean() if 'Performance_Score' in summary.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #6B7280;">PERFORMANCE SCORE</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #8B5CF6;">{avg_score:.0f}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Capacity Utilization
        st.markdown("### 🏭 CAPACITY UTILIZATION")
        
        if hasattr(analyzer, 'capacity_metrics'):
            capacity_data = []
            for furnace, metrics in analyzer.capacity_metrics.items():
                capacity_data.append({
                    'Furnace': furnace,
                    'MVA Capacity': metrics['mva_capacity'],
                    'Design Capacity (MT/day)': metrics['design_capacity_mt'],
                    'Utilization %': metrics['current_utilization']
                })
            
            if capacity_data:
                cap_df = pd.DataFrame(capacity_data)
                
                fig = px.bar(
                    cap_df,
                    x='Furnace',
                    y='Utilization %',
                    title="Capacity Utilization by Furnace",
                    color='Utilization %',
                    color_continuous_scale='RdYlGn',
                    text='Utilization %',
                    labels={'Utilization %': 'Utilization (%)'}
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(yaxis_range=[0, max(120, cap_df['Utilization %'].max() * 1.1)])
                st.plotly_chart(fig, use_container_width=True)
    
    # ========== COMPREHENSIVE INSIGHTS ==========
    st.markdown("## 💡 COMPREHENSIVE ACTIONABLE INSIGHTS")
    
    if insights:
        # Count total insights
        total_insights = sum(len(cat_insights) for cat_insights in insights.values())
        critical_count = len(insights.get('🚨 CRITICAL ISSUES', []))
        
        st.markdown(f"**Generated {total_insights} insights ({critical_count} critical)**")
        
        # Show all insight categories
        for category, category_insights in insights.items():
            if category_insights:
                st.markdown(f"### {category}")
                
                for insight in category_insights:
                    severity = insight.get('severity', 'medium')
                    furnace = insight.get('furnace', '')
                    
                    # Determine CSS class
                    if severity == 'high' and category == '🚨 CRITICAL ISSUES':
                        css_class = 'critical'
                    elif severity == 'high':
                        css_class = 'high'
                    else:
                        css_class = 'medium'
                    
                    st.markdown(f"""
                    <div class="insight-card {css_class}">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.8rem;">
                            <h4 style="margin: 0; color: {'#DC2626' if severity == 'high' else '#F59E0B' if severity == 'medium' else '#10B981'};">{insight.get('title', 'Insight')}</h4>
                            {f'<span class="furnace-badge">{furnace}</span>' if furnace else ''}
                        </div>
                        <p style="margin: 0.5rem 0; color: #4B5563;"><strong>📋 Description:</strong> {insight.get('description', '')}</p>
                        <p style="margin: 0.5rem 0; color: #4B5563;"><strong>💥 Impact:</strong> {insight.get('impact', '')}</p>
                        <p style="margin: 0.5rem 0; color: #059669;"><strong>🎯 Recommendation:</strong> {insight.get('recommendation', '')}</p>
                        {f'<p style="margin: 0.5rem 0; color: #DC2626;"><strong>💰 Financial Impact:</strong> {insight.get("financial_impact", "")}</p>' if insight.get('financial_impact') else ''}
                        
                        {f'<div style="margin-top: 1rem;"><strong>📊 Data Points:</strong>' + 
                         ''.join([f'<div class="data-point">{k}: {v}</div>' for k, v in insight.get('data', {}).items()]) + 
                         '</div>' if insight.get('data') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("No insights generated. Please check your data format.")
    
    # ========== MULTI-GRADE ANALYSIS ==========
    st.markdown("## 📈 MULTI-GRADE PRODUCTION ANALYSIS")
    
    if hasattr(analyzer, 'grade_analysis') and analyzer.grade_analysis:
        grade_data = []
        for grade, analysis in analyzer.grade_analysis.items():
            grade_data.append({
                'Grade': grade,
                'Total Production (MT)': analysis.get('total_production', 0),
                'Avg Cost/Ton (₹)': analysis.get('avg_cost_per_ton', 0),
                'Avg Grade MN (%)': analysis.get('avg_grade_mn', 0),
                'Avg Grade SI (%)': analysis.get('avg_grade_si', 0),
                'Production Days': analysis.get('production_days', 0)
            })
        
        grade_df = pd.DataFrame(grade_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Grade-wise production
            fig = px.bar(
                grade_df,
                x='Grade',
                y='Total Production (MT)',
                title="Production by Grade",
                color='Grade',
                text='Total Production (MT)'
            )
            fig.update_traces(texttemplate='%{text:,.0f} MT', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Grade-wise cost
            fig = px.bar(
                grade_df,
                x='Grade',
                y='Avg Cost/Ton (₹)',
                title="Cost per Ton by Grade",
                color='Avg Cost/Ton (₹)',
                color_continuous_scale='RdYlGn_r',
                text='Avg Cost/Ton (₹)'
            )
            fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # Show grade distribution
        st.markdown("#### Grade Distribution Details")
        st.dataframe(grade_df, use_container_width=True)
    
    # ========== FURNACE COMPARISON ==========
    st.markdown("## 📊 FURNACE PERFORMANCE COMPARISON")
    
    if hasattr(analyzer, 'get_furnace_summary'):
        summary = analyzer.get_furnace_summary()
        
        # Create comparison tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Cost & Power", "Recovery & Quality", "Operations", "Full Summary"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    summary,
                    x='Furnace',
                    y='Avg_Cost_per_Ton',
                    title="Cost per Ton Comparison",
                    color='Avg_Cost_per_Ton',
                    color_continuous_scale='RdYlGn_r',
                    text='Avg_Cost_per_Ton'
                )
                fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    summary,
                    x='Furnace',
                    y='Avg_Power_kWh_MT',
                    title="Power Consumption Comparison",
                    color='Avg_Power_kWh_MT',
                    color_continuous_scale='RdYlGn_r',
                    text='Avg_Power_kWh_MT'
                )
                fig.update_traces(texttemplate='%{text:,.0f} kWh', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Avg_MN_Recovery_%' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Avg_MN_Recovery_%',
                        title="MN Recovery Comparison",
                        color='Avg_MN_Recovery_%',
                        color_continuous_scale='RdYlGn',
                        text='Avg_MN_Recovery_%'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Avg_Grade_MN_%' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Avg_Grade_MN_%',
                        title="Grade MN Comparison",
                        color='Avg_Grade_MN_%',
                        color_continuous_scale='RdYlGn',
                        text='Avg_Grade_MN_%'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Avg_Breakdown_Mins' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Avg_Breakdown_Mins',
                        title="Breakdown Time Comparison",
                        color='Avg_Breakdown_Mins',
                        color_continuous_scale='RdYlGn_r',
                        text='Avg_Breakdown_Mins'
                    )
                    fig.update_traces(texttemplate='%{text:.0f} mins', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Operational_Availability_%' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Operational_Availability_%',
                        title="Operational Availability",
                        color='Operational_Availability_%',
                        color_continuous_scale='RdYlGn',
                        text='Operational_Availability_%'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.dataframe(summary, use_container_width=True)
    
    # ========== DATA QUALITY CHECK ==========
    with st.expander("🔍 DATA QUALITY & SAMPLE"):
        if hasattr(analyzer, 'processed_df'):
            df = analyzer.processed_df
        else:
            df = analyzer
        
        st.markdown("#### Sample Data (First 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown("#### Data Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df))
            st.metric("Total Columns", len(df.columns))
        
        with col2:
            if 'Furnace' in df.columns:
                st.metric("Unique Furnaces", df['Furnace'].nunique())
            if 'GRADE' in df.columns:
                st.metric("Unique Grades", df['GRADE'].nunique())
        
        with col3:
            if 'DATE' in df.columns:
                st.metric("Date Range", f"{df['DATE'].min().date()} to {df['DATE'].max().date()}")
                st.metric("Total Days", df['DATE'].nunique())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; padding: 1rem; font-size: 0.9rem;">
        <p><strong>🔥 Furnace Performance Intelligence System • Enterprise Edition</strong></p>
        <p>Comprehensive Analysis • Multi-Grade Support • APEX Reduction Focus • Quality Maintenance</p>
        <p style="font-size: 0.8rem;">© 2024 • All calculations from data • Only MVA input required</p>
    </div>
    """,
    unsafe_allow_html=True
)
# app_fixed_correct.py - Fixed app with correct unit handling
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Furnace Intelligence - Corrected",
    page_icon="🔥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-top: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 500;
    }
    .correction-note {
        background: #FEF3C7;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 4px solid #F59E0B;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .data-verification {
        background: #ECFDF5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #10B981;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🔥 FURNACE INTELLIGENCE - CORRECTED UNITS</h1>', unsafe_allow_html=True)
st.markdown("***Fixed for accurate calculations based on your actual data***")
st.markdown("---")

# Initialize session state
if 'fixed_analyzer' not in st.session_state:
    st.session_state.fixed_analyzer = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Sidebar
with st.sidebar:
    st.markdown("### 📁 UPLOAD YOUR DATA")
    
    uploaded_file = st.file_uploader(
        "Upload furnace Excel file",
        type=['xlsx', 'xls']
    )
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ File loaded: {len(df)} rows")
            
            # Show data issues
            with st.expander("🔍 Data Issues Found"):
                st.write("**Original MN Recovery values:**")
                if 'MN Recovery PLC' in df.columns:
                    sample = df['MN Recovery PLC'].head(3).tolist()
                    st.write(f"Sample: {sample}")
                    st.write("**Issue:** Values are decimals (0.90 = 90%)")
                
                st.write("**Cost per Ton Calculation:**")
                if 'Actual Production Qty' in df.columns and 'Total Cost PLC' in df.columns:
                    mask = df['Actual Production Qty'] > 0
                    if mask.any():
                        cost_per_ton = df.loc[mask, 'Total Cost PLC'] / df.loc[mask, 'Actual Production Qty']
                        st.write(f"Range: ₹{cost_per_ton.min():,.0f} to ₹{cost_per_ton.max():,.0f}")
            
            # Capacity input
            st.markdown("---")
            st.markdown("### ⚙️ FURNACE CAPACITY")
            
            if 'Furnace' in df.columns:
                furnaces = sorted(df['Furnace'].unique())
                capacities = {}
                
                for furnace in furnaces:
                    mva = st.number_input(
                        f"MVA - {furnace}",
                        min_value=1.0,
                        max_value=100.0,
                        value=12.5,
                        step=0.5,
                        key=f"mva_{furnace}"
                    )
                    capacities[furnace] = mva
                
                st.session_state.capacities = capacities
            
            # Process with FIXED analyzer
            if st.button("🚀 ANALYZE WITH CORRECTIONS", type="primary", use_container_width=True):
                with st.spinner("🔄 Applying unit corrections and analyzing..."):
                    try:
                        from fixed_analyzer import FixedFurnaceAnalyzer
                        
                        analyzer = FixedFurnaceAnalyzer(df)
                        st.session_state.fixed_analyzer = analyzer
                        st.session_state.data_loaded = True
                        
                        st.success("✅ Analysis complete with unit corrections!")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    
    else:
        st.info("👆 Upload your furnace data")

# Main content
if not st.session_state.data_loaded:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 CORRECTED UNIT ANALYSIS")
        st.markdown("""
        This version **corrects the unit issues** found in your data:
        
        #### **Issues Fixed:**
        
        🔧 **MN Recovery PLC** - Multiplied by 100 (0.90 → 90%)  
        🔧 **SI Recovery PLC** - Multiplied by 100  
        🔧 **Load Factor** - Corrected if in decimals  
        🔧 **Power Units** - Adjusted if needed  
        
        #### **Accurate Calculations:**
        
        ✅ **Cost per Ton** = Total Cost PLC / Actual Production Qty  
        ✅ **Power per Ton** = Total Power / Production  
        ✅ **Recovery Rates** = Corrected percentages  
        ✅ **Yield** = Actual Production / Cake Production  
        
        #### **Only Input Needed:**
        • MVA capacity for each furnace
        """)
    
    with col2:
        st.image("https://img.icons8.com/color/200/000000/calculator.png", width=150)
        st.markdown("### 📊 Unit Corrections")
        st.markdown("""
        **Before:**  
        MN Recovery: 0.90  
        **After:**  
        MN Recovery: 90%
        
        **Before:**  
        Load Factor: 1.01  
        **After:**  
        Load Factor: 101%
        """)

else:
    # Data loaded - show CORRECTED analysis
    analyzer = st.session_state.fixed_analyzer
    
    # ========== CORRECTION NOTES ==========
    st.markdown("""
    <div class="correction-note">
    🔧 <strong>UNIT CORRECTIONS APPLIED:</strong> MN Recovery, SI Recovery, and other percentages multiplied by 100 for correct interpretation.
    </div>
    """, unsafe_allow_html=True)
    
    # ========== CORRECTED DASHBOARD ==========
    st.markdown("## 📊 CORRECTED PERFORMANCE DASHBOARD")
    
    if hasattr(analyzer, 'get_overall_stats'):
        stats = analyzer.get_overall_stats()
        
        # Display CORRECTED metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_prod = stats.get('total_production', 0)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">TOTAL PRODUCTION</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_prod:,.0f} MT</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            avg_cost = stats.get('avg_cost_per_ton', 0)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">AVG COST PER TON</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">₹{avg_cost:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            avg_power = stats.get('avg_power_per_ton', 0)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">AVG POWER PER TON</div>', unsafe_allow_html=True)
            if avg_power > 1000:
                st.markdown(f'<div class="metric-value">{avg_power:,.0f} kWh</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-value">{avg_power:.1f} kWh</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            avg_mn = stats.get('avg_mn_recovery', 0)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">AVG MN RECOVERY</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_mn:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional metrics
        col5, col6, col7 = st.columns(3)
        
        with col5:
            total_cost = stats.get('total_cost', 0)
            st.metric("TOTAL COST", f"₹{total_cost:,.0f}")
        
        with col6:
            avg_si = stats.get('avg_si_recovery', 0)
            st.metric("AVG SI RECOVERY", f"{avg_si:.1f}%")
        
        with col7:
            avg_load = stats.get('avg_load_factor', 0)
            st.metric("AVG LOAD FACTOR", f"{avg_load:.1f}%")
    
    # ========== DATA VERIFICATION ==========
    st.markdown("## 🔍 DATA VERIFICATION")
    
    if hasattr(analyzer, 'get_data_verification'):
        verification = analyzer.get_data_verification()
        
        st.markdown('<div class="data-verification">', unsafe_allow_html=True)
        st.markdown("### ✅ Unit Correction Verification")
        
        if verification['original_mn_recovery_sample'] and verification['corrected_mn_recovery_sample']:
            st.write("**MN Recovery Correction:**")
            for i, (orig, corr) in enumerate(zip(verification['original_mn_recovery_sample'], 
                                               verification['corrected_mn_recovery_sample'])):
                st.write(f"  Row {i}: {orig:.4f} → {corr:.1f}%")
        
        if verification['cost_calculation_sample']:
            st.write("**Cost per Ton Calculation:**")
            for i, calc in enumerate(verification['cost_calculation_sample'][:3]):
                st.write(f"  Row {i}: ₹{calc['cost']:,.0f} / {calc['production']:.1f} MT = ₹{calc['cost_per_ton']:,.0f}/MT")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== FURNACE COMPARISON ==========
    st.markdown("## 🏭 FURNACE PERFORMANCE COMPARISON")
    
    if hasattr(analyzer, 'get_furnace_summary'):
        summary = analyzer.get_furnace_summary()
        
        if not summary.empty:
            st.dataframe(summary, use_container_width=True)
            
            # Charts with CORRECTED data
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    summary,
                    x='Furnace',
                    y='Avg Cost/Ton (₹)',
                    title='Corrected Cost per Ton by Furnace',
                    color='Avg Cost/Ton (₹)',
                    color_continuous_scale='RdYlGn_r',
                    text='Avg Cost/Ton (₹)'
                )
                fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Avg MN Recovery (%)' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Avg MN Recovery (%)',
                        title='Corrected MN Recovery by Furnace',
                        color='Avg MN Recovery (%)',
                        color_continuous_scale='RdYlGn',
                        text='Avg MN Recovery (%)'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(yaxis_range=[0, 100])
                    st.plotly_chart(fig, use_container_width=True)
            
            # More charts
            col3, col4 = st.columns(2)
            
            with col3:
                if 'Avg Power/Ton (kWh/MT)' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Avg Power/Ton (kWh/MT)',
                        title='Power per Ton by Furnace',
                        color='Avg Power/Ton (kWh/MT)',
                        color_continuous_scale='RdYlGn_r',
                        text='Avg Power/Ton (kWh/MT)'
                    )
                    fig.update_traces(texttemplate='%{text:.0f} kWh', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'Avg Yield (%)' in summary.columns:
                    fig = px.bar(
                        summary,
                        x='Furnace',
                        y='Avg Yield (%)',
                        title='Yield Percentage by Furnace',
                        color='Avg Yield (%)',
                        color_continuous_scale='RdYlGn',
                        text='Avg Yield (%)'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
    
    # ========== INSIGHTS ==========
    st.markdown("## 💡 INSIGHTS & RECOMMENDATIONS")
    
    if hasattr(analyzer, 'furnace_analysis'):
        furnace_analysis = analyzer.furnace_analysis
        
        insights = []
        
        for furnace, analysis in furnace_analysis.items():
            # Cost insights
            avg_cost = analysis.get('avg_cost_per_ton', 0)
            if avg_cost > 70000:
                insights.append({
                    'type': 'high',
                    'title': f'High Production Cost - {furnace}',
                    'desc': f'Average cost: ₹{avg_cost:,.0f}/MT',
                    'rec': 'Review raw material usage and power consumption'
                })
            elif avg_cost < 40000:
                insights.append({
                    'type': 'good',
                    'title': f'Good Cost Performance - {furnace}',
                    'desc': f'Average cost: ₹{avg_cost:,.0f}/MT (Below ₹40,000)',
                    'rec': 'Maintain current practices'
                })
            
            # MN Recovery insights
            avg_mn = analysis.get('avg_mn_recovery', 0)
            if avg_mn < 75:
                insights.append({
                    'type': 'high',
                    'title': f'Low MN Recovery - {furnace}',
                    'desc': f'MN Recovery: {avg_mn:.1f}% (Below 75%)',
                    'rec': 'Optimize furnace temperature and slag chemistry'
                })
            elif avg_mn > 85:
                insights.append({
                    'type': 'good',
                    'title': f'Excellent MN Recovery - {furnace}',
                    'desc': f'MN Recovery: {avg_mn:.1f}% (Above 85%)',
                    'rec': 'Excellent performance, maintain parameters'
                })
            
            # Power insights
            avg_power = analysis.get('avg_power_per_ton', 0)
            if avg_power > 3000:
                insights.append({
                    'type': 'high',
                    'title': f'High Power Consumption - {furnace}',
                    'desc': f'Power: {avg_power:,.0f} kWh/MT',
                    'rec': 'Check electrode efficiency and power factor'
                })
        
        # Display insights
        if insights:
            for insight in insights:
                if insight['type'] == 'high':
                    st.error(f"🚨 **{insight['title']}**\n\n{insight['desc']}\n\n**Recommendation:** {insight['rec']}")
                elif insight['type'] == 'good':
                    st.success(f"✅ **{insight['title']}**\n\n{insight['desc']}\n\n**Recommendation:** {insight['rec']}")
        else:
            st.info("✅ All furnaces operating within acceptable ranges.")
    
    # ========== RAW DATA CHECK ==========
    with st.expander("📋 RAW DATA CHECK (First 3 rows)"):
        if hasattr(analyzer, 'clean_df'):
            df = analyzer.clean_df
            st.dataframe(df.head(3), use_container_width=True)
            
            # Show key columns
            st.write("**Key Columns Check:**")
            key_cols = ['Actual Production Qty', 'Total Cost PLC', 'MN Recovery PLC', 
                       'Specific Power Consumption', 'Grade MN', 'Grade SI']
            for col in key_cols:
                if col in df.columns:
                    st.write(f"{col}: {df[col].dtype}, Range: {df[col].min():.2f} to {df[col].max():.2f}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p><strong>Furnace Intelligence System - Corrected Units Version</strong></p>
        <p>Accurate Calculations • Unit Corrections Applied • Data-Driven Insights</p>
        <p style="font-size: 0.8rem;">MN Recovery, SI Recovery, and percentages corrected (×100)</p>
    </div>
    """,
    unsafe_allow_html=True
)
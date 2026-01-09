# app_fixed.py - Fixed and simplified furnace intelligence app
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.core.data_loader import FurnaceDataLoader
    from src.intelligence.insights_engine import InsightsEngine
except ImportError:
    # Create simple versions if import fails
    st.error("❌ Could not import core modules. Using simplified version.")
    
    # Simple data loader class
    class SimpleDataLoader:
        def load_excel(self, file_path):
            df = pd.read_excel(file_path)
            df.columns = [str(col).strip() for col in df.columns]
            return df
    
    # Simple insights engine
    class SimpleInsightsEngine:
        def __init__(self, df):
            self.df = df
        
        def analyze_all(self):
            return {"Cost Optimization": [], "Power Efficiency": [], 
                   "Material Recovery": [], "Operational Excellence": []}
    
    FurnaceDataLoader = SimpleDataLoader
    InsightsEngine = SimpleInsightsEngine

# Set page config
st.set_page_config(
    page_title="Furnace Intelligence System",
    page_icon="🔥",
    layout="wide"
)

# Title
st.title("🔥 Furnace Performance Intelligence System")
st.markdown("---")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'insights' not in st.session_state:
    st.session_state.insights = None

# Sidebar
with st.sidebar:
    st.header("📁 Data Upload")
    
    uploaded_file = st.file_uploader(
        "Upload Furnace Data Excel File",
        type=['xlsx', 'xls']
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = "temp_uploaded_data.xlsx"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("🚀 Analyze Data", type="primary"):
            with st.spinner("Loading and analyzing data..."):
                try:
                    # Load data
                    loader = FurnaceDataLoader()
                    df = loader.load_excel(temp_path)
                    st.session_state.df = df
                    
                    # Generate insights
                    engine = InsightsEngine(df)
                    insights = engine.analyze_all()
                    st.session_state.insights = insights
                    
                    st.session_state.data_loaded = True
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.markdown("""
    **Furnace Intelligence System**
    
    Transforms raw furnace data into:
    • Cost optimization insights
    • Power efficiency recommendations
    • Material recovery analysis
    • Operational excellence guidance
    """)

# Main content
if not st.session_state.data_loaded:
    # Show welcome screen
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("👆 Upload your furnace data Excel file to begin analysis")
        
        st.markdown("""
        ### 📋 Expected Data Format
        
        Your Excel file should contain these columns (or similar):
        
        **Core Columns:**
        - `Furnace` - Furnace identifier (F1, F2, etc.)
        - `DATE` - Date of operation
        - `Actual Production Qty` - Production quantity in tons
        - `Total Cost PLC` - Total production cost
        
        **Recommended Columns:**
        - `Specific Power Consumption` - Power per ton (kWh/ton)
        - `MN Recovery PLC` - Manganese recovery percentage
        - `Total Breakdown Mins` - Total breakdown minutes
        - `Load Factor` - Electrical load factor
        """)
    
    with col2:
        st.markdown("### 🧪 Try Sample Data")
        if st.button("Load Sample Data"):
            # Use the existing sample data
            if os.path.exists('sample_furnace_data.xlsx'):
                with st.spinner("Loading sample data..."):
                    try:
                        loader = FurnaceDataLoader()
                        df = loader.load_excel('sample_furnace_data.xlsx')
                        st.session_state.df = df
                        
                        engine = InsightsEngine(df)
                        insights = engine.analyze_all()
                        st.session_state.insights = insights
                        
                        st.session_state.data_loaded = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading sample: {e}")
            else:
                st.warning("Sample data file not found. Run create_sample.py first.")
    
else:
    # Data is loaded - show analysis
    df = st.session_state.df
    
    # ========== DASHBOARD HEADER ==========
    st.header("📊 Performance Dashboard")
    
    # Key metrics - use safe column detection
    col1, col2, col3, col4 = st.columns(4)
    
    # Find production column
    production_cols = [col for col in df.columns if 'prod' in str(col).lower() or 'qty' in str(col).lower()]
    production_col = production_cols[0] if production_cols else None
    
    # Find cost column
    cost_cols = [col for col in df.columns if 'cost' in str(col).lower() and 'total' in str(col).lower()]
    cost_col = cost_cols[0] if cost_cols else None
    
    # Find power column
    power_cols = [col for col in df.columns if 'power' in str(col).lower() and 'specific' in str(col).lower()]
    power_col = power_cols[0] if power_cols else None
    
    # Find MN recovery column
    mn_cols = [col for col in df.columns if 'mn' in str(col).lower() and 'recovery' in str(col).lower()]
    mn_col = mn_cols[0] if mn_cols else None
    
    with col1:
        if production_col:
            total_prod = df[production_col].sum()
            st.metric("Total Production", f"{total_prod:,.0f} MT")
        else:
            st.metric("Total Production", "N/A")
    
    with col2:
        if production_col and cost_col:
            try:
                df['cost_per_ton_temp'] = df[cost_col] / df[production_col]
                avg_cost = df['cost_per_ton_temp'].mean()
                st.metric("Avg Cost/Ton", f"₹{avg_cost:,.0f}")
            except:
                st.metric("Avg Cost/Ton", "N/A")
        else:
            st.metric("Avg Cost/Ton", "N/A")
    
    with col3:
        if power_col:
            avg_power = df[power_col].mean()
            st.metric("Avg Power/Ton", f"{avg_power:,.0f} kWh")
        else:
            st.metric("Avg Power/Ton", "N/A")
    
    with col4:
        if mn_col:
            avg_mn = df[mn_col].mean()
            st.metric("Avg MN Recovery", f"{avg_mn:.1f}%")
        else:
            st.metric("Avg MN Recovery", "N/A")
    
    # ========== DATA EXPLORER ==========
    st.header("🔍 Data Explorer")
    
    with st.expander("View Raw Data"):
        st.dataframe(df, use_container_width=True)
        
        # Show column information
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null': df.notnull().sum(),
            'Sample Values': df.iloc[0].astype(str) if len(df) > 0 else ['']
        })
        st.dataframe(col_info, use_container_width=True)
    
    # ========== BASIC VISUALIZATIONS ==========
    st.header("📈 Basic Visualizations")
    
    # Furnace column
    furnace_cols = [col for col in df.columns if 'furnace' in str(col).lower()]
    furnace_col = furnace_cols[0] if furnace_cols else None
    
    if furnace_col:
        # Production by furnace
        if production_col:
            st.subheader("Production by Furnace")
            furnace_prod = df.groupby(furnace_col)[production_col].sum().reset_index()
            
            fig = px.bar(
                furnace_prod,
                x=furnace_col,
                y=production_col,
                title="Total Production by Furnace",
                color=furnace_col
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost by furnace
        if cost_col:
            st.subheader("Cost by Furnace")
            furnace_cost = df.groupby(furnace_col)[cost_col].sum().reset_index()
            
            fig = px.bar(
                furnace_cost,
                x=furnace_col,
                y=cost_col,
                title="Total Cost by Furnace",
                color=furnace_col
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Time series analysis
    date_cols = [col for col in df.columns if 'date' in str(col).lower()]
    date_col = date_cols[0] if date_cols else None
    
    if date_col and production_col:
        st.subheader("Production Over Time")
        try:
            df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
            time_series = df.groupby('date_parsed')[production_col].sum().reset_index()
            time_series = time_series.sort_values('date_parsed')
            
            fig = px.line(
                time_series,
                x='date_parsed',
                y=production_col,
                title="Production Trend Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Could not parse dates for time series")
    
    # ========== CORRELATION ANALYSIS ==========
    st.header("📊 Correlation Analysis")
    
    # Select numeric columns for correlation
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) > 1:
        selected_cols = st.multiselect(
            "Select columns for correlation analysis",
            options=numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
        
        if len(selected_cols) >= 2:
            # Calculate correlation matrix
            corr_matrix = df[selected_cols].corr()
            
            # Create heatmap
            fig = px.imshow(
                corr_matrix,
                title="Correlation Matrix",
                labels=dict(color="Correlation"),
                x=selected_cols,
                y=selected_cols,
                color_continuous_scale="RdBu"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show scatter plots for highly correlated pairs
            st.subheader("Top Correlations")
            
            # Find top correlations
            corr_pairs = []
            for i in range(len(selected_cols)):
                for j in range(i+1, len(selected_cols)):
                    col1 = selected_cols[i]
                    col2 = selected_cols[j]
                    corr = abs(corr_matrix.loc[col1, col2])
                    if not np.isnan(corr):
                        corr_pairs.append((col1, col2, corr))
            
            # Sort by correlation strength
            corr_pairs.sort(key=lambda x: x[2], reverse=True)
            
            # Show top 3 correlations
            for i, (col1, col2, corr) in enumerate(corr_pairs[:3]):
                st.write(f"**{col1} vs {col2}**: Correlation = {corr:.3f}")
                fig = px.scatter(
                    df,
                    x=col1,
                    y=col2,
                    title=f"{col1} vs {col2} (Correlation: {corr:.3f})",
                    trendline=None  # Remove trendline to avoid statsmodels error
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ========== INSIGHTS SECTION ==========
    st.header("💡 Insights")
    
    insights = st.session_state.insights
    if insights and any(len(cat_insights) > 0 for cat_insights in insights.values()):
        # Create tabs for different insight categories
        categories_with_insights = [cat for cat, ins in insights.items() if len(ins) > 0]
        
        if categories_with_insights:
            tabs = st.tabs(categories_with_insights)
            
            for tab, category in zip(tabs, categories_with_insights):
                with tab:
                    category_insights = insights[category]
                    
                    for insight in category_insights:
                        # Determine color based on severity
                        severity = insight.get('severity', 'medium')
                        if severity == 'high':
                            border_color = "#ff4b4b"
                        elif severity == 'medium':
                            border_color = "#ffa500"
                        else:
                            border_color = "#4CAF50"
                        
                        # Create a styled container for each insight
                        st.markdown(f"""
                        <div style="
                            border-left: 5px solid {border_color};
                            padding: 10px 15px;
                            margin: 10px 0;
                            background-color: #f8f9fa;
                            border-radius: 5px;
                        ">
                            <h4 style="margin: 0;">{insight.get('title', 'Insight')}</h4>
                            <p style="margin: 5px 0;"><strong>Description:</strong> {insight.get('description', '')}</p>
                            <p style="margin: 5px 0;"><strong>Impact:</strong> {insight.get('impact', '')}</p>
                            <p style="margin: 5px 0;"><strong>Recommendation:</strong> {insight.get('recommendation', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No insights generated from the data.")
    else:
        st.info("No insights generated. The system is running in basic analysis mode.")
    
    # ========== EXPORT SECTION ==========
    st.header("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export data as CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Processed Data (CSV)",
            data=csv,
            file_name="furnace_processed_data.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export basic summary
        summary_text = "FURNACE DATA SUMMARY\n"
        summary_text += "=" * 50 + "\n\n"
        
        if furnace_col:
            summary_text += f"Furnaces: {', '.join(df[furnace_col].unique())}\n"
        
        if production_col:
            summary_text += f"Total Production: {df[production_col].sum():,.0f} MT\n"
        
        if cost_col:
            summary_text += f"Total Cost: ₹{df[cost_col].sum():,.0f}\n"
        
        summary_text += f"\nData Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
        
        st.download_button(
            label="📥 Download Summary (TXT)",
            data=summary_text,
            file_name="furnace_summary.txt",
            mime="text/plain"
        )

# Footer
st.markdown("---")
st.markdown("*Furnace Intelligence System • Basic Analysis Mode*")
# accurate_analyzer.py - Accurate furnace data analyzer
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AccurateFurnaceAnalyzer:
    """Accurate furnace data analyzer based on your exact columns"""
    
    def __init__(self, df):
        self.raw_df = df.copy()
        self.clean_df = None
        self.analyzed_data = {}
        self._clean_data()
        self._analyze_data()
    
    def _clean_data(self):
        """Clean and prepare the data"""
        df = self.raw_df.copy()
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Convert DATE to datetime
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        
        # Convert key numeric columns
        key_columns = [
            'Actual Production Qty', 'Cake Production Qty', 'Slag Qty (MT)',
            'MnO%', 'SiO2%', 'Feo%', 'Cao%', 'Mgo%', 'Al2O3%', 'Basicity',
            'Input Qty(Ore PLC)(MT)', 'Input Qty(Coke PLC)(MT)',
            'Furnace Power Consumption', 'Aux power Consumption', 'Specific Power Consumption',
            'MN Recovery PLC', 'SI Recovery PLC', 'Grade MN', 'Grade SI', 'C%',
            'Ore Cost PLC', 'Coke Cost PLC', 'Power Cost', 'Fluxes PLC', 'Total Cost PLC',
            'Target cost', 'Total Breakdown Mins', 'Load Factor', 'Power Factor'
        ]
        
        for col in key_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill NaN with 0 for breakdown columns
        if 'Total Breakdown Mins' in df.columns:
            df['Total Breakdown Mins'] = df['Total Breakdown Mins'].fillna(0)
        
        self.clean_df = df
    
    def _analyze_data(self):
        """Perform accurate analysis"""
        df = self.clean_df
        
        if df.empty:
            return
        
        # 1. Calculate accurate metrics
        df_analysis = df.copy()
        
        # Calculate Cost per Ton (ACCURATE)
        if 'Total Cost PLC' in df_analysis.columns and 'Actual Production Qty' in df_analysis.columns:
            # Avoid division by zero
            production_mask = df_analysis['Actual Production Qty'] > 0
            df_analysis.loc[production_mask, 'Cost_per_Ton_Accurate'] = (
                df_analysis.loc[production_mask, 'Total Cost PLC'] / 
                df_analysis.loc[production_mask, 'Actual Production Qty']
            )
        
        # Calculate Power Cost per Ton
        if 'Power Cost' in df_analysis.columns and 'Actual Production Qty' in df_analysis.columns:
            df_analysis.loc[production_mask, 'Power_Cost_per_Ton'] = (
                df_analysis.loc[production_mask, 'Power Cost'] / 
                df_analysis.loc[production_mask, 'Actual Production Qty']
            )
        
        # Calculate Yield Percentage
        if 'Actual Production Qty' in df_analysis.columns and 'Cake Production Qty' in df_analysis.columns:
            cake_mask = df_analysis['Cake Production Qty'] > 0
            df_analysis.loc[cake_mask, 'Yield_Percentage'] = (
                df_analysis.loc[cake_mask, 'Actual Production Qty'] / 
                df_analysis.loc[cake_mask, 'Cake Production Qty'] * 100
            )
        
        # Calculate Ore Efficiency
        if 'Actual Production Qty' in df_analysis.columns and 'Input Qty(Ore PLC)(MT)' in df_analysis.columns:
            ore_mask = df_analysis['Input Qty(Ore PLC)(MT)'] > 0
            df_analysis.loc[ore_mask, 'Ore_Efficiency'] = (
                df_analysis.loc[ore_mask, 'Actual Production Qty'] / 
                df_analysis.loc[ore_mask, 'Input Qty(Ore PLC)(MT)']
            )
        
        # Calculate Operational Availability
        if 'Total Breakdown Mins' in df_analysis.columns:
            df_analysis['Operational_Availability'] = ((1440 - df_analysis['Total Breakdown Mins']) / 1440) * 100
        
        self.analysis_df = df_analysis
        
        # 2. Analyze by Furnace
        if 'Furnace' in df_analysis.columns:
            self._analyze_by_furnace(df_analysis)
        
        # 3. Calculate overall statistics
        self._calculate_overall_stats(df_analysis)
    
    def _analyze_by_furnace(self, df):
        """Analyze data by furnace"""
        furnaces = df['Furnace'].unique()
        furnace_analysis = {}
        
        for furnace in furnaces:
            furnace_data = df[df['Furnace'] == furnace]
            
            # Calculate accurate averages (ignore NaN)
            analysis = {
                'furnace': furnace,
                'total_production': furnace_data['Actual Production Qty'].sum(),
                'total_cost': furnace_data['Total Cost PLC'].sum(),
                'total_power_cost': furnace_data['Power Cost'].sum() if 'Power Cost' in furnace_data.columns else 0,
                'total_breakdown_hours': furnace_data['Total Breakdown Mins'].sum() / 60,
                
                # Averages (only valid data)
                'avg_production': furnace_data['Actual Production Qty'].mean(),
                'avg_cost_per_ton': furnace_data.loc[furnace_data['Actual Production Qty'] > 0, 'Cost_per_Ton_Accurate'].mean() 
                                    if 'Cost_per_Ton_Accurate' in furnace_data.columns else 0,
                'avg_power_consumption': furnace_data['Specific Power Consumption'].mean(),
                'avg_mn_recovery': furnace_data['MN Recovery PLC'].mean(),
                'avg_si_recovery': furnace_data['SI Recovery PLC'].mean() if 'SI Recovery PLC' in furnace_data.columns else 0,
                'avg_grade_mn': furnace_data['Grade MN'].mean(),
                'avg_grade_si': furnace_data['Grade SI'].mean(),
                'avg_carbon': furnace_data['C%'].mean(),
                'avg_basicity': furnace_data['Basicity'].mean(),
                'avg_load_factor': furnace_data['Load Factor'].mean() if 'Load Factor' in furnace_data.columns else 0,
                'avg_power_factor': furnace_data['Power Factor'].mean() if 'Power Factor' in furnace_data.columns else 0,
                'avg_breakdown_mins': furnace_data['Total Breakdown Mins'].mean(),
                'operational_availability': furnace_data['Operational_Availability'].mean() 
                                          if 'Operational_Availability' in furnace_data.columns else 0,
                
                # Counts
                'days_operated': furnace_data['DATE'].nunique() if 'DATE' in furnace_data.columns else len(furnace_data),
                'total_records': len(furnace_data),
            }
            
            # Calculate capacity utilization if we have MVA
            furnace_analysis[furnace] = analysis
        
        self.furnace_analysis = furnace_analysis
    
    def _calculate_overall_stats(self, df):
        """Calculate overall statistics"""
        self.overall_stats = {
            'total_production': df['Actual Production Qty'].sum(),
            'total_cost': df['Total Cost PLC'].sum(),
            'avg_cost_per_ton': df.loc[df['Actual Production Qty'] > 0, 'Cost_per_Ton_Accurate'].mean() 
                               if 'Cost_per_Ton_Accurate' in df.columns else 0,
            'avg_power_consumption': df['Specific Power Consumption'].mean(),
            'avg_mn_recovery': df['MN Recovery PLC'].mean(),
            'avg_si_recovery': df['SI Recovery PLC'].mean() if 'SI Recovery PLC' in df.columns else 0,
            'total_breakdown_hours': df['Total Breakdown Mins'].sum() / 60,
            'operational_availability': df['Operational_Availability'].mean() 
                                      if 'Operational_Availability' in df.columns else 0,
            'total_days': df['DATE'].nunique() if 'DATE' in df.columns else len(df),
        }
    
    def get_furnace_summary(self):
        """Get summary of all furnaces"""
        if not hasattr(self, 'furnace_analysis'):
            return pd.DataFrame()
        
        summary_data = []
        for furnace, analysis in self.furnace_analysis.items():
            row = {
                'Furnace': furnace,
                'Total Production (MT)': analysis['total_production'],
                'Avg Daily Production (MT)': analysis['avg_production'],
                'Avg Cost/Ton (₹)': analysis['avg_cost_per_ton'],
                'Avg Power (kWh/MT)': analysis['avg_power_consumption'],
                'Avg MN Recovery (%)': analysis['avg_mn_recovery'],
                'Avg SI Recovery (%)': analysis['avg_si_recovery'],
                'Avg Grade MN (%)': analysis['avg_grade_mn'],
                'Avg Grade SI (%)': analysis['avg_grade_si'],
                'Avg Breakdown (mins/day)': analysis['avg_breakdown_mins'],
                'Operational Availability (%)': analysis['operational_availability'],
                'Days Operated': analysis['days_operated']
            }
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def get_overall_stats(self):
        """Get overall statistics"""
        return self.overall_stats
# fixed_analyzer.py - Fixed analyzer for your actual data
import pandas as pd
import numpy as np
from datetime import datetime

class FixedFurnaceAnalyzer:
    """Fixed analyzer for your actual data with correct unit conversions"""
    
    def __init__(self, df):
        self.raw_df = df.copy()
        self.clean_df = None
        self._clean_and_fix_data()
        self._analyze_fixed_data()
    
    def _clean_and_fix_data(self):
        """Clean and FIX the data units"""
        df = self.raw_df.copy()
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Remove unnecessary columns
        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)
        
        # Convert DATE to datetime
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        
        # ========== CRITICAL FIXES ==========
        # Convert key columns to numeric
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
        
        # ========== UNIT CORRECTIONS ==========
        # 1. MN Recovery PLC - Multiply by 100 to get percentage
        if 'MN Recovery PLC' in df.columns:
            df['MN Recovery PLC'] = df['MN Recovery PLC'] * 100
        
        # 2. SI Recovery PLC - Multiply by 100 to get percentage
        if 'SI Recovery PLC' in df.columns:
            df['SI Recovery PLC'] = df['SI Recovery PLC'] * 100
        
        # 3. MN Recovery Feeding - Multiply by 100
        if 'MN Recovery Feeding' in df.columns:
            df['MN Recovery Feeding'] = df['MN Recovery Feeding'] * 100
        
        # 4. SI Recovery Feeding - Multiply by 100
        if 'SI Recovery Feeding' in df.columns:
            df['SI Recovery Feeding'] = df['SI Recovery Feeding'] * 100
        
        # 5. Load Factor - Seems to be decimal, multiply by 100 if < 10
        if 'Load Factor' in df.columns:
            if df['Load Factor'].max() < 10:
                df['Load Factor'] = df['Load Factor'] * 100
        
        # 6. Recovery Liquid Metal - Multiply by 100 if < 1
        if 'Recovery Liquid Metal' in df.columns:
            if df['Recovery Liquid Metal'].max() < 1:
                df['Recovery Liquid Metal'] = df['Recovery Liquid Metal'] * 100
        
        # 7. Power Consumption - Check if values are too small
        if 'Furnace Power Consumption' in df.columns:
            if df['Furnace Power Consumption'].max() < 1000:
                # Values might be in MW instead of kWh? Let's check
                avg_power = df['Furnace Power Consumption'].mean()
                if avg_power < 100:
                    # Probably in MW, convert to kWh (×1000)
                    df['Furnace Power Consumption'] = df['Furnace Power Consumption'] * 1000
                    if 'Aux power Consumption' in df.columns:
                        df['Aux power Consumption'] = df['Aux power Consumption'] * 1000
        
        self.clean_df = df
    
    def _analyze_fixed_data(self):
        """Analyze with corrected units"""
        df = self.clean_df
        
        if df.empty:
            return
        
        # Calculate metrics with CORRECTED units
        df_analysis = df.copy()
        
        # 1. Cost per Ton (using Total Cost PLC)
        if 'Total Cost PLC' in df_analysis.columns and 'Actual Production Qty' in df_analysis.columns:
            mask = df_analysis['Actual Production Qty'] > 0
            df_analysis.loc[mask, 'Cost_per_Ton_Corrected'] = (
                df_analysis.loc[mask, 'Total Cost PLC'] / 
                df_analysis.loc[mask, 'Actual Production Qty']
            )
        
        # 2. Power Cost per Ton
        if 'Power Cost' in df_analysis.columns and 'Actual Production Qty' in df_analysis.columns:
            mask = df_analysis['Actual Production Qty'] > 0
            df_analysis.loc[mask, 'Power_Cost_per_Ton'] = (
                df_analysis.loc[mask, 'Power Cost'] / 
                df_analysis.loc[mask, 'Actual Production Qty']
            )
        
        # 3. Calculate Total Power (Furnace + Aux)
        if 'Furnace Power Consumption' in df_analysis.columns:
            total_power = df_analysis['Furnace Power Consumption']
            if 'Aux power Consumption' in df_analysis.columns:
                total_power = total_power + df_analysis['Aux power Consumption']
            df_analysis['Total_Power_kWh'] = total_power
        
        # 4. Power per Ton
        if 'Total_Power_kWh' in df_analysis.columns and 'Actual Production Qty' in df_analysis.columns:
            mask = df_analysis['Actual Production Qty'] > 0
            df_analysis.loc[mask, 'Power_per_Ton_kWh'] = (
                df_analysis.loc[mask, 'Total_Power_kWh'] / 
                df_analysis.loc[mask, 'Actual Production Qty']
            )
        
        # 5. Yield Percentage
        if 'Actual Production Qty' in df_analysis.columns and 'Cake Production Qty' in df_analysis.columns:
            mask = df_analysis['Cake Production Qty'] > 0
            df_analysis.loc[mask, 'Yield_Percentage'] = (
                df_analysis.loc[mask, 'Actual Production Qty'] / 
                df_analysis.loc[mask, 'Cake Production Qty'] * 100
            )
        
        # 6. Ore Efficiency
        if 'Actual Production Qty' in df_analysis.columns and 'Input Qty(Ore PLC)(MT)' in df_analysis.columns:
            mask = df_analysis['Input Qty(Ore PLC)(MT)'] > 0
            df_analysis.loc[mask, 'Ore_Efficiency'] = (
                df_analysis.loc[mask, 'Actual Production Qty'] / 
                df_analysis.loc[mask, 'Input Qty(Ore PLC)(MT)']
            )
        
        # 7. Coke Efficiency
        if 'Actual Production Qty' in df_analysis.columns and 'Input Qty(Coke PLC)(MT)' in df_analysis.columns:
            mask = df_analysis['Input Qty(Coke PLC)(MT)'] > 0
            df_analysis.loc[mask, 'Coke_Efficiency'] = (
                df_analysis.loc[mask, 'Actual Production Qty'] / 
                df_analysis.loc[mask, 'Input Qty(Coke PLC)(MT)']
            )
        
        self.analysis_df = df_analysis
        
        # Analyze by furnace
        if 'Furnace' in df_analysis.columns:
            self._analyze_by_furnace_fixed(df_analysis)
        
        # Calculate overall stats
        self._calculate_overall_fixed_stats(df_analysis)
    
    def _analyze_by_furnace_fixed(self, df):
        """Analyze by furnace with corrected units"""
        furnaces = df['Furnace'].unique()
        furnace_analysis = {}
        
        for furnace in furnaces:
            furnace_data = df[df['Furnace'] == furnace]
            
            # Calculate with CORRECTED units
            analysis = {
                'furnace': furnace,
                'total_production': furnace_data['Actual Production Qty'].sum(),
                'total_cost': furnace_data['Total Cost PLC'].sum(),
                'total_power_cost': furnace_data['Power Cost'].sum() if 'Power Cost' in furnace_data.columns else 0,
                
                # Averages with corrected units
                'avg_production': furnace_data['Actual Production Qty'].mean(),
                'avg_cost_per_ton': furnace_data.loc[furnace_data['Actual Production Qty'] > 0, 'Cost_per_Ton_Corrected'].mean() 
                                    if 'Cost_per_Ton_Corrected' in furnace_data.columns else 0,
                'avg_power_per_ton': furnace_data.loc[furnace_data['Actual Production Qty'] > 0, 'Power_per_Ton_kWh'].mean() 
                                    if 'Power_per_Ton_kWh' in furnace_data.columns else 0,
                'avg_mn_recovery': furnace_data['MN Recovery PLC'].mean(),
                'avg_si_recovery': furnace_data['SI Recovery PLC'].mean() if 'SI Recovery PLC' in furnace_data.columns else 0,
                'avg_grade_mn': furnace_data['Grade MN'].mean(),
                'avg_grade_si': furnace_data['Grade SI'].mean(),
                'avg_carbon': furnace_data['C%'].mean(),
                'avg_basicity': furnace_data['Basicity'].mean(),
                'avg_load_factor': furnace_data['Load Factor'].mean() if 'Load Factor' in furnace_data.columns else 0,
                'avg_power_factor': furnace_data['Power Factor'].mean() if 'Power Factor' in furnace_data.columns else 0,
                'avg_yield': furnace_data['Yield_Percentage'].mean() if 'Yield_Percentage' in furnace_data.columns else 0,
                'avg_ore_efficiency': furnace_data['Ore_Efficiency'].mean() if 'Ore_Efficiency' in furnace_data.columns else 0,
                
                # Counts
                'days_operated': furnace_data['DATE'].nunique() if 'DATE' in furnace_data.columns else len(furnace_data),
                'total_records': len(furnace_data),
            }
            
            furnace_analysis[furnace] = analysis
        
        self.furnace_analysis = furnace_analysis
    
    def _calculate_overall_fixed_stats(self, df):
        """Calculate overall stats with corrected units"""
        self.overall_stats = {
            'total_production': df['Actual Production Qty'].sum(),
            'total_cost': df['Total Cost PLC'].sum(),
            'avg_cost_per_ton': df.loc[df['Actual Production Qty'] > 0, 'Cost_per_Ton_Corrected'].mean() 
                               if 'Cost_per_Ton_Corrected' in df.columns else 0,
            'avg_power_per_ton': df.loc[df['Actual Production Qty'] > 0, 'Power_per_Ton_kWh'].mean() 
                               if 'Power_per_Ton_kWh' in df.columns else 0,
            'avg_mn_recovery': df['MN Recovery PLC'].mean(),
            'avg_si_recovery': df['SI Recovery PLC'].mean() if 'SI Recovery PLC' in df.columns else 0,
            'avg_grade_mn': df['Grade MN'].mean(),
            'avg_grade_si': df['Grade SI'].mean(),
            'avg_carbon': df['C%'].mean(),
            'avg_basicity': df['Basicity'].mean(),
            'avg_load_factor': df['Load Factor'].mean() if 'Load Factor' in df.columns else 0,
            'total_days': df['DATE'].nunique() if 'DATE' in df.columns else len(df),
        }
    
    def get_furnace_summary(self):
        """Get summary with corrected units"""
        if not hasattr(self, 'furnace_analysis'):
            return pd.DataFrame()
        
        summary_data = []
        for furnace, analysis in self.furnace_analysis.items():
            row = {
                'Furnace': furnace,
                'Total Production (MT)': analysis['total_production'],
                'Avg Daily Production (MT)': analysis['avg_production'],
                'Avg Cost/Ton (₹)': analysis['avg_cost_per_ton'],
                'Avg Power/Ton (kWh/MT)': analysis['avg_power_per_ton'],
                'Avg MN Recovery (%)': analysis['avg_mn_recovery'],
                'Avg SI Recovery (%)': analysis['avg_si_recovery'],
                'Avg Grade MN (%)': analysis['avg_grade_mn'],
                'Avg Grade SI (%)': analysis['avg_grade_si'],
                'Avg Carbon (%)': analysis['avg_carbon'],
                'Avg Yield (%)': analysis['avg_yield'],
                'Avg Load Factor (%)': analysis['avg_load_factor'],
                'Days Operated': analysis['days_operated']
            }
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def get_overall_stats(self):
        """Get overall stats with corrected units"""
        return self.overall_stats
    
    def get_data_verification(self):
        """Show data verification with corrections"""
        df = self.analysis_df if hasattr(self, 'analysis_df') else self.clean_df
        
        verification = {
            'original_mn_recovery_sample': self.raw_df['MN Recovery PLC'].head(3).tolist() if 'MN Recovery PLC' in self.raw_df.columns else [],
            'corrected_mn_recovery_sample': df['MN Recovery PLC'].head(3).tolist() if 'MN Recovery PLC' in df.columns else [],
            'cost_calculation_sample': []
        }
        
        # Show cost calculation
        if 'Cost_per_Ton_Corrected' in df.columns:
            for i in range(min(3, len(df))):
                prod = df.iloc[i]['Actual Production Qty'] if 'Actual Production Qty' in df.columns else 0
                cost = df.iloc[i]['Total Cost PLC'] if 'Total Cost PLC' in df.columns else 0
                calc = df.iloc[i]['Cost_per_Ton_Corrected']
                verification['cost_calculation_sample'].append({
                    'production': prod,
                    'cost': cost,
                    'cost_per_ton': calc
                })
        
        return verification
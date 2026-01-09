# src/core/complete_analyzer.py - Complete furnace data analyzer
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class FurnaceCapacity:
    """Only capacity input needed from user"""
    furnace_id: str
    mva_capacity: float  # Only user input needed
    design_capacity_mt_per_day: Optional[float] = None  # Will be calculated from data

class CompleteFurnaceAnalyzer:
    """Analyze complete furnace data with multi-grade support"""
    
    def __init__(self, df: pd.DataFrame):
        self.raw_df = df.copy()
        self.processed_df = None
        self.grade_analysis = {}
        self.furnace_analysis = {}
        self.targets = {}
        
        # Process the data
        self._process_data()
        self._calculate_targets()
        self._analyze_all()
    
    def _process_data(self):
        """Process and clean the complete dataset"""
        df = self.raw_df.copy()
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Convert DATE to datetime
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = [
            'Actual Production Qty', 'Shortage', 'Cake Production Qty',
            'Slag Qty (MT)', 'MnO%', 'SiO2%', 'Feo%', 'Cao%', 'Mgo%', 'Al2O3%',
            'Basicity', 'Tappings', 'Input Qty(Ore PLC)(MT)', 'Input Qty(Coke PLC)(MT)',
            'Number of Batches A Shift', 'Number of Batches B Shift', 'Number of Batches C Shift',
            'Total Number of Batches', 'Input Ratio', 'Metal Wt', 'Recovery Liquid Metal',
            'Grade MN', 'Grade SI', 'C%', 'MN Feeding', 'MN PLC', 'MN Recovery Feeding',
            'MN Recovery PLC', 'FC Feeding', 'FC PLC', 'SI Recovery Feeding', 'SI Recovery PLC',
            'Breaking Size', 'Under Size Generation', 'Furnace Power Consumption',
            'Aux power Consumption', 'Specific Power Consumption', 'Avg. Mg.', 'Load Factor',
            'Elec. Length Day Avg.', 'Power Factor', 'Elec. Holding Day Avg.', 'Elec. Slipping Day Avg.',
            'Ore Cost Feeding', 'Coke Cost Feeding', 'Fluxes Feeding', 'Consumable items',
            'Power Cost', 'Undersize Cost', 'Over head', 'Total Cost Feeding',
            'Ore Cost PLC', 'Coke Cost PLC', 'Fluxes PLC', 'Undersize Cost PLC', 'Total Cost PLC',
            'Mechanical B/D Mins', 'Electrical B/D Mins', 'Production B/D Mins',
            'Preventive B/D Mins', 'Shutdown Mins', 'Total Breakdown Mins',
            'Target cost', 'Total Cost PLC 4 Items', 'P/L', 'Total P/L'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate key metrics
        df = self._calculate_metrics(df)
        
        self.processed_df = df
    
    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all derived metrics"""
        df_calc = df.copy()
        
        # 1. Production Efficiency Metrics
        if 'Actual Production Qty' in df_calc.columns and 'Cake Production Qty' in df_calc.columns:
            df_calc['Yield_Percentage'] = (df_calc['Actual Production Qty'] / df_calc['Cake Production Qty']) * 100
        
        if 'Actual Production Qty' in df_calc.columns and 'Input Qty(Ore PLC)(MT)' in df_calc.columns:
            df_calc['Ore_Efficiency'] = df_calc['Actual Production Qty'] / df_calc['Input Qty(Ore PLC)(MT)']
        
        if 'Actual Production Qty' in df_calc.columns and 'Input Qty(Coke PLC)(MT)' in df_calc.columns:
            df_calc['Coke_Efficiency'] = df_calc['Actual Production Qty'] / df_calc['Input Qty(Coke PLC)(MT)']
        
        # 2. Cost Metrics
        if 'Total Cost PLC' in df_calc.columns and 'Actual Production Qty' in df_calc.columns:
            df_calc['Cost_per_Ton'] = df_calc['Total Cost PLC'] / df_calc['Actual Production Qty']
        
        if 'Power Cost' in df_calc.columns and 'Actual Production Qty' in df_calc.columns:
            df_calc['Power_Cost_per_Ton'] = df_calc['Power Cost'] / df_calc['Actual Production Qty']
        
        # 3. Material Recovery Metrics
        if 'MN Recovery PLC' in df_calc.columns and 'MN Recovery Feeding' in df_calc.columns:
            df_calc['MN_Recovery_Gap'] = df_calc['MN Recovery PLC'] - df_calc['MN Recovery Feeding']
        
        if 'SI Recovery PLC' in df_calc.columns and 'SI Recovery Feeding' in df_calc.columns:
            df_calc['SI_Recovery_Gap'] = df_calc['SI Recovery PLC'] - df_calc['SI Recovery Feeding']
        
        # 4. Operational Metrics
        if 'Total Breakdown Mins' in df_calc.columns:
            df_calc['Operational_Availability'] = ((1440 - df_calc['Total Breakdown Mins']) / 1440) * 100
        
        # 5. Quality Score (0-100)
        quality_score = 0
        
        if 'Grade MN' in df_calc.columns:
            # Grade MN score (target 70%)
            mn_score = 100 - abs(df_calc['Grade MN'] - 70) * 5
            mn_score = mn_score.clip(0, 100)
            quality_score += mn_score * 0.4  # 40% weight
        
        if 'Grade SI' in df_calc.columns:
            # Grade SI score (target 17.5%)
            si_score = 100 - abs(df_calc['Grade SI'] - 17.5) * 10
            si_score = si_score.clip(0, 100)
            quality_score += si_score * 0.3  # 30% weight
        
        if 'C%' in df_calc.columns:
            # Carbon score (target 7%)
            c_score = 100 - abs(df_calc['C%'] - 7) * 20
            c_score = c_score.clip(0, 100)
            quality_score += c_score * 0.2  # 20% weight
        
        if 'Basicity' in df_calc.columns:
            # Basicity score (target 1.35)
            basicity_score = 100 - abs(df_calc['Basicity'] - 1.35) * 40
            basicity_score = basicity_score.clip(0, 100)
            quality_score += basicity_score * 0.1  # 10% weight
        
        df_calc['Quality_Score'] = quality_score
        
        # 6. Overall Performance Score (0-100)
        performance_score = 0
        weights = 0
        
        # Cost score (lower is better)
        if 'Cost_per_Ton' in df_calc.columns:
            cost_mean = df_calc['Cost_per_Ton'].mean()
            if cost_mean > 0:
                cost_score = 100 - (df_calc['Cost_per_Ton'] / cost_mean - 1) * 50
                cost_score = cost_score.clip(0, 100)
                performance_score += cost_score * 0.3  # 30% weight
                weights += 0.3
        
        # Power score (lower is better)
        if 'Specific Power Consumption' in df_calc.columns:
            power_mean = df_calc['Specific Power Consumption'].mean()
            if power_mean > 0:
                power_score = 100 - (df_calc['Specific Power Consumption'] / power_mean - 1) * 50
                power_score = power_score.clip(0, 100)
                performance_score += power_score * 0.2  # 20% weight
                weights += 0.2
        
        # MN Recovery score (higher is better)
        if 'MN Recovery PLC' in df_calc.columns:
            mn_recovery_score = df_calc['MN Recovery PLC'].clip(0, 100)
            performance_score += mn_recovery_score * 0.2  # 20% weight
            weights += 0.2
        
        # Yield score (higher is better)
        if 'Yield_Percentage' in df_calc.columns:
            yield_score = df_calc['Yield_Percentage'].clip(0, 100)
            performance_score += yield_score * 0.15  # 15% weight
            weights += 0.15
        
        # Quality score
        if 'Quality_Score' in df_calc.columns:
            performance_score += df_calc['Quality_Score'] * 0.15  # 15% weight
            weights += 0.15
        
        if weights > 0:
            df_calc['Performance_Score'] = performance_score / weights
        
        return df_calc
    
    def _calculate_targets(self):
        """Calculate targets from historical best performance"""
        df = self.processed_df
        
        # Calculate targets as 75th percentile (good performance)
        self.targets = {
            # Production
            'Production_per_Day': df.groupby('DATE')['Actual Production Qty'].sum().quantile(0.75),
            'Yield_Percentage': df['Yield_Percentage'].quantile(0.75) if 'Yield_Percentage' in df.columns else 95,
            
            # Cost
            'Cost_per_Ton': df['Cost_per_Ton'].quantile(0.25) if 'Cost_per_Ton' in df.columns else 50000,  # Lower is better
            
            # Power
            'Specific_Power_Consumption': df['Specific Power Consumption'].quantile(0.25) if 'Specific Power Consumption' in df.columns else 2500,
            'Load_Factor': df['Load Factor'].quantile(0.75) if 'Load Factor' in df.columns else 85,
            'Power_Factor': df['Power Factor'].quantile(0.75) if 'Power Factor' in df.columns else 0.95,
            
            # Recovery
            'MN_Recovery_PLC': df['MN Recovery PLC'].quantile(0.75) if 'MN Recovery PLC' in df.columns else 80,
            'SI_Recovery_PLC': df['SI Recovery PLC'].quantile(0.75) if 'SI Recovery PLC' in df.columns else 45,
            
            # Quality
            'Grade_MN': 70,  # Standard target
            'Grade_SI': 17.5,  # Standard target
            'C_Percent': 7.0,  # Standard target
            'Basicity': 1.35,  # Standard target
            
            # Operations
            'Breakdown_Mins': df['Total Breakdown Mins'].quantile(0.25) if 'Total Breakdown Mins' in df.columns else 60,
            'Operational_Availability': 90,  # Target 90%
            
            # Efficiency
            'Ore_Efficiency': df['Ore_Efficiency'].quantile(0.75) if 'Ore_Efficiency' in df.columns else 0.55,
            'Coke_Efficiency': df['Coke_Efficiency'].quantile(0.75) if 'Coke_Efficiency' in df.columns else 4.0,
        }
    
    def _analyze_all(self):
        """Perform complete analysis"""
        df = self.processed_df
        
        # 1. Analyze by Furnace
        if 'Furnace' in df.columns:
            self._analyze_by_furnace()
        
        # 2. Analyze by Grade
        if 'GRADE' in df.columns:
            self._analyze_by_grade()
        
        # 3. Analyze by Date/Time patterns
        if 'DATE' in df.columns:
            self._analyze_time_patterns()
    
    def _analyze_by_furnace(self):
        """Analyze performance by furnace"""
        df = self.processed_df
        furnaces = df['Furnace'].unique()
        
        for furnace in furnaces:
            furnace_data = df[df['Furnace'] == furnace]
            
            # Calculate key metrics
            analysis = {
                'furnace': furnace,
                'total_records': len(furnace_data),
                'date_range': {
                    'start': furnace_data['DATE'].min(),
                    'end': furnace_data['DATE'].max()
                } if 'DATE' in furnace_data.columns else {},
                
                # Production Metrics
                'total_production': furnace_data['Actual Production Qty'].sum(),
                'avg_daily_production': furnace_data['Actual Production Qty'].mean(),
                'max_daily_production': furnace_data['Actual Production Qty'].max(),
                
                # Cost Metrics
                'total_cost': furnace_data['Total Cost PLC'].sum(),
                'avg_cost_per_ton': furnace_data['Cost_per_Ton'].mean() if 'Cost_per_Ton' in furnace_data.columns else 0,
                'cost_std_dev': furnace_data['Cost_per_Ton'].std() if 'Cost_per_Ton' in furnace_data.columns else 0,
                
                # Power Metrics
                'avg_power_consumption': furnace_data['Specific Power Consumption'].mean(),
                'avg_load_factor': furnace_data['Load Factor'].mean() if 'Load Factor' in furnace_data.columns else 0,
                'avg_power_factor': furnace_data['Power Factor'].mean() if 'Power Factor' in furnace_data.columns else 0,
                
                # Recovery Metrics
                'avg_mn_recovery': furnace_data['MN Recovery PLC'].mean(),
                'avg_si_recovery': furnace_data['SI Recovery PLC'].mean() if 'SI Recovery PLC' in furnace_data.columns else 0,
                'avg_mn_recovery_gap': furnace_data['MN_Recovery_Gap'].mean() if 'MN_Recovery_Gap' in furnace_data.columns else 0,
                
                # Quality Metrics
                'avg_grade_mn': furnace_data['Grade MN'].mean(),
                'avg_grade_si': furnace_data['Grade SI'].mean(),
                'avg_carbon': furnace_data['C%'].mean(),
                'avg_basicity': furnace_data['Basicity'].mean(),
                'avg_quality_score': furnace_data['Quality_Score'].mean() if 'Quality_Score' in furnace_data.columns else 0,
                
                # Operational Metrics
                'avg_breakdown_mins': furnace_data['Total Breakdown Mins'].mean(),
                'operational_availability': furnace_data['Operational_Availability'].mean() if 'Operational_Availability' in furnace_data.columns else 0,
                'total_breakdown_hours': furnace_data['Total Breakdown Mins'].sum() / 60,
                
                # Efficiency Metrics
                'avg_yield': furnace_data['Yield_Percentage'].mean() if 'Yield_Percentage' in furnace_data.columns else 0,
                'avg_ore_efficiency': furnace_data['Ore_Efficiency'].mean() if 'Ore_Efficiency' in furnace_data.columns else 0,
                'avg_coke_efficiency': furnace_data['Coke_Efficiency'].mean() if 'Coke_Efficiency' in furnace_data.columns else 0,
                
                # Performance Score
                'performance_score': furnace_data['Performance_Score'].mean() if 'Performance_Score' in furnace_data.columns else 0,
                
                # Cost Breakdown (if available)
                'cost_breakdown': self._get_cost_breakdown(furnace_data),
                
                # Grade Production (if GRADE available)
                'grade_production': self._get_grade_production(furnace_data) if 'GRADE' in furnace_data.columns else {},
            }
            
            self.furnace_analysis[furnace] = analysis
    
    def _analyze_by_grade(self):
        """Analyze performance by product grade"""
        df = self.processed_df
        
        if 'GRADE' not in df.columns:
            return
        
        grades = df['GRADE'].unique()
        
        for grade in grades:
            grade_data = df[df['GRADE'] == grade]
            
            analysis = {
                'grade': grade,
                'total_production': grade_data['Actual Production Qty'].sum(),
                'avg_cost_per_ton': (grade_data['Total Cost PLC'].sum() / grade_data['Actual Production Qty'].sum()) 
                                   if grade_data['Actual Production Qty'].sum() > 0 else 0,
                'furnace_distribution': grade_data.groupby('Furnace')['Actual Production Qty'].sum().to_dict(),
                'avg_grade_mn': grade_data['Grade MN'].mean(),
                'avg_grade_si': grade_data['Grade SI'].mean(),
                'avg_carbon': grade_data['C%'].mean(),
                'production_days': grade_data['DATE'].nunique(),
            }
            
            self.grade_analysis[grade] = analysis
    
    def _analyze_time_patterns(self):
        """Analyze time-based patterns"""
        df = self.processed_df
        
        if 'DATE' not in df.columns:
            return
        
        # Add time features
        df['Year'] = df['DATE'].dt.year
        df['Month'] = df['DATE'].dt.month
        df['Week'] = df['DATE'].dt.isocalendar().week
        df['DayOfWeek'] = df['DATE'].dt.dayofweek
        
        # Store for later use
        self.time_features_df = df
    
    def _get_cost_breakdown(self, furnace_data: pd.DataFrame) -> Dict[str, float]:
        """Get cost breakdown for furnace"""
        cost_columns = [
            'Ore Cost PLC', 'Coke Cost PLC', 'Power Cost', 
            'Fluxes PLC', 'Undersize Cost PLC'
        ]
        
        breakdown = {}
        total_cost = furnace_data['Total Cost PLC'].sum()
        
        for col in cost_columns:
            if col in furnace_data.columns:
                col_cost = furnace_data[col].sum()
                if total_cost > 0:
                    percentage = (col_cost / total_cost) * 100
                    breakdown[col.replace(' Cost PLC', '').replace(' PLC', '')] = {
                        'amount': col_cost,
                        'percentage': percentage,
                        'per_ton': col_cost / furnace_data['Actual Production Qty'].sum()
                    }
        
        return breakdown
    
    def _get_grade_production(self, furnace_data: pd.DataFrame) -> Dict[str, Dict]:
        """Get production by grade for furnace"""
        if 'GRADE' not in furnace_data.columns:
            return {}
        
        grade_summary = furnace_data.groupby('GRADE').agg({
            'Actual Production Qty': ['sum', 'mean', 'count'],
            'Total Cost PLC': 'sum',
            'Cost_per_Ton': 'mean' if 'Cost_per_Ton' in furnace_data.columns else None,
            'Grade MN': 'mean',
            'Grade SI': 'mean'
        }).round(2)
        
        # Flatten column names
        grade_summary.columns = ['_'.join(col).strip() for col in grade_summary.columns.values]
        grade_summary = grade_summary.reset_index()
        
        return grade_summary.to_dict('records')
    
    def get_furnace_summary(self) -> pd.DataFrame:
        """Get summary of all furnaces"""
        if not self.furnace_analysis:
            return pd.DataFrame()
        
        # Convert to DataFrame
        summary_data = []
        for furnace, analysis in self.furnace_analysis.items():
            row = {
                'Furnace': furnace,
                'Total_Production_MT': analysis.get('total_production', 0),
                'Avg_Daily_Production_MT': analysis.get('avg_daily_production', 0),
                'Avg_Cost_per_Ton': analysis.get('avg_cost_per_ton', 0),
                'Avg_Power_kWh_MT': analysis.get('avg_power_consumption', 0),
                'Avg_MN_Recovery_%': analysis.get('avg_mn_recovery', 0),
                'Avg_SI_Recovery_%': analysis.get('avg_si_recovery', 0),
                'Avg_Grade_MN_%': analysis.get('avg_grade_mn', 0),
                'Avg_Grade_SI_%': analysis.get('avg_grade_si', 0),
                'Avg_Carbon_%': analysis.get('avg_carbon', 0),
                'Avg_Breakdown_Mins': analysis.get('avg_breakdown_mins', 0),
                'Operational_Availability_%': analysis.get('operational_availability', 0),
                'Performance_Score': analysis.get('performance_score', 0),
            }
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def get_comprehensive_insights_data(self) -> Dict[str, Any]:
        """Get all data needed for comprehensive insights"""
        return {
            'furnace_analysis': self.furnace_analysis,
            'grade_analysis': self.grade_analysis,
            'targets': self.targets,
            'processed_data': self.processed_df,
            'summary': self.get_furnace_summary().to_dict('records')
        }
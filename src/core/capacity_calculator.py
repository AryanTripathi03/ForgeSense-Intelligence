# src/core/capacity_calculator.py - Capacity-based performance calculator
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FurnaceCapacity:
    """Furnace capacity configuration"""
    furnace_id: str
    mva_capacity: float  # MVA rating
    design_capacity_mt: float  # Designed production capacity in MT/day
    optimal_power_kwh_mt: float  # Optimal power consumption kWh/MT
    target_mn_recovery: float  # Target MN recovery %
    target_si_recovery: float  # Target SI recovery %
    target_cost_mt: float  # Target cost ₹/MT

class CapacityCalculator:
    """Calculate performance based on furnace capacity"""
    
    def __init__(self, df: pd.DataFrame, capacities: Dict[str, FurnaceCapacity]):
        """
        Initialize calculator with data and furnace capacities
        
        Args:
            df: Processed furnace data
            capacities: Dictionary of furnace_id -> FurnaceCapacity
        """
        self.df = df.copy()
        self.capacities = capacities
        self.results = {}
        
        # Calculate all metrics
        self._calculate_all_metrics()
    
    def _calculate_all_metrics(self):
        """Calculate all performance metrics based on capacity"""
        
        for furnace_id, capacity in self.capacities.items():
            furnace_data = self.df[self.df['Furnace'] == furnace_id].copy()
            
            if len(furnace_data) == 0:
                continue
            
            # Calculate actual vs capacity metrics
            results = {
                'furnace': furnace_id,
                'mva_capacity': capacity.mva_capacity,
                'design_capacity_mt': capacity.design_capacity_mt,
                'total_production': furnace_data['Actual Production Qty'].sum(),
                'avg_daily_production': furnace_data['Actual Production Qty'].mean(),
                'capacity_utilization': (furnace_data['Actual Production Qty'].mean() / capacity.design_capacity_mt) * 100,
                
                # Cost metrics
                'total_cost': furnace_data['Total Cost PLC'].sum(),
                'avg_cost_mt': furnace_data['Total Cost PLC'].sum() / furnace_data['Actual Production Qty'].sum(),
                'cost_vs_target': ((furnace_data['Total Cost PLC'].sum() / furnace_data['Actual Production Qty'].sum()) / capacity.target_cost_mt - 1) * 100,
                
                # Power metrics
                'avg_power_mt': furnace_data['Specific Power Consumption'].mean(),
                'power_vs_optimal': (furnace_data['Specific Power Consumption'].mean() / capacity.optimal_power_kwh_mt - 1) * 100,
                'total_power_cost': furnace_data['Power Cost'].sum(),
                
                # Recovery metrics
                'avg_mn_recovery': furnace_data['MN Recovery PLC'].mean(),
                'mn_recovery_gap': capacity.target_mn_recovery - furnace_data['MN Recovery PLC'].mean(),
                'avg_si_recovery': furnace_data['SI Recovery PLC'].mean() if 'SI Recovery PLC' in furnace_data.columns else None,
                
                # Quality metrics
                'avg_grade_mn': furnace_data['Grade MN'].mean() if 'Grade MN' in furnace_data.columns else None,
                'avg_grade_si': furnace_data['Grade SI'].mean() if 'Grade SI' in furnace_data.columns else None,
                'avg_carbon': furnace_data['C%'].mean() if 'C%' in furnace_data.columns else None,
                
                # Operational metrics
                'avg_breakdown_mins': furnace_data['Total Breakdown Mins'].mean(),
                'operational_availability': ((1440 - furnace_data['Total Breakdown Mins'].mean()) / 1440) * 100,
                'avg_load_factor': furnace_data['Load Factor'].mean() if 'Load Factor' in furnace_data.columns else None,
            }
            
            self.results[furnace_id] = results
    
    def get_furnace_performance(self, furnace_id: str) -> Dict:
        """Get performance analysis for a specific furnace"""
        return self.results.get(furnace_id, {})
    
    def get_comparative_analysis(self) -> pd.DataFrame:
        """Get comparative analysis of all furnaces"""
        if not self.results:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df_results = pd.DataFrame(self.results.values())
        
        # Calculate rankings
        metrics_to_rank = {
            'capacity_utilization': False,  # Higher is better
            'avg_cost_mt': True,  # Lower is better
            'avg_power_mt': True,  # Lower is better
            'avg_mn_recovery': False,  # Higher is better
            'operational_availability': False,  # Higher is better
        }
        
        for metric, ascending in metrics_to_rank.items():
            if metric in df_results.columns:
                df_results[f'{metric}_rank'] = df_results[metric].rank(ascending=ascending)
        
        return df_results
    
    def identify_cost_drivers(self, furnace_id: str) -> Dict[str, float]:
        """Identify main cost drivers for a furnace"""
        furnace_data = self.df[self.df['Furnace'] == furnace_id]
        
        cost_columns = [
            'Ore Cost PLC', 'Coke Cost PLC', 'Power Cost', 
            'Fluxes PLC', 'Undersize Cost PLC'
        ]
        
        cost_drivers = {}
        total_cost = furnace_data['Total Cost PLC'].sum()
        
        for col in cost_columns:
            if col in furnace_data.columns:
                col_cost = furnace_data[col].sum()
                if total_cost > 0:
                    percentage = (col_cost / total_cost) * 100
                    cost_drivers[col] = {
                        'amount': col_cost,
                        'percentage': percentage,
                        'per_ton': col_cost / furnace_data['Actual Production Qty'].sum()
                    }
        
        return cost_drivers
    
    def calculate_potential_savings(self) -> Dict[str, Dict]:
        """Calculate potential savings for each furnace"""
        savings = {}
        
        for furnace_id, capacity in self.capacities.items():
            if furnace_id not in self.results:
                continue
            
            perf = self.results[furnace_id]
            furnace_data = self.df[self.df['Furnace'] == furnace_id]
            total_production = furnace_data['Actual Production Qty'].sum()
            
            # Cost savings potential
            current_cost_mt = perf['avg_cost_mt']
            target_cost_mt = capacity.target_cost_mt
            cost_saving_mt = max(0, current_cost_mt - target_cost_mt)
            annual_cost_saving = cost_saving_mt * total_production * 365 / len(furnace_data)
            
            # Power savings potential
            current_power_mt = perf['avg_power_mt']
            optimal_power_mt = capacity.optimal_power_kwh_mt
            power_saving_mt = max(0, current_power_mt - optimal_power_mt)
            annual_power_saving = power_saving_mt * total_production * 8 * 365 / (1000 * len(furnace_data))  # ₹8/kWh
            
            # Recovery improvement potential
            current_mn_recovery = perf['avg_mn_recovery']
            target_mn_recovery = capacity.target_mn_recovery
            recovery_gap = max(0, target_mn_recovery - current_mn_recovery)
            
            savings[furnace_id] = {
                'cost_saving_per_ton': cost_saving_mt,
                'annual_cost_saving': annual_cost_saving,
                'power_saving_per_ton': power_saving_mt,
                'annual_power_saving': annual_power_saving,
                'mn_recovery_gap': recovery_gap,
                'potential_mn_improvement': (recovery_gap / 100) * furnace_data['MN Feeding'].sum() if 'MN Feeding' in furnace_data.columns else 0
            }
        
        return savings
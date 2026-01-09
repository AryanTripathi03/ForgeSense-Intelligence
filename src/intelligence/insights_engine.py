# src/intelligence/insights_engine.py - Generate actionable insights
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

class InsightsEngine:
    """Generate insights from furnace data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.insights = []
        
        # Target values (can be customized)
        self.targets = {
            'cost_per_ton': 70000,  # From your data: avg is 72,698
            'Specific Power Consumption': 2500,
            'MN Recovery PLC': 80,
            'SI Recovery PLC': 45,
            'operational_availability': 90,
            'Load Factor': 85
        }
    
    def analyze_all(self) -> Dict[str, List[Dict]]:
        """Run all analyses and return insights"""
        self.insights = []
        
        # 1. Cost Analysis
        self._analyze_costs()
        
        # 2. Power Efficiency Analysis
        self._analyze_power()
        
        # 3. Material Recovery Analysis
        self._analyze_recovery()
        
        # 4. Operational Analysis
        self._analyze_operations()
        
        # 5. Comparative Analysis
        self._analyze_comparative()
        
        # Categorize insights
        categorized = self._categorize_insights()
        
        return categorized
    
    def _analyze_costs(self):
        """Analyze cost-related insights"""
        if 'cost_per_ton' not in self.df.columns:
            return
        
        # Analyze each furnace
        for furnace in self.df['Furnace'].unique():
            furnace_data = self.df[self.df['Furnace'] == furnace]
            avg_cost = furnace_data['cost_per_ton'].mean()
            
            # Check if above target
            if avg_cost > self.targets['cost_per_ton']:
                percent_above = ((avg_cost - self.targets['cost_per_ton']) / self.targets['cost_per_ton']) * 100
                
                self.insights.append({
                    'type': 'cost',
                    'severity': 'high' if percent_above > 10 else 'medium',
                    'furnace': furnace,
                    'title': f'High Operating Cost - {furnace}',
                    'description': f'Average cost per ton (₹{avg_cost:,.0f}) is {percent_above:.1f}% above target (₹{self.targets["cost_per_ton"]:,.0f})',
                    'impact': f'Extra cost: ₹{(avg_cost - self.targets["cost_per_ton"]) * furnace_data["Actual Production Qty"].sum() / len(furnace_data):,.0f} per day',
                    'recommendation': 'Review raw material mix, optimize power consumption, reduce breakdown time',
                    'metric': 'cost_per_ton',
                    'value': avg_cost,
                    'target': self.targets['cost_per_ton']
                })
        
        # Find cost drivers
        if 'Total Cost PLC' in self.df.columns:
            # Calculate cost breakdown
            cost_columns = ['Ore Cost PLC', 'Coke Cost PLC', 'Power Cost', 'Fluxes PLC']
            available_cost_cols = [col for col in cost_columns if col in self.df.columns]
            
            if available_cost_cols:
                total_costs = self.df[available_cost_cols].sum()
                max_cost_component = total_costs.idxmax()
                max_cost_value = total_costs.max()
                total_all_costs = total_costs.sum()
                
                if total_all_costs > 0:
                    percent_of_total = (max_cost_value / total_all_costs) * 100
                    
                    self.insights.append({
                        'type': 'cost_structure',
                        'severity': 'medium',
                        'title': 'Major Cost Driver Identified',
                        'description': f'{max_cost_component} accounts for {percent_of_total:.1f}% of total costs',
                        'impact': 'Opportunity for targeted cost reduction',
                        'recommendation': f'Focus on optimizing {max_cost_component.replace(" Cost PLC", "").lower()} usage and sourcing'
                    })
    
    def _analyze_power(self):
        """Analyze power efficiency"""
        if 'Specific Power Consumption' not in self.df.columns:
            return
        
        for furnace in self.df['Furnace'].unique():
            furnace_data = self.df[self.df['Furnace'] == furnace]
            avg_power = furnace_data['Specific Power Consumption'].mean()
            
            if avg_power > self.targets['Specific Power Consumption']:
                percent_above = ((avg_power - self.targets['Specific Power Consumption']) / 
                               self.targets['Specific Power Consumption']) * 100
                
                self.insights.append({
                    'type': 'power',
                    'severity': 'medium' if percent_above < 20 else 'high',
                    'furnace': furnace,
                    'title': f'High Power Consumption - {furnace}',
                    'description': f'Specific power consumption ({avg_power:,.0f} kWh/ton) is {percent_above:.1f}% above target ({self.targets["Specific Power Consumption"]:,.0f} kWh/ton)',
                    'impact': f'Extra power cost: ₹{(avg_power - self.targets["Specific Power Consumption"]) * furnace_data["Actual Production Qty"].sum() * 8 / 1000:,.0f}',
                    'recommendation': 'Optimize electrode control, improve power factor, reduce idle time',
                    'metric': 'Specific Power Consumption',
                    'value': avg_power,
                    'target': self.targets['Specific Power Consumption']
                })
    
    def _analyze_recovery(self):
        """Analyze material recovery rates"""
        if 'MN Recovery PLC' not in self.df.columns:
            return
        
        for furnace in self.df['Furnace'].unique():
            furnace_data = self.df[self.df['Furnace'] == furnace]
            avg_mn_recovery = furnace_data['MN Recovery PLC'].mean()
            
            if avg_mn_recovery < self.targets['MN Recovery PLC']:
                percent_below = ((self.targets['MN Recovery PLC'] - avg_mn_recovery) / 
                               self.targets['MN Recovery PLC']) * 100
                
                self.insights.append({
                    'type': 'recovery',
                    'severity': 'high' if percent_below > 5 else 'medium',
                    'furnace': furnace,
                    'title': f'Low Manganese Recovery - {furnace}',
                    'description': f'MN Recovery ({avg_mn_recovery:.1f}%) is {percent_below:.1f}% below target ({self.targets["MN Recovery PLC"]}%)',
                    'impact': f'Material loss: {(self.targets["MN Recovery PLC"] - avg_mn_recovery)/100 * furnace_data["MN Feeding"].sum() if "MN Feeding" in furnace_data.columns else "N/A":,.1f} tons',
                    'recommendation': 'Optimize temperature control, review slag basicity, check raw material quality',
                    'metric': 'MN Recovery PLC',
                    'value': avg_mn_recovery,
                    'target': self.targets['MN Recovery PLC']
                })
    
    def _analyze_operations(self):
        """Analyze operational metrics"""
        # Breakdown analysis
        if 'Total Breakdown Mins' in self.df.columns:
            total_breakdown = self.df['Total Breakdown Mins'].sum()
            avg_breakdown = self.df['Total Breakdown Mins'].mean()
            
            if avg_breakdown > 60:  # More than 1 hour average breakdown
                self.insights.append({
                    'type': 'operations',
                    'severity': 'high',
                    'title': 'High Breakdown Time',
                    'description': f'Average breakdown time: {avg_breakdown:.0f} minutes per day',
                    'impact': f'Total production loss: {total_breakdown/60 * self.df["Actual Production Qty"].mean()/24:,.1f} tons',
                    'recommendation': 'Implement preventive maintenance, improve maintenance scheduling'
                })
        
        # Load factor analysis
        if 'Load Factor' in self.df.columns:
            low_load_furnaces = []
            for furnace in self.df['Furnace'].unique():
                furnace_lf = self.df[self.df['Furnace'] == furnace]['Load Factor'].mean()
                if furnace_lf < self.targets['Load Factor']:
                    low_load_furnaces.append(furnace)
            
            if low_load_furnaces:
                self.insights.append({
                    'type': 'operations',
                    'severity': 'medium',
                    'title': 'Low Load Factor Detected',
                    'description': f'Furnaces with low load factor: {", ".join(low_load_furnaces)}',
                    'impact': 'Inefficient power usage, higher specific power consumption',
                    'recommendation': 'Optimize furnace loading, improve power management'
                })
    
    def _analyze_comparative(self):
        """Compare furnaces against each other"""
        if 'Furnace' not in self.df.columns or 'cost_per_ton' not in self.df.columns:
            return
        
        # Group by furnace
        furnace_stats = self.df.groupby('Furnace').agg({
            'cost_per_ton': 'mean',
            'Specific Power Consumption': 'mean',
            'MN Recovery PLC': 'mean',
            'Actual Production Qty': 'sum'
        }).round(2).reset_index()
        
        if len(furnace_stats) < 2:
            return
        
        # Find best and worst for cost
        best_cost = furnace_stats.loc[furnace_stats['cost_per_ton'].idxmin()]
        worst_cost = furnace_stats.loc[furnace_stats['cost_per_ton'].idxmax()]
        
        if worst_cost['cost_per_ton'] > best_cost['cost_per_ton'] * 1.1:  # 10% higher
            cost_gap_pct = ((worst_cost['cost_per_ton'] - best_cost['cost_per_ton']) / best_cost['cost_per_ton']) * 100
            
            self.insights.append({
                'type': 'comparative',
                'severity': 'high',
                'title': 'Significant Cost Variance Between Furnaces',
                'description': f'{worst_cost["Furnace"]} costs {cost_gap_pct:.1f}% more per ton than {best_cost["Furnace"]}',
                'impact': f'Potential savings by matching {best_cost["Furnace"]} performance: ₹{(worst_cost["cost_per_ton"] - best_cost["cost_per_ton"]) * worst_cost["Actual Production Qty"]:,.0f}',
                'recommendation': f'Benchmark practices from {best_cost["Furnace"]} to {worst_cost["Furnace"]}'
            })
        
        # Find best and worst for power
        if 'Specific Power Consumption' in furnace_stats.columns:
            best_power = furnace_stats.loc[furnace_stats['Specific Power Consumption'].idxmin()]
            worst_power = furnace_stats.loc[furnace_stats['Specific Power Consumption'].idxmax()]
            
            if worst_power['Specific Power Consumption'] > best_power['Specific Power Consumption'] * 1.15:  # 15% higher
                power_gap_pct = ((worst_power['Specific Power Consumption'] - best_power['Specific Power Consumption']) / 
                               best_power['Specific Power Consumption']) * 100
                
                self.insights.append({
                    'type': 'comparative',
                    'severity': 'medium',
                    'title': 'Power Efficiency Gap',
                    'description': f'{worst_power["Furnace"]} uses {power_gap_pct:.1f}% more power per ton than {best_power["Furnace"]}',
                    'impact': f'Extra power cost: ₹{(worst_power["Specific Power Consumption"] - best_power["Specific Power Consumption"]) * worst_power["Actual Production Qty"] * 8 / 1000:,.0f}',
                    'recommendation': f'Review electrical parameters and operating practices of {best_power["Furnace"]}'
                })
    
    def _categorize_insights(self) -> Dict[str, List[Dict]]:
        """Categorize insights by type"""
        categories = {
            'Cost Optimization': [],
            'Power Efficiency': [],
            'Material Recovery': [],
            'Operational Excellence': [],
            'Comparative Analysis': []
        }
        
        for insight in self.insights:
            insight_type = insight.get('type', '')
            
            if 'cost' in insight_type:
                categories['Cost Optimization'].append(insight)
            elif 'power' in insight_type:
                categories['Power Efficiency'].append(insight)
            elif 'recovery' in insight_type:
                categories['Material Recovery'].append(insight)
            elif 'operations' in insight_type or 'breakdown' in insight['title'].lower():
                categories['Operational Excellence'].append(insight)
            else:
                categories['Comparative Analysis'].append(insight)
        
        return categories
    
    def get_top_insights(self, limit: int = 10) -> List[Dict]:
        """Get top insights sorted by severity"""
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        
        sorted_insights = sorted(
            self.insights,
            key=lambda x: severity_order.get(x.get('severity', 'low'), 0),
            reverse=True
        )
        
        return sorted_insights[:limit]
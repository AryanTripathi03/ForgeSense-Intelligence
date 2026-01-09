# src/intelligence/insights_final.py - Final insights generator
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ProductionInsightsGenerator:
    """Generate production insights for furnace operations"""
    
    def __init__(self, processor):
        self.processor = processor
        self.df = processor.processed_df
        self.insights = []
        
        # Targets (can be customized)
        self.targets = {
            'cost_per_ton': 50000,
            'Specific Power Consumption': 2500,
            'MN Recovery PLC': 80,
            'SI Recovery PLC': 45,
            'yield_percentage': 95,
            'ore_efficiency': 0.55,
            'Load Factor': 85,
            'Power Factor': 0.95
        }
    
    def generate_all_insights(self) -> Dict[str, List[Dict]]:
        """Generate all insights for the data"""
        self.insights = []
        
        # Generate insights in order of importance
        self._generate_cost_insights()
        self._generate_power_insights()
        self._generate_recovery_insights()
        self._generate_quality_insights()
        self._generate_operational_insights()
        self._generate_comparative_insights()
        self._generate_trend_insights()
        
        # Categorize insights
        return self._categorize_insights()
    
    def _generate_cost_insights(self):
        """Generate cost-related insights"""
        if 'cost_per_ton' not in self.df.columns:
            return
        
        # Analyze each furnace
        furnace_summary = self.processor.get_furnace_summary()
        
        if furnace_summary.empty:
            return
        
        for _, furnace_row in furnace_summary.iterrows():
            furnace = furnace_row['Furnace']
            avg_cost = furnace_row.get('cost_per_ton_mean')
            
            if pd.isna(avg_cost):
                continue
            
            # Check against target
            target_cost = self.targets['cost_per_ton']
            
            if avg_cost > target_cost * 1.15:  # 15% above target
                percent_above = ((avg_cost - target_cost) / target_cost) * 100
                
                self.insights.append({
                    'category': 'cost',
                    'severity': 'high',
                    'furnace': furnace,
                    'title': f'High Operating Cost - {furnace}',
                    'description': f'Average cost per ton (₹{avg_cost:,.0f}) is {percent_above:.1f}% above target (₹{target_cost:,.0f})',
                    'impact': f'Estimated excess cost: ₹{(avg_cost - target_cost) * furnace_row.get("Actual Production Qty_sum", 0):,.0f}',
                    'recommendation': 'Review: 1) Raw material mix 2) Power optimization 3) Breakdown reduction',
                    'action_items': [
                        'Analyze ore-to-coke ratio',
                        'Check power consumption patterns',
                        'Review maintenance schedule'
                    ]
                })
        
        # Cost driver analysis
        cost_columns = ['Ore Cost PLC', 'Coke Cost PLC', 'Power Cost', 'Fluxes PLC']
        available_costs = [col for col in cost_columns if col in self.df.columns]
        
        if available_costs:
            total_costs = self.df[available_costs].sum()
            max_component = total_costs.idxmax()
            max_value = total_costs.max()
            total_all = total_costs.sum()
            
            if total_all > 0:
                percent = (max_value / total_all) * 100
                
                self.insights.append({
                    'category': 'cost',
                    'severity': 'medium',
                    'title': 'Primary Cost Driver Identified',
                    'description': f'{max_component} accounts for {percent:.1f}% of total production costs',
                    'impact': 'Targeted cost reduction in this area will have maximum impact',
                    'recommendation': f'Focus optimization efforts on {max_component.replace(" Cost PLC", "").lower()} usage',
                    'action_items': [
                        f'Analyze {max_component.replace(" Cost PLC", "").lower()} consumption patterns',
                        'Review supplier contracts',
                        'Explore alternative materials'
                    ]
                })
    
    def _generate_power_insights(self):
        """Generate power efficiency insights"""
        if 'Specific Power Consumption' not in self.df.columns:
            return
        
        furnace_summary = self.processor.get_furnace_summary()
        
        if furnace_summary.empty:
            return
        
        for _, furnace_row in furnace_summary.iterrows():
            furnace = furnace_row['Furnace']
            avg_power = furnace_row.get('Specific Power Consumption_mean')
            
            if pd.isna(avg_power):
                continue
            
            target_power = self.targets['Specific Power Consumption']
            
            if avg_power > target_power * 1.2:  # 20% above target
                percent_above = ((avg_power - target_power) / target_power) * 100
                
                # Check load factor
                load_factor = furnace_row.get('Load Factor_mean', 0) if 'Load Factor_mean' in furnace_row else 0
                
                self.insights.append({
                    'category': 'power',
                    'severity': 'medium',
                    'furnace': furnace,
                    'title': f'Power Efficiency Opportunity - {furnace}',
                    'description': f'Specific power ({avg_power:,.0f} kWh/MT) is {percent_above:.1f}% above target. Load Factor: {load_factor:.1f}%',
                    'impact': f'Extra power cost: ₹{(avg_power - target_power) * furnace_row.get("Actual Production Qty_sum", 0) * 8 / 1000:,.0f}',
                    'recommendation': 'Optimize: 1) Electrode control 2) Power factor 3) Load management',
                    'action_items': [
                        'Review electrode positioning',
                        'Check power factor correction',
                        'Optimize furnace loading pattern'
                    ]
                })
    
    def _generate_recovery_insights(self):
        """Generate material recovery insights"""
        for recovery_metric in ['MN Recovery PLC', 'SI Recovery PLC']:
            if recovery_metric not in self.df.columns:
                continue
            
            furnace_summary = self.processor.get_furnace_summary()
            
            if furnace_summary.empty:
                continue
            
            target_key = recovery_metric.replace(' PLC', '')
            target_value = self.targets.get(target_key)
            
            if not target_value:
                continue
            
            for _, furnace_row in furnace_summary.iterrows():
                furnace = furnace_row['Furnace']
                avg_recovery = furnace_row.get(f'{recovery_metric}_mean')
                
                if pd.isna(avg_recovery):
                    continue
                
                if avg_recovery < target_value * 0.9:  # 10% below target
                    percent_below = ((target_value - avg_recovery) / target_value) * 100
                    material = 'Manganese' if 'MN' in recovery_metric else 'Silicon'
                    
                    self.insights.append({
                        'category': 'recovery',
                        'severity': 'high',
                        'furnace': furnace,
                        'title': f'Low {material} Recovery - {furnace}',
                        'description': f'{material} recovery ({avg_recovery:.1f}%) is {percent_below:.1f}% below target ({target_value}%)',
                        'impact': f'Material loss affecting product quality and cost',
                        'recommendation': f'Optimize {material.lower()} recovery through temperature and slag control',
                        'action_items': [
                            'Review furnace temperature profile',
                            'Adjust slag basicity',
                            'Check raw material quality'
                        ]
                    })
    
    def _generate_quality_insights(self):
        """Generate product quality insights"""
        quality_params = {
            'Grade MN': {'target': 70, 'min': 65, 'max': 75},
            'Grade SI': {'target': 17.5, 'min': 15, 'max': 20},
            'C%': {'target': 7, 'min': 6, 'max': 8},
            'Basicity': {'target': 1.35, 'min': 1.2, 'max': 1.5}
        }
        
        for param, ranges in quality_params.items():
            if param not in self.df.columns:
                continue
            
            # Find out-of-spec data
            out_of_spec = self.df[
                (self.df[param] < ranges['min']) | 
                (self.df[param] > ranges['max'])
            ]
            
            if len(out_of_spec) > 0:
                percent_out = (len(out_of_spec) / len(self.df)) * 100
                
                self.insights.append({
                    'category': 'quality',
                    'severity': 'medium',
                    'title': f'{param} Out of Specification',
                    'description': f'{percent_out:.1f}% of readings outside optimal range ({ranges["min"]}-{ranges["max"]})',
                    'impact': 'Potential product quality issues and customer complaints',
                    'recommendation': 'Review and adjust process parameters to maintain quality standards',
                    'action_items': [
                        f'Monitor {param} closely',
                        'Adjust raw material mix',
                        'Review process control settings'
                    ]
                })
    
    def _generate_operational_insights(self):
        """Generate operational insights"""
        # Breakdown analysis
        if 'Total Breakdown Mins' in self.df.columns:
            total_breakdown = self.df['Total Breakdown Mins'].sum()
            avg_breakdown = self.df['Total Breakdown Mins'].mean()
            
            if avg_breakdown > 60:  # More than 1 hour average
                self.insights.append({
                    'category': 'operations',
                    'severity': 'high',
                    'title': 'High Breakdown Time Impacting Production',
                    'description': f'Average daily breakdown: {avg_breakdown:.0f} minutes',
                    'impact': f'Estimated production loss: {total_breakdown/60 * self.df["Actual Production Qty"].mean()/24:,.1f} MT',
                    'recommendation': 'Implement preventive maintenance program and reduce unplanned stops',
                    'action_items': [
                        'Review breakdown causes',
                        'Implement preventive maintenance schedule',
                        'Train operators on quick changeovers'
                    ]
                })
    
    def _generate_comparative_insights(self):
        """Generate comparative insights between furnaces"""
        if 'Furnace' not in self.df.columns:
            return
        
        furnace_summary = self.processor.get_furnace_summary()
        
        if len(furnace_summary) < 2:
            return
        
        # Cost comparison
        if 'cost_per_ton_mean' in furnace_summary.columns:
            worst_cost = furnace_summary.loc[furnace_summary['cost_per_ton_mean'].idxmax()]
            best_cost = furnace_summary.loc[furnace_summary['cost_per_ton_mean'].idxmin()]
            
            if worst_cost['cost_per_ton_mean'] > best_cost['cost_per_ton_mean'] * 1.1:
                gap_percent = ((worst_cost['cost_per_ton_mean'] - best_cost['cost_per_ton_mean']) / 
                             best_cost['cost_per_ton_mean']) * 100
                
                self.insights.append({
                    'category': 'comparative',
                    'severity': 'high',
                    'title': 'Significant Cost Performance Gap',
                    'description': f'{worst_cost["Furnace"]} costs {gap_percent:.1f}% more per ton than {best_cost["Furnace"]}',
                    'impact': f'Opportunity: ₹{(worst_cost["cost_per_ton_mean"] - best_cost["cost_per_ton_mean"]) * worst_cost.get("Actual Production Qty_sum", 0):,.0f}',
                    'recommendation': f'Benchmark best practices from {best_cost["Furnace"]} to {worst_cost["Furnace"]}',
                    'action_items': [
                        f'Compare operating parameters between {best_cost["Furnace"]} and {worst_cost["Furnace"]}',
                        'Share best practices across teams',
                        'Standardize operating procedures'
                    ]
                })
    
    def _generate_trend_insights(self):
        """Generate trend-based insights"""
        if 'DATE' not in self.df.columns or 'cost_per_ton' not in self.df.columns:
            return
        
        # Check for trends in cost
        self.df = self.df.sort_values('DATE')
        
        if len(self.df) >= 7:
            recent_avg = self.df.tail(7)['cost_per_ton'].mean()
            previous_avg = self.df.iloc[-14:-7]['cost_per_ton'].mean() if len(self.df) >= 14 else self.df.iloc[:-7]['cost_per_ton'].mean()
            
            if previous_avg > 0:
                trend = ((recent_avg - previous_avg) / previous_avg) * 100
                
                if trend > 10:  # 10% increase
                    self.insights.append({
                        'category': 'trend',
                        'severity': 'medium',
                        'title': 'Recent Cost Increase Trend',
                        'description': f'Cost per ton increased by {trend:.1f}% in the last week',
                        'impact': 'If trend continues, will impact monthly profitability',
                        'recommendation': 'Investigate recent cost increases and take corrective action',
                        'action_items': [
                            'Review recent raw material purchases',
                            'Check for equipment issues',
                            'Analyze power consumption trends'
                        ]
                    })
    
    def _categorize_insights(self) -> Dict[str, List[Dict]]:
        """Categorize insights for display"""
        categories = {
            'Cost Optimization': [],
            'Power Efficiency': [],
            'Material Recovery': [],
            'Product Quality': [],
            'Operations Management': [],
            'Performance Benchmarking': [],
            'Trend Analysis': []
        }
        
        category_mapping = {
            'cost': 'Cost Optimization',
            'power': 'Power Efficiency',
            'recovery': 'Material Recovery',
            'quality': 'Product Quality',
            'operations': 'Operations Management',
            'comparative': 'Performance Benchmarking',
            'trend': 'Trend Analysis'
        }
        
        for insight in self.insights:
            category = category_mapping.get(insight.get('category', ''), 'Operations Management')
            categories[category].append(insight)
        
        # Sort insights within each category by severity
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        
        for category in categories:
            categories[category].sort(
                key=lambda x: severity_order.get(x.get('severity', 'low'), 0),
                reverse=True
            )
        
        return categories
    
    def get_priority_insights(self, limit: int = 5) -> List[Dict]:
        """Get highest priority insights"""
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        
        sorted_insights = sorted(
            self.insights,
            key=lambda x: (severity_order.get(x.get('severity', 'low'), 0), 
                          x.get('category', '')),
            reverse=True
        )
        
        return sorted_insights[:limit]
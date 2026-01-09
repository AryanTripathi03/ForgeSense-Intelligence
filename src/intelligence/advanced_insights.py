# src/intelligence/advanced_insights.py - Advanced, accurate insights
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class AdvancedInsightsEngine:
    """Generate accurate, actionable insights for furnace operations"""
    
    def __init__(self, calculator, capacities: Dict[str, dict]):
        """
        Initialize insights engine
        
        Args:
            calculator: CapacityCalculator instance
            capacities: Dictionary of furnace capacities
        """
        self.calculator = calculator
        self.capacities = capacities
        self.df = calculator.df
        self.insights = []
    
    def generate_all_insights(self) -> Dict[str, List[Dict]]:
        """Generate all insights categorized by priority"""
        self.insights = []
        
        # Generate insights in priority order
        self._generate_capacity_insights()
        self._generate_cost_insights()
        self._generate_power_insights()
        self._generate_recovery_insights()
        self._generate_quality_insights()
        self._generate_operational_insights()
        self._generate_comparative_insights()
        
        # Categorize and prioritize
        return self._categorize_insights()
    
    def _generate_capacity_insights(self):
        """Generate insights based on furnace capacity utilization"""
        comparative = self.calculator.get_comparative_analysis()
        
        if comparative.empty:
            return
        
        for _, row in comparative.iterrows():
            furnace = row['furnace']
            capacity_util = row.get('capacity_utilization', 0)
            design_capacity = row.get('design_capacity_mt', 0)
            avg_production = row.get('avg_daily_production', 0)
            
            # Low capacity utilization
            if capacity_util < 70:
                self.insights.append({
                    'category': 'capacity',
                    'severity': 'high',
                    'furnace': furnace,
                    'title': f'Low Capacity Utilization - {furnace}',
                    'description': f'Operating at {capacity_util:.1f}% of design capacity ({avg_production:.1f} MT/day vs {design_capacity:.1f} MT/day)',
                    'impact': f'Underutilization leads to higher fixed costs per ton',
                    'recommendation': f'Increase throughput or optimize batch sizing',
                    'financial_impact': f'Potential loss: ₹{(design_capacity - avg_production) * 50000 * 30:,.0f}/month',
                    'confidence': 'high',
                    'data_points': [
                        f'Design capacity: {design_capacity:.1f} MT/day',
                        f'Actual average: {avg_production:.1f} MT/day',
                        f'Utilization: {capacity_util:.1f}%'
                    ]
                })
            
            # Very high utilization (potential overloading)
            elif capacity_util > 110:
                self.insights.append({
                    'category': 'capacity',
                    'severity': 'medium',
                    'furnace': furnace,
                    'title': f'Potential Overloading - {furnace}',
                    'description': f'Operating at {capacity_util:.1f}% of design capacity',
                    'impact': f'Risk of equipment stress and reduced lifespan',
                    'recommendation': f'Monitor equipment parameters and schedule maintenance',
                    'confidence': 'medium',
                    'data_points': [f'Utilization: {capacity_util:.1f}%']
                })
    
    def _generate_cost_insights(self):
        """Generate cost optimization insights"""
        for furnace_id, capacity in self.capacities.items():
            perf = self.calculator.get_furnace_performance(furnace_id)
            
            if not perf:
                continue
            
            current_cost = perf.get('avg_cost_mt', 0)
            target_cost = capacity.target_cost_mt
            cost_vs_target = perf.get('cost_vs_target', 0)
            
            # High cost furnace
            if cost_vs_target > 15:  # 15% above target
                cost_drivers = self.calculator.identify_cost_drivers(furnace_id)
                
                # Find main cost driver
                main_driver = None
                main_percentage = 0
                for driver, data in cost_drivers.items():
                    if data['percentage'] > main_percentage:
                        main_percentage = data['percentage']
                        main_driver = driver
                
                insight_desc = f'Cost per ton (₹{current_cost:,.0f}) is {cost_vs_target:.1f}% above target (₹{target_cost:,.0f})'
                
                if main_driver:
                    insight_desc += f'. {main_driver} accounts for {main_percentage:.1f}% of total cost'
                
                self.insights.append({
                    'category': 'cost',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'High Production Cost - {furnace_id}',
                    'description': insight_desc,
                    'impact': f'Excess cost: ₹{(current_cost - target_cost) * perf.get("total_production", 0):,.0f}',
                    'recommendation': f'Focus on optimizing {main_driver.replace(" Cost PLC", "").lower() if main_driver else "raw material"} usage',
                    'financial_impact': f'Potential monthly savings: ₹{(current_cost - target_cost) * perf.get("avg_daily_production", 0) * 30:,.0f}',
                    'confidence': 'high',
                    'action_items': [
                        'Review raw material consumption patterns',
                        'Optimize power usage during peak hours',
                        'Reduce material wastage in process'
                    ]
                })
    
    def _generate_power_insights(self):
        """Generate power efficiency insights"""
        for furnace_id, capacity in self.capacities.items():
            perf = self.calculator.get_furnace_performance(furnace_id)
            
            if not perf:
                continue
            
            current_power = perf.get('avg_power_mt', 0)
            optimal_power = capacity.optimal_power_kwh_mt
            power_vs_optimal = perf.get('power_vs_optimal', 0)
            
            if power_vs_optimal > 20:  # 20% above optimal
                self.insights.append({
                    'category': 'power',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'High Power Consumption - {furnace_id}',
                    'description': f'Power consumption ({current_power:,.0f} kWh/MT) is {power_vs_optimal:.1f}% above optimal ({optimal_power:,.0f} kWh/MT)',
                    'impact': f'Extra power cost: ₹{(current_power - optimal_power) * perf.get("total_production", 0) * 8 / 1000:,.0f}',
                    'recommendation': 'Optimize electrode control and improve power factor',
                    'confidence': 'high',
                    'action_items': [
                        'Check electrode positioning and length',
                        'Review power factor correction equipment',
                        'Optimize furnace load distribution'
                    ]
                })
            
            # Check load factor
            load_factor = perf.get('avg_load_factor', 0)
            if load_factor < 75:
                self.insights.append({
                    'category': 'power',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Low Load Factor - {furnace_id}',
                    'description': f'Load factor ({load_factor:.1f}%) indicates inefficient power usage',
                    'impact': 'Higher specific power consumption and increased costs',
                    'recommendation': 'Optimize batch scheduling to improve load factor',
                    'confidence': 'medium'
                })
    
    def _generate_recovery_insights(self):
        """Generate material recovery insights"""
        for furnace_id, capacity in self.capacities.items():
            perf = self.calculator.get_furnage_performance(furnace_id)
            
            if not perf:
                continue
            
            current_mn = perf.get('avg_mn_recovery', 0)
            target_mn = capacity.target_mn_recovery
            mn_gap = perf.get('mn_recovery_gap', 0)
            
            if mn_gap > 5:  # 5% below target
                # Analyze potential causes
                causes = []
                furnace_data = self.df[self.df['Furnace'] == furnace_id]
                
                if 'Basicity' in furnace_data.columns:
                    avg_basicity = furnace_data['Basicity'].mean()
                    if avg_basicity < 1.2 or avg_basicity > 1.5:
                        causes.append(f'Slag basicity ({avg_basicity:.2f}) outside optimal range (1.2-1.5)')
                
                if 'MnO%' in furnace_data.columns:
                    avg_mno = furnace_data['MnO%'].mean()
                    if avg_mno > 15:
                        causes.append(f'High MnO in slag ({avg_mno:.1f}%) indicates manganese loss')
                
                cause_text = 'Possible causes: ' + ', '.join(causes) if causes else ''
                
                self.insights.append({
                    'category': 'recovery',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'Low Manganese Recovery - {furnace_id}',
                    'description': f'MN recovery ({current_mn:.1f}%) is {mn_gap:.1f}% below target ({target_mn}%) {cause_text}',
                    'impact': f'Material loss: {(mn_gap/100) * furnace_data["MN Feeding"].sum() if "MN Feeding" in furnace_data.columns else "Significant"} tons',
                    'recommendation': 'Optimize temperature profile and slag chemistry',
                    'confidence': 'high',
                    'action_items': [
                        'Adjust furnace temperature setpoints',
                        'Optimize slag basicity (target: 1.2-1.5)',
                        'Review raw material Mn content'
                    ]
                })
    
    def _generate_quality_insights(self):
        """Generate product quality insights"""
        quality_params = {
            'Grade MN': {'optimal': (68, 72), 'critical': (65, 75)},
            'Grade SI': {'optimal': (16, 18), 'critical': (15, 20)},
            'C%': {'optimal': (6.5, 7.5), 'critical': (6, 8)},
            'Basicity': {'optimal': (1.3, 1.4), 'critical': (1.2, 1.5)}
        }
        
        for furnace_id in self.capacities.keys():
            furnace_data = self.df[self.df['Furnace'] == furnace_id]
            
            for param, ranges in quality_params.items():
                if param in furnace_data.columns:
                    avg_value = furnace_data[param].mean()
                    
                    # Check if outside optimal range
                    if avg_value < ranges['optimal'][0] or avg_value > ranges['optimal'][1]:
                        severity = 'medium'
                        
                        # Check if outside critical range
                        if avg_value < ranges['critical'][0] or avg_value > ranges['critical'][1]:
                            severity = 'high'
                        
                        deviation = min(
                            abs(avg_value - ranges['optimal'][0]),
                            abs(avg_value - ranges['optimal'][1])
                        )
                        
                        self.insights.append({
                            'category': 'quality',
                            'severity': severity,
                            'furnace': furnace_id,
                            'title': f'{param} Deviation - {furnace_id}',
                            'description': f'{param} ({avg_value:.2f}) outside optimal range ({ranges["optimal"][0]}-{ranges["optimal"][1]})',
                            'impact': 'Potential quality issues and customer complaints',
                            'recommendation': f'Adjust process parameters to bring {param} within optimal range',
                            'confidence': 'high',
                            'action_items': [
                                f'Monitor {param} closely for next batch',
                                'Review raw material quality',
                                'Adjust process setpoints'
                            ]
                        })
    
    def _generate_operational_insights(self):
        """Generate operational efficiency insights"""
        for furnace_id in self.capacities.keys():
            furnace_data = self.df[self.df['Furnace'] == furnace_id]
            
            # Breakdown analysis
            if 'Total Breakdown Mins' in furnace_data.columns:
                avg_breakdown = furnace_data['Total Breakdown Mins'].mean()
                
                if avg_breakdown > 120:  # More than 2 hours average
                    # Analyze breakdown types
                    breakdown_types = {}
                    for col in ['Mechanical B/D Mins', 'Electrical B/D Mins', 'Production B/D Mins']:
                        if col in furnace_data.columns:
                            breakdown_types[col] = furnace_data[col].mean()
                    
                    main_cause = max(breakdown_types, key=breakdown_types.get) if breakdown_types else 'Unknown'
                    
                    self.insights.append({
                        'category': 'operations',
                        'severity': 'high',
                        'furnace': furnace_id,
                        'title': f'High Breakdown Time - {furnace_id}',
                        'description': f'Average {avg_breakdown:.0f} minutes downtime per day ({main_cause.replace(" B/D Mins", "")} issues dominant)',
                        'impact': f'Production loss: {avg_breakdown/60 * furnace_data["Actual Production Qty"].mean()/24:.1f} tons/day',
                        'recommendation': f'Implement preventive maintenance program focusing on {main_cause.replace(" B/D Mins", "").lower()}',
                        'confidence': 'high',
                        'action_items': [
                            'Schedule immediate maintenance',
                            'Implement root cause analysis',
                            'Train operators on quick troubleshooting'
                        ]
                    })
    
    def _generate_comparative_insights(self):
        """Generate comparative insights between furnaces"""
        comparative = self.calculator.get_comparative_analysis()
        
        if len(comparative) < 2:
            return
        
        # Find best and worst performers for key metrics
        metrics_comparison = {
            'avg_cost_mt': 'Cost per Ton',
            'avg_power_mt': 'Power Consumption',
            'avg_mn_recovery': 'MN Recovery',
            'capacity_utilization': 'Capacity Utilization'
        }
        
        for metric, display_name in metrics_comparison.items():
            if metric in comparative.columns:
                best_idx = comparative[metric].idxmin() if metric in ['avg_cost_mt', 'avg_power_mt'] else comparative[metric].idxmax()
                worst_idx = comparative[metric].idxmax() if metric in ['avg_cost_mt', 'avg_power_mt'] else comparative[metric].idxmin()
                
                best_furnace = comparative.iloc[best_idx]
                worst_furnace = comparative.iloc[worst_idx]
                
                if metric in ['avg_cost_mt', 'avg_power_mt']:
                    # Lower is better
                    gap_pct = ((worst_furnace[metric] - best_furnace[metric]) / best_furnace[metric]) * 100
                    if gap_pct > 20:  # 20% gap
                        self.insights.append({
                            'category': 'comparative',
                            'severity': 'high',
                            'title': f'{display_name} Performance Gap',
                            'description': f'{worst_furnace["furnace"]} has {gap_pct:.1f}% higher {display_name.lower()} than {best_furnace["furnace"]}',
                            'impact': f'Opportunity to match {best_furnace["furnace"]} performance',
                            'recommendation': f'Benchmark operating parameters from {best_furnace["furnace"]} to {worst_furnace["furnace"]}',
                            'confidence': 'high',
                            'action_items': [
                                f'Compare operating parameters between {best_furnace["furnace"]} and {worst_furnace["furnace"]}',
                                'Share best practices across teams',
                                'Standardize operating procedures'
                            ]
                        })
    
    def _categorize_insights(self) -> Dict[str, List[Dict]]:
        """Categorize insights by priority"""
        categories = {
            '🚨 Critical Issues': [],
            '💰 Cost Optimization': [],
            '⚡ Power Efficiency': [],
            '🔬 Material Recovery': [],
            '🎯 Quality Control': [],
            '🏭 Operations': [],
            '📊 Performance Benchmarking': []
        }
        
        # First, identify critical issues (multiple high-severity problems)
        furnace_issues = {}
        for insight in self.insights:
            if insight.get('severity') == 'high':
                furnace = insight.get('furnace', 'General')
                if furnace not in furnace_issues:
                    furnace_issues[furnace] = []
                furnace_issues[furnace].append(insight)
        
        # Create critical issues for furnaces with multiple high-severity problems
        for furnace, issues in furnace_issues.items():
            if len(issues) >= 2 and furnace != 'General':
                self.insights.append({
                    'category': 'critical',
                    'severity': 'high',
                    'furnace': furnace,
                    'title': f'⚠️ Multiple Critical Issues - {furnace}',
                    'description': f'{furnace} has {len(issues)} high-priority issues requiring immediate attention',
                    'impact': 'Significant impact on production cost and quality',
                    'recommendation': 'Prioritize corrective actions for this furnace',
                    'confidence': 'high',
                    'action_items': [f'Address {len(issues)} identified issues']
                })
        
        # Categorize all insights
        for insight in self.insights:
            category = insight.get('category', 'operations')
            
            if insight.get('severity') == 'high' and category != 'critical':
                categories['🚨 Critical Issues'].append(insight)
            elif category == 'cost':
                categories['💰 Cost Optimization'].append(insight)
            elif category == 'power':
                categories['⚡ Power Efficiency'].append(insight)
            elif category == 'recovery':
                categories['🔬 Material Recovery'].append(insight)
            elif category == 'quality':
                categories['🎯 Quality Control'].append(insight)
            elif category == 'capacity' or category == 'operations':
                categories['🏭 Operations'].append(insight)
            elif category == 'comparative':
                categories['📊 Performance Benchmarking'].append(insight)
            else:
                categories['🏭 Operations'].append(insight)
        
        # Sort insights within each category
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        for category in categories:
            categories[category].sort(
                key=lambda x: (severity_order.get(x.get('severity', 'low'), 0), 
                              x.get('financial_impact', 0) if 'financial_impact' in x else 0),
                reverse=True
            )
        
        return categories
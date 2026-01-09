# src/intelligence/comprehensive_insights.py - Comprehensive insights for all parameters
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ComprehensiveInsightsEngine:
    """Generate comprehensive insights for ALL furnace parameters"""
    
    def __init__(self, analyzer, capacities: Dict[str, float]):
        """
        Initialize insights engine
        
        Args:
            analyzer: CompleteFurnaceAnalyzer instance
            capacities: Dict of furnace_id -> MVA capacity (only user input)
        """
        self.analyzer = analyzer
        self.capacities = capacities
        self.data = analyzer.get_comprehensive_insights_data()
        self.targets = analyzer.targets
        self.insights = []
        
        # Calculate capacity-based metrics
        self._calculate_capacity_metrics()
    
    def _calculate_capacity_metrics(self):
        """Calculate capacity-based metrics from MVA input"""
        self.capacity_metrics = {}
        
        for furnace_id, mva_capacity in self.capacities.items():
            if furnace_id in self.data['furnace_analysis']:
                furnace_data = self.data['furnace_analysis'][furnace_id]
                avg_daily_prod = furnace_data.get('avg_daily_production', 0)
                
                # Estimate design capacity from data (90th percentile of daily production)
                furnace_records = self.analyzer.processed_df[self.analyzer.processed_df['Furnace'] == furnace_id]
                if len(furnace_records) > 0:
                    design_capacity = furnace_records.groupby('DATE')['Actual Production Qty'].sum().quantile(0.9)
                else:
                    design_capacity = avg_daily_prod * 1.2  # 20% above average
                
                self.capacity_metrics[furnace_id] = {
                    'mva_capacity': mva_capacity,
                    'design_capacity_mt': design_capacity,
                    'current_utilization': (avg_daily_prod / design_capacity * 100) if design_capacity > 0 else 0,
                    'mva_per_mt': mva_capacity / avg_daily_prod if avg_daily_prod > 0 else 0,
                }
    
    def generate_all_insights(self) -> Dict[str, List[Dict]]:
        """Generate comprehensive insights for ALL parameters"""
        self.insights = []
        
        # Generate insights in logical order
        self._generate_capacity_insights()
        self._generate_production_insights()
        self._generate_cost_insights()
        self._generate_power_insights()
        self._generate_recovery_insights()
        self._generate_quality_insights()
        self._generate_efficiency_insights()
        self._generate_operational_insights()
        self._generate_grade_based_insights()
        self._generate_comparative_insights()
        self._generate_trend_insights()
        
        # Categorize and prioritize
        return self._categorize_insights()
    
    def _generate_capacity_insights(self):
        """Generate capacity utilization insights"""
        for furnace_id, metrics in self.capacity_metrics.items():
            utilization = metrics['current_utilization']
            
            if utilization < 70:
                self.insights.append({
                    'category': 'capacity',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'Low Capacity Utilization - {furnace_id}',
                    'description': f'Operating at {utilization:.1f}% of estimated design capacity ({metrics["design_capacity_mt"]:.1f} MT/day)',
                    'impact': 'High fixed cost per ton, inefficient resource usage',
                    'recommendation': 'Increase throughput or optimize production scheduling',
                    'data': {
                        'MVA Capacity': f'{metrics["mva_capacity"]} MVA',
                        'Design Capacity': f'{metrics["design_capacity_mt"]:.1f} MT/day',
                        'Current Utilization': f'{utilization:.1f}%'
                    }
                })
            elif utilization > 110:
                self.insights.append({
                    'category': 'capacity',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Potential Overloading - {furnace_id}',
                    'description': f'Operating at {utilization:.1f}% of design capacity',
                    'impact': 'Risk of equipment stress and quality issues',
                    'recommendation': 'Monitor equipment parameters and schedule preventive maintenance',
                    'data': {
                        'Utilization': f'{utilization:.1f}%',
                        'MVA per MT': f'{metrics["mva_per_mt"]:.3f}'
                    }
                })
    
    def _generate_production_insights(self):
        """Generate production-related insights"""
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            # Check yield percentage
            yield_pct = analysis.get('avg_yield', 0)
            target_yield = self.targets.get('Yield_Percentage', 95)
            
            if yield_pct < target_yield - 5:  # 5% below target
                self.insights.append({
                    'category': 'production',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'Low Yield Percentage - {furnace_id}',
                    'description': f'Yield ({yield_pct:.1f}%) is below target ({target_yield}%)',
                    'impact': 'Material wastage and increased production cost',
                    'recommendation': 'Optimize tapping process and reduce metal loss in slag',
                    'data': {
                        'Current Yield': f'{yield_pct:.1f}%',
                        'Target Yield': f'{target_yield}%',
                        'Gap': f'{target_yield - yield_pct:.1f}%'
                    }
                })
            
            # Check production consistency
            cost_std = analysis.get('cost_std_dev', 0)
            avg_cost = analysis.get('avg_cost_per_ton', 0)
            
            if avg_cost > 0 and (cost_std / avg_cost) > 0.2:  # High variation (20%+)
                self.insights.append({
                    'category': 'production',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'High Cost Variation - {furnace_id}',
                    'description': f'Cost per ton varies significantly (Std Dev: ₹{cost_std:,.0f})',
                    'impact': 'Unpredictable production costs and planning challenges',
                    'recommendation': 'Standardize operating procedures and raw material quality',
                    'data': {
                        'Average Cost': f'₹{avg_cost:,.0f}/MT',
                        'Standard Deviation': f'₹{cost_std:,.0f}',
                        'Variation Coefficient': f'{(cost_std/avg_cost*100):.1f}%'
                    }
                })
    
    def _generate_cost_insights(self):
        """Generate cost optimization insights"""
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            current_cost = analysis.get('avg_cost_per_ton', 0)
            target_cost = self.targets.get('Cost_per_Ton', 50000)
            
            if current_cost > target_cost * 1.15:  # 15% above target
                cost_drivers = analysis.get('cost_breakdown', {})
                
                # Find main cost driver
                main_driver = None
                main_percentage = 0
                for driver, data in cost_drivers.items():
                    if data['percentage'] > main_percentage:
                        main_percentage = data['percentage']
                        main_driver = driver
                
                self.insights.append({
                    'category': 'cost',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'High Production Cost - {furnace_id}',
                    'description': f'Cost per ton (₹{current_cost:,.0f}) is {((current_cost/target_cost - 1)*100):.1f}% above target. {main_driver if main_driver else "Raw material"} is main driver ({main_percentage:.1f}%)',
                    'impact': f'Excess cost: ₹{(current_cost - target_cost) * analysis.get("total_production", 0):,.0f}',
                    'recommendation': f'Focus on optimizing {main_driver.lower() if main_driver else "raw material"} consumption and sourcing',
                    'financial_impact': f'Potential monthly savings: ₹{(current_cost - target_cost) * analysis.get("avg_daily_production", 0) * 30:,.0f}',
                    'data': {
                        'Current Cost': f'₹{current_cost:,.0f}/MT',
                        'Target Cost': f'₹{target_cost:,.0f}/MT',
                        'Main Cost Driver': f'{main_driver} ({main_percentage:.1f}%)' if main_driver else 'N/A'
                    }
                })
    
    def _generate_power_insights(self):
        """Generate power efficiency insights"""
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            current_power = analysis.get('avg_power_consumption', 0)
            target_power = self.targets.get('Specific_Power_Consumption', 2500)
            
            if current_power > target_power * 1.2:  # 20% above target
                load_factor = analysis.get('avg_load_factor', 0)
                power_factor = analysis.get('avg_power_factor', 0)
                
                self.insights.append({
                    'category': 'power',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'High Power Consumption - {furnace_id}',
                    'description': f'Power consumption ({current_power:,.0f} kWh/MT) is {((current_power/target_power - 1)*100):.1f}% above target. Load Factor: {load_factor:.1f}%, Power Factor: {power_factor:.3f}',
                    'impact': f'Extra power cost: ₹{(current_power - target_power) * analysis.get("total_production", 0) * 8 / 1000:,.0f}',
                    'recommendation': 'Optimize electrode control and improve power factor',
                    'data': {
                        'Current Power': f'{current_power:,.0f} kWh/MT',
                        'Target Power': f'{target_power:,.0f} kWh/MT',
                        'Load Factor': f'{load_factor:.1f}%',
                        'Power Factor': f'{power_factor:.3f}'
                    }
                })
            
            # Check power factor
            if power_factor < 0.9:
                self.insights.append({
                    'category': 'power',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Low Power Factor - {furnace_id}',
                    'description': f'Power factor ({power_factor:.3f}) below optimal (0.95+)',
                    'impact': 'Inefficient power usage and potential penalty charges',
                    'recommendation': 'Install or optimize power factor correction equipment',
                    'data': {
                        'Current Power Factor': f'{power_factor:.3f}',
                        'Recommended': '> 0.95'
                    }
                })
    
    def _generate_recovery_insights(self):
        """Generate material recovery insights"""
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            # Manganese Recovery
            current_mn = analysis.get('avg_mn_recovery', 0)
            target_mn = self.targets.get('MN_Recovery_PLC', 80)
            
            if current_mn < target_mn - 5:  # 5% below target
                mn_gap = analysis.get('avg_mn_recovery_gap', 0)
                basicity = analysis.get('avg_basicity', 0)
                
                cause_analysis = []
                if basicity < 1.2 or basicity > 1.5:
                    cause_analysis.append(f'Slag basicity ({basicity:.2f}) outside optimal range (1.2-1.5)')
                if mn_gap < -2:
                    cause_analysis.append(f'Large gap between PLC ({current_mn:.1f}%) and Feeding recovery')
                
                cause_text = ' | '.join(cause_analysis) if cause_analysis else 'Review process parameters'
                
                self.insights.append({
                    'category': 'recovery',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'Low Manganese Recovery - {furnace_id}',
                    'description': f'MN recovery ({current_mn:.1f}%) is {target_mn - current_mn:.1f}% below target. {cause_text}',
                    'impact': 'Significant material loss affecting product yield and cost',
                    'recommendation': 'Optimize temperature control and slag chemistry',
                    'data': {
                        'Current Recovery': f'{current_mn:.1f}%',
                        'Target Recovery': f'{target_mn}%',
                        'Slag Basicity': f'{basicity:.2f}',
                        'Recovery Gap (PLC-Feeding)': f'{mn_gap:.1f}%'
                    }
                })
            
            # Silicon Recovery (if data available)
            current_si = analysis.get('avg_si_recovery', 0)
            if current_si > 0:  # Data available
                target_si = self.targets.get('SI_Recovery_PLC', 45)
                if current_si < target_si - 5:
                    self.insights.append({
                        'category': 'recovery',
                        'severity': 'medium',
                        'furnace': furnace_id,
                        'title': f'Low Silicon Recovery - {furnace_id}',
                        'description': f'SI recovery ({current_si:.1f}%) is {target_si - current_si:.1f}% below target',
                        'impact': 'Silicon loss affecting ferroalloy quality',
                        'recommendation': 'Optimize furnace temperature and silicon content in charge',
                        'data': {
                            'Current Recovery': f'{current_si:.1f}%',
                            'Target Recovery': f'{target_si}%'
                        }
                    })
    
    def _generate_quality_insights(self):
        """Generate product quality insights"""
        quality_params = {
            'Grade MN': {'analysis_key': 'avg_grade_mn', 'optimal': (68, 72), 'critical': (65, 75)},
            'Grade SI': {'analysis_key': 'avg_grade_si', 'optimal': (16, 18), 'critical': (15, 20)},
            'C%': {'analysis_key': 'avg_carbon', 'optimal': (6.5, 7.5), 'critical': (6, 8)},
            'Basicity': {'analysis_key': 'avg_basicity', 'optimal': (1.3, 1.4), 'critical': (1.2, 1.5)},
        }
        
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            for param_name, param_info in quality_params.items():
                current_value = analysis.get(param_info['analysis_key'], 0)
                
                if current_value > 0:  # Valid data
                    # Check if outside optimal range
                    if current_value < param_info['optimal'][0] or current_value > param_info['optimal'][1]:
                        severity = 'medium'
                        
                        # Check if outside critical range
                        if current_value < param_info['critical'][0] or current_value > param_info['critical'][1]:
                            severity = 'high'
                        
                        deviation = min(
                            abs(current_value - param_info['optimal'][0]),
                            abs(current_value - param_info['optimal'][1])
                        )
                        
                        self.insights.append({
                            'category': 'quality',
                            'severity': severity,
                            'furnace': furnace_id,
                            'title': f'{param_name} Deviation - {furnace_id}',
                            'description': f'{param_name} ({current_value:.2f}) outside optimal range ({param_info["optimal"][0]}-{param_info["optimal"][1]})',
                            'impact': 'Potential quality issues and customer specification violations',
                            'recommendation': f'Adjust raw material mix and process parameters for {param_name} control',
                            'data': {
                                'Current Value': f'{current_value:.2f}',
                                'Optimal Range': f'{param_info["optimal"][0]}-{param_info["optimal"][1]}',
                                'Deviation': f'{deviation:.2f}'
                            }
                        })
            
            # Overall quality score
            quality_score = analysis.get('avg_quality_score', 0)
            if quality_score < 70:
                self.insights.append({
                    'category': 'quality',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Low Overall Quality Score - {furnace_id}',
                    'description': f'Quality score ({quality_score:.1f}/100) indicates room for improvement',
                    'impact': 'Consistent quality issues affecting product acceptance',
                    'recommendation': 'Review all quality parameters and implement corrective actions',
                    'data': {
                        'Quality Score': f'{quality_score:.1f}/100',
                        'Target Score': '> 85'
                    }
                })
    
    def _generate_efficiency_insights(self):
        """Generate efficiency insights"""
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            # Ore Efficiency
            ore_eff = analysis.get('avg_ore_efficiency', 0)
            target_ore_eff = self.targets.get('Ore_Efficiency', 0.55)
            
            if ore_eff < target_ore_eff * 0.9:  # 10% below target
                self.insights.append({
                    'category': 'efficiency',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Low Ore Efficiency - {furnace_id}',
                    'description': f'Ore efficiency ({ore_eff:.3f} MT/MT) below target ({target_ore_eff:.3f})',
                    'impact': 'Higher ore consumption per ton of production',
                    'recommendation': 'Optimize ore mix and reduce fines generation',
                    'data': {
                        'Current Efficiency': f'{ore_eff:.3f} MT/MT',
                        'Target Efficiency': f'{target_ore_eff:.3f} MT/MT'
                    }
                })
            
            # Coke Efficiency
            coke_eff = analysis.get('avg_coke_efficiency', 0)
            target_coke_eff = self.targets.get('Coke_Efficiency', 4.0)
            
            if coke_eff > 0 and coke_eff < target_coke_eff * 0.9:
                self.insights.append({
                    'category': 'efficiency',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Low Coke Efficiency - {furnace_id}',
                    'description': f'Coke efficiency ({coke_eff:.2f} MT/MT) below target ({target_coke_eff:.2f})',
                    'impact': 'Higher coke consumption and cost',
                    'recommendation': 'Optimize coke quality and size distribution',
                    'data': {
                        'Current Efficiency': f'{coke_eff:.2f} MT/MT',
                        'Target Efficiency': f'{target_coke_eff:.2f} MT/MT'
                    }
                })
    
    def _generate_operational_insights(self):
        """Generate operational insights"""
        for furnace_id, analysis in self.data['furnace_analysis'].items():
            # Breakdown Analysis
            avg_breakdown = analysis.get('avg_breakdown_mins', 0)
            target_breakdown = self.targets.get('Breakdown_Mins', 60)
            
            if avg_breakdown > target_breakdown * 1.5:  # 50% above target
                breakdown_hours = analysis.get('total_breakdown_hours', 0)
                
                self.insights.append({
                    'category': 'operations',
                    'severity': 'high',
                    'furnace': furnace_id,
                    'title': f'High Breakdown Time - {furnace_id}',
                    'description': f'Average {avg_breakdown:.0f} minutes downtime per day ({breakdown_hours:.1f} total hours)',
                    'impact': f'Production loss: {avg_breakdown/60 * analysis.get("avg_daily_production", 0)/24:.1f} tons/day',
                    'recommendation': 'Implement preventive maintenance program and quick changeover procedures',
                    'data': {
                        'Avg Daily Breakdown': f'{avg_breakdown:.0f} minutes',
                        'Target': f'{target_breakdown:.0f} minutes',
                        'Total Breakdown': f'{breakdown_hours:.1f} hours'
                    }
                })
            
            # Operational Availability
            availability = analysis.get('operational_availability', 0)
            target_availability = self.targets.get('Operational_Availability', 90)
            
            if availability < target_availability - 5:
                self.insights.append({
                    'category': 'operations',
                    'severity': 'medium',
                    'furnace': furnace_id,
                    'title': f'Low Operational Availability - {furnace_id}',
                    'description': f'Availability ({availability:.1f}%) below target ({target_availability}%)',
                    'impact': 'Reduced production capacity and higher fixed costs',
                    'recommendation': 'Reduce unplanned stops and improve maintenance scheduling',
                    'data': {
                        'Current Availability': f'{availability:.1f}%',
                        'Target Availability': f'{target_availability}%'
                    }
                })
    
    def _generate_grade_based_insights(self):
        """Generate insights based on product grades"""
        if not self.data['grade_analysis']:
            return
        
        # Analyze cost variation by grade
        grade_costs = []
        for grade, analysis in self.data['grade_analysis'].items():
            grade_costs.append({
                'grade': grade,
                'cost': analysis.get('avg_cost_per_ton', 0),
                'production': analysis.get('total_production', 0)
            })
        
        if len(grade_costs) > 1:
            # Find highest cost grade
            grade_costs.sort(key=lambda x: x['cost'], reverse=True)
            highest_cost = grade_costs[0]
            lowest_cost = grade_costs[-1]
            
            cost_difference = ((highest_cost['cost'] - lowest_cost['cost']) / lowest_cost['cost']) * 100
            
            if cost_difference > 20:  # 20% cost difference
                self.insights.append({
                    'category': 'grade',
                    'severity': 'high',
                    'title': f'Significant Cost Variation by Grade',
                    'description': f'{highest_cost["grade"]} costs {cost_difference:.1f}% more per ton than {lowest_cost["grade"]}',
                    'impact': f'Opportunity to optimize {highest_cost["grade"]} production or pricing',
                    'recommendation': f'Analyze cost drivers for {highest_cost["grade"]} and implement cost reduction measures',
                    'data': {
                        'Highest Cost Grade': f'{highest_cost["grade"]} (₹{highest_cost["cost"]:,.0f}/MT)',
                        'Lowest Cost Grade': f'{lowest_cost["grade"]} (₹{lowest_cost["cost"]:,.0f}/MT)',
                        'Cost Difference': f'{cost_difference:.1f}%'
                    }
                })
    
    def _generate_comparative_insights(self):
        """Generate comparative insights between furnaces"""
        furnace_summary = self.analyzer.get_furnace_summary()
        
        if len(furnace_summary) < 2:
            return
        
        # Compare key metrics
        comparison_metrics = [
            ('Avg_Cost_per_Ton', 'Cost per Ton', True),  # Lower is better
            ('Avg_Power_kWh_MT', 'Power Consumption', True),  # Lower is better
            ('Avg_MN_Recovery_%', 'MN Recovery', False),  # Higher is better
            ('Operational_Availability_%', 'Availability', False),  # Higher is better
            ('Performance_Score', 'Performance Score', False),  # Higher is better
        ]
        
        for metric_col, display_name, lower_is_better in comparison_metrics:
            if metric_col in furnace_summary.columns:
                if lower_is_better:
                    best_idx = furnace_summary[metric_col].idxmin()
                    worst_idx = furnace_summary[metric_col].idxmax()
                else:
                    best_idx = furnace_summary[metric_col].idxmax()
                    worst_idx = furnace_summary[metric_col].idxmin()
                
                best_furnace = furnace_summary.iloc[best_idx]
                worst_furnace = furnace_summary.iloc[worst_idx]
                
                best_value = best_furnace[metric_col]
                worst_value = worst_furnace[metric_col]
                
                if best_value > 0:
                    gap_pct = abs((worst_value - best_value) / best_value) * 100
                    
                    if gap_pct > 20:  # 20% performance gap
                        self.insights.append({
                            'category': 'comparative',
                            'severity': 'high',
                            'title': f'{display_name} Performance Gap',
                            'description': f'{worst_furnace["Furnace"]} has {gap_pct:.1f}% {("higher" if lower_is_better else "lower")} {display_name.lower()} than {best_furnace["Furnace"]}',
                            'impact': f'Opportunity to match {best_furnace["Furnace"]} performance',
                            'recommendation': f'Benchmark operating parameters from {best_furnace["Furnace"]} to {worst_furnace["Furnace"]}',
                            'data': {
                                'Best Performer': f'{best_furnace["Furnace"]} ({best_value:.1f})',
                                'Worst Performer': f'{worst_furnace["Furnace"]} ({worst_value:.1f})',
                                'Performance Gap': f'{gap_pct:.1f}%'
                            }
                        })
    
    def _generate_trend_insights(self):
        """Generate trend-based insights"""
        df = self.analyzer.processed_df
        
        if 'DATE' not in df.columns or len(df) < 14:
            return
        
        # Check for weekly trends
        df = df.sort_values('DATE')
        recent_week = df.tail(7)
        previous_week = df.iloc[-14:-7] if len(df) >= 14 else df.iloc[:-7]
        
        if len(recent_week) > 3 and len(previous_week) > 3:
            # Cost trend
            if 'Cost_per_Ton' in df.columns:
                recent_cost = recent_week['Cost_per_Ton'].mean()
                previous_cost = previous_week['Cost_per_Ton'].mean()
                
                if previous_cost > 0 and recent_cost > previous_cost * 1.1:  # 10% increase
                    self.insights.append({
                        'category': 'trend',
                        'severity': 'medium',
                        'title': f'Recent Cost Increase Trend',
                        'description': f'Cost per ton increased by {((recent_cost/previous_cost - 1)*100):.1f}% in the last week',
                        'impact': 'If trend continues, will impact monthly profitability',
                        'recommendation': 'Investigate recent cost drivers (raw material prices, power rates, etc.)',
                        'data': {
                            'Previous Week Avg': f'₹{previous_cost:,.0f}/MT',
                            'Recent Week Avg': f'₹{recent_cost:,.0f}/MT',
                            'Increase': f'{((recent_cost/previous_cost - 1)*100):.1f}%'
                        }
                    })
    
    def _categorize_insights(self) -> Dict[str, List[Dict]]:
        """Categorize insights for display"""
        categories = {
            '🚨 CRITICAL ISSUES': [],
            '💰 COST OPTIMIZATION': [],
            '⚡ POWER EFFICIENCY': [],
            '🔬 MATERIAL RECOVERY': [],
            '🎯 PRODUCT QUALITY': [],
            '🏭 PRODUCTION EFFICIENCY': [],
            '⚙️ OPERATIONAL EXCELLENCE': [],
            '📊 PERFORMANCE BENCHMARKING': [],
            '📈 TREND ANALYSIS': []
        }
        
        # First, identify critical issues (high severity with financial impact)
        for insight in self.insights:
            severity = insight.get('severity', 'medium')
            category = insight.get('category', '')
            
            if severity == 'high' and 'financial_impact' in insight:
                categories['🚨 CRITICAL ISSUES'].append(insight)
            elif category == 'cost':
                categories['💰 COST OPTIMIZATION'].append(insight)
            elif category == 'power':
                categories['⚡ POWER EFFICIENCY'].append(insight)
            elif category == 'recovery':
                categories['🔬 MATERIAL RECOVERY'].append(insight)
            elif category == 'quality':
                categories['🎯 PRODUCT QUALITY'].append(insight)
            elif category in ['production', 'efficiency', 'capacity']:
                categories['🏭 PRODUCTION EFFICIENCY'].append(insight)
            elif category == 'operations':
                categories['⚙️ OPERATIONAL EXCELLENCE'].append(insight)
            elif category == 'comparative':
                categories['📊 PERFORMANCE BENCHMARKING'].append(insight)
            elif category == 'trend':
                categories['📈 TREND ANALYSIS'].append(insight)
            elif category == 'grade':
                categories['💰 COST OPTIMIZATION'].append(insight)
            else:
                categories['⚙️ OPERATIONAL EXCELLENCE'].append(insight)
        
        # Sort insights within each category
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        for category in categories:
            categories[category].sort(
                key=lambda x: (
                    severity_order.get(x.get('severity', 'low'), 0),
                    x.get('financial_impact', 0) if 'financial_impact' in x else 0
                ),
                reverse=True
            )
        
        return categories
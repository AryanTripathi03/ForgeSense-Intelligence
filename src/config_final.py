# src/config_final.py - Final configuration for your furnace data
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ColumnConfig:
    name: str
    display_name: str
    unit: str
    target: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    higher_is_better: bool = True

class FurnaceConfigFinal:
    """Final configuration based on your actual data structure"""
    
    # ========== CORE COLUMNS FROM YOUR DATA ==========
    CORE_COLUMNS = {
        # Identification
        'Furnace': ColumnConfig('Furnace', 'Furnace ID', '', higher_is_better=None),
        'DATE': ColumnConfig('DATE', 'Date', '', higher_is_better=None),
        'Incharge': ColumnConfig('Incharge', 'Manager', '', higher_is_better=None),
        
        # Production (Priority 1)
        'Actual Production Qty': ColumnConfig('Actual Production Qty', 'Production', 'MT', target=100, higher_is_better=True),
        'Shortage': ColumnConfig('Shortage', 'Shortage', 'MT', target=0, higher_is_better=False),
        'Cake Production Qty': ColumnConfig('Cake Production Qty', 'Cake Production', 'MT', higher_is_better=True),
        
        # Slag Chemistry (Priority 2)
        'Slag Qty (MT)': ColumnConfig('Slag Qty (MT)', 'Slag Quantity', 'MT', higher_is_better=False),
        'MnO%': ColumnConfig('MnO%', 'MnO Percentage', '%', target=10, min_value=5, max_value=15),
        'SiO2%': ColumnConfig('SiO2%', 'SiO2 Percentage', '%', target=35, min_value=30, max_value=40),
        'Feo%': ColumnConfig('Feo%', 'FeO Percentage', '%', target=3, min_value=1, max_value=5),
        'Cao%': ColumnConfig('Cao%', 'CaO Percentage', '%', target=40, min_value=35, max_value=45),
        'Mgo%': ColumnConfig('Mgo%', 'MgO Percentage', '%', target=7.5, min_value=5, max_value=10),
        'Al2O3%': ColumnConfig('Al2O3%', 'Al2O3 Percentage', '%', target=15, min_value=10, max_value=20),
        'Basicity': ColumnConfig('Basicity', 'Basicity Ratio', '', target=1.35, min_value=1.2, max_value=1.5),
        
        # Costs (Priority 1)
        'Ore Cost Feeding': ColumnConfig('Ore Cost Feeding', 'Ore Cost', '₹', higher_is_better=False),
        'Coke Cost Feeding': ColumnConfig('Coke Cost Feeding', 'Coke Cost', '₹', higher_is_better=False),
        'Fluxes Feeding': ColumnConfig('Fluxes Feeding', 'Fluxes Cost', '₹', higher_is_better=False),
        'Power Cost': ColumnConfig('Power Cost', 'Power Cost', '₹', higher_is_better=False),
        'Total Cost Feeding': ColumnConfig('Total Cost Feeding', 'Total Cost', '₹', higher_is_better=False),
        'Ore Cost PLC': ColumnConfig('Ore Cost PLC', 'Ore Cost (PLC)', '₹', higher_is_better=False),
        'Coke Cost PLC': ColumnConfig('Coke Cost PLC', 'Coke Cost (PLC)', '₹', higher_is_better=False),
        'Total Cost PLC': ColumnConfig('Total Cost PLC', 'Total Cost (PLC)', '₹', higher_is_better=False),
        'Target cost': ColumnConfig('Target cost', 'Target Cost', '₹', higher_is_better=False),
        
        # Power (Priority 1)
        'Furnace Power Consumption': ColumnConfig('Furnace Power Consumption', 'Furnace Power', 'kWh', higher_is_better=False),
        'Specific Power Consumption': ColumnConfig('Specific Power Consumption', 'Specific Power', 'kWh/MT', target=2500, higher_is_better=False),
        'Load Factor': ColumnConfig('Load Factor', 'Load Factor', '%', target=85, higher_is_better=True),
        'Power Factor': ColumnConfig('Power Factor', 'Power Factor', '', target=0.95, higher_is_better=True),
        
        # Recovery (Priority 1)
        'MN Recovery PLC': ColumnConfig('MN Recovery PLC', 'MN Recovery', '%', target=80, higher_is_better=True),
        'SI Recovery PLC': ColumnConfig('SI Recovery PLC', 'SI Recovery', '%', target=45, higher_is_better=True),
        
        # Material Input (Priority 2)
        'Input Qty(Ore PLC)(MT)': ColumnConfig('Input Qty(Ore PLC)(MT)', 'Ore Input', 'MT', higher_is_better=False),
        'Input Qty(Coke PLC)(MT)': ColumnConfig('Input Qty(Coke PLC)(MT)', 'Coke Input', 'MT', higher_is_better=False),
        
        # Quality (Priority 2)
        'Grade MN': ColumnConfig('Grade MN', 'MN Grade', '%', target=70, min_value=65, max_value=75),
        'Grade SI': ColumnConfig('Grade SI', 'SI Grade', '%', target=17.5, min_value=15, max_value=20),
        'C%': ColumnConfig('C%', 'Carbon Percentage', '%', target=7, min_value=6, max_value=8),
    }
    
    # ========== CALCULATED METRICS ==========
    CALCULATED_METRICS = {
        'cost_per_ton': {
            'formula': 'Total Cost PLC / Actual Production Qty',
            'display_name': 'Cost per Ton',
            'unit': '₹/MT',
            'target': 50000,
            'higher_is_better': False
        },
        'power_cost_per_ton': {
            'formula': 'Power Cost / Actual Production Qty',
            'display_name': 'Power Cost per Ton',
            'unit': '₹/MT',
            'higher_is_better': False
        },
        'yield_percentage': {
            'formula': '(Actual Production Qty / Cake Production Qty) * 100',
            'display_name': 'Yield Percentage',
            'unit': '%',
            'target': 95,
            'higher_is_better': True
        },
        'ore_efficiency': {
            'formula': 'Actual Production Qty / Input Qty(Ore PLC)(MT)',
            'display_name': 'Ore Efficiency',
            'unit': 'MT/MT',
            'target': 0.55,
            'higher_is_better': True
        },
        'coke_efficiency': {
            'formula': 'Actual Production Qty / Input Qty(Coke PLC)(MT)',
            'display_name': 'Coke Efficiency',
            'unit': 'MT/MT',
            'target': 4.0,
            'higher_is_better': True
        }
    }
    
    # ========== INSIGHT RULES ==========
    INSIGHT_RULES = {
        'cost_high': {
            'metric': 'cost_per_ton',
            'condition': 'value > target * 1.15',  # 15% above target
            'severity': 'high',
            'title_template': 'High Cost per Ton - {furnace}',
            'description_template': 'Cost per ton (₹{value:,.0f}) is {percent_above:.1f}% above target',
            'recommendation': 'Review raw material mix, optimize power consumption, reduce breakdown time'
        },
        'power_high': {
            'metric': 'Specific Power Consumption',
            'condition': 'value > target * 1.2',  # 20% above target
            'severity': 'medium',
            'title_template': 'High Power Consumption - {furnace}',
            'description_template': 'Power consumption ({value:,.0f} kWh/MT) is above target',
            'recommendation': 'Optimize electrode control, improve power factor'
        },
        'recovery_low': {
            'metric': 'MN Recovery PLC',
            'condition': 'value < target * 0.9',  # 10% below target
            'severity': 'high',
            'title_template': 'Low MN Recovery - {furnace}',
            'description_template': 'MN Recovery ({value:.1f}%) is below target ({target}%)',
            'recommendation': 'Optimize temperature control, review slag chemistry'
        },
        'quality_out_of_range': {
            'metrics': ['Grade MN', 'Grade SI', 'C%', 'Basicity'],
            'condition': 'value < min_value or value > max_value',
            'severity': 'medium',
            'title_template': 'Quality Parameter Out of Range - {furnace}',
            'description_template': '{metric} ({value:.1f}{unit}) outside optimal range ({min:.1f}-{max:.1f})',
            'recommendation': 'Adjust raw material mix and process parameters'
        }
    }
    
    # ========== VISUALIZATION SETTINGS ==========
    CHARTS = {
        'production_trend': {
            'type': 'line',
            'x': 'DATE',
            'y': 'Actual Production Qty',
            'title': 'Production Trend',
            'color': 'Furnace'
        },
        'cost_comparison': {
            'type': 'bar',
            'x': 'Furnace',
            'y': 'cost_per_ton',
            'title': 'Cost per Ton by Furnace',
            'color': 'cost_per_ton'
        },
        'recovery_analysis': {
            'type': 'scatter',
            'x': 'MN Recovery PLC',
            'y': 'SI Recovery PLC',
            'title': 'MN vs SI Recovery',
            'color': 'Furnace'
        }
    }
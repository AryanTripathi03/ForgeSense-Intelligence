# src/config.py - Configuration for furnace data
import pandas as pd
from typing import Dict, List, Optional

class FurnaceConfig:
    """Configuration for furnace data processing"""
    
    # ========== EXACT COLUMN MAPPING FROM YOUR DATA ==========
    COLUMNS = {
        # Core identification
        'Furnace': {'type': 'category', 'importance': 'high'},
        'DATE': {'type': 'datetime', 'importance': 'high'},
        'Incharge': {'type': 'category', 'importance': 'medium'},
        
        # Production metrics
        'Actual Production Qty': {'type': 'float', 'importance': 'high'},
        'Shortage': {'type': 'float', 'importance': 'medium'},
        'Cake Production Qty': {'type': 'float', 'importance': 'high'},
        
        # Slag chemistry
        'Slag Qty (MT)': {'type': 'float', 'importance': 'high'},
        'MnO%': {'type': 'float', 'importance': 'high'},
        'SiO2%': {'type': 'float', 'importance': 'high'},
        'Feo%': {'type': 'float', 'importance': 'medium'},
        'Cao%': {'type': 'float', 'importance': 'high'},
        'Mgo%': {'type': 'float', 'importance': 'medium'},
        'Al2O3%': {'type': 'float', 'importance': 'medium'},
        'Basicity': {'type': 'float', 'importance': 'high'},
        
        # Operations
        'Tappings': {'type': 'float', 'importance': 'medium'},
        'Input Qty(Ore PLC)(MT)': {'type': 'float', 'importance': 'high'},
        'Input Qty(Coke PLC)(MT)': {'type': 'float', 'importance': 'high'},
        
        # Batches and shifts
        'Number of Batches A Shift': {'type': 'float', 'importance': 'medium'},
        'Number of Batches B Shift': {'type': 'float', 'importance': 'medium'},
        'Number of Batches C Shift': {'type': 'float', 'importance': 'medium'},
        'Total Number of Batches': {'type': 'float', 'importance': 'medium'},
        'Input Ratio': {'type': 'float', 'importance': 'high'},
        
        # Metal quality
        'Metal Wt': {'type': 'float', 'importance': 'high'},
        'Recovery Liquid Metal': {'type': 'float', 'importance': 'high'},
        'GRADE': {'type': 'category', 'importance': 'high'},
        'Grade MN': {'type': 'float', 'importance': 'high'},
        'Grade SI': {'type': 'float', 'importance': 'high'},
        'C%': {'type': 'float', 'importance': 'high'},
        
        # Manganese metrics
        'MN Feeding': {'type': 'float', 'importance': 'high'},
        'MN PLC': {'type': 'float', 'importance': 'high'},
        'MN Recovery Feeding': {'type': 'float', 'importance': 'high'},
        'MN Recovery PLC': {'type': 'float', 'importance': 'high'},
        
        # Fixed carbon
        'FC Feeding': {'type': 'float', 'importance': 'medium'},
        'FC PLC': {'type': 'float', 'importance': 'medium'},
        
        # Silicon recovery
        'SI Recovery Feeding': {'type': 'float', 'importance': 'high'},
        'SI Recovery PLC': {'type': 'float', 'importance': 'high'},
        
        # Size distribution
        'Breaking Size': {'type': 'float', 'importance': 'medium'},
        'Under Size Generation': {'type': 'float', 'importance': 'high'},
        
        # Power consumption
        'Furnace Power Consumption': {'type': 'float', 'importance': 'high'},
        'Aux power Consumption': {'type': 'float', 'importance': 'medium'},
        'Specific Power Consumption': {'type': 'float', 'importance': 'high'},
        
        # Electrical parameters
        'Avg. Mg.': {'type': 'float', 'importance': 'medium'},
        'Load Factor': {'type': 'float', 'importance': 'high'},
        'Elec. Length Day Avg.': {'type': 'float', 'importance': 'medium'},
        'Power Factor': {'type': 'float', 'importance': 'high'},
        'Elec. Holding Day Avg.': {'type': 'float', 'importance': 'medium'},
        'Elec. Slipping Day Avg.': {'type': 'float', 'importance': 'medium'},
        
        # Costs - Feeding
        'Ore Cost Feeding': {'type': 'float', 'importance': 'high'},
        'Coke Cost Feeding': {'type': 'float', 'importance': 'high'},
        'Fluxes Feeding': {'type': 'float', 'importance': 'high'},
        'Consumable items': {'type': 'float', 'importance': 'medium'},
        'Power Cost': {'type': 'float', 'importance': 'high'},
        'Undersize Cost': {'type': 'float', 'importance': 'high'},
        'Over head': {'type': 'float', 'importance': 'medium'},
        'Total Cost Feeding': {'type': 'float', 'importance': 'high'},
        
        # Costs - PLC
        'Ore Cost PLC': {'type': 'float', 'importance': 'high'},
        'Coke Cost PLC': {'type': 'float', 'importance': 'high'},
        'Fluxes PLC': {'type': 'float', 'importance': 'high'},
        'Undersize Cost PLC': {'type': 'float', 'importance': 'high'},
        'Total Cost PLC': {'type': 'float', 'importance': 'high'},
        
        # Breakdowns
        'Mechanical B/D Mins': {'type': 'float', 'importance': 'high'},
        'Electrical B/D Mins': {'type': 'float', 'importance': 'high'},
        'Production B/D Mins': {'type': 'float', 'importance': 'high'},
        'Preventive B/D Mins': {'type': 'float', 'importance': 'medium'},
        'Shutdown Mins': {'type': 'float', 'importance': 'high'},
        'Total Breakdown Mins': {'type': 'float', 'importance': 'high'},
        
        # Performance
        'Target cost': {'type': 'float', 'importance': 'high'},
        'Total Cost PLC 4 Items': {'type': 'float', 'importance': 'high'},
        'P/L': {'type': 'float', 'importance': 'high'},
        'Total P/L': {'type': 'float', 'importance': 'high'},
        
        # Time dimensions
        'Week': {'type': 'int', 'importance': 'medium'},
        'Month': {'type': 'int', 'importance': 'medium'},
        
        # Text fields
        'Reason': {'type': 'text', 'importance': 'low'},
        'Production Dept. Comments': {'type': 'text', 'importance': 'low'}
    }
    
    # ========== CALCULATED METRICS ==========
    DERIVED_METRICS = {
        'cost_per_ton': 'Total Cost PLC / Actual Production Qty',
        'power_cost_per_ton': 'Power Cost / Actual Production Qty',
        'yield_percentage': '(Actual Production Qty / Cake Production Qty) * 100',
        'ore_efficiency': 'Actual Production Qty / Input Qty(Ore PLC)(MT)',
        'mn_recovery_gap': 'MN Recovery PLC - MN Recovery Feeding',
        'si_recovery_gap': 'SI Recovery PLC - SI Recovery Feeding',
        'operational_availability': '((1440 - Total Breakdown Mins) / 1440) * 100'
    }
    
    # ========== TARGET VALUES (Can be adjusted) ==========
    TARGETS = {
        'Specific Power Consumption': 2500,  # kWh/ton
        'MN Recovery PLC': 80,  # %
        'SI Recovery PLC': 45,  # %
        'Load Factor': 85,  # %
        'Power Factor': 0.95,
        'cost_per_ton': 50000,  # ₹/ton
        'operational_availability': 90  # %
    }
    
    # ========== ALERT THRESHOLDS ==========
    ALERT_THRESHOLDS = {
        'cost_high': 0.15,  # 15% above target
        'power_high': 0.20,  # 20% above target
        'recovery_low': 0.10,  # 10% below target
        'breakdown_high': 180  # minutes
    }
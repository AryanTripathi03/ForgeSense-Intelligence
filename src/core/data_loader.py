# src/core/data_loader.py - Load and process furnace data
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import warnings

class FurnaceDataLoader:
    """Load and process furnace Excel data"""
    
    def __init__(self):
        self.df = None
        self.processed_df = None
    
    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        Load Excel file and return cleaned DataFrame
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Cleaned DataFrame
        """
        print(f"📂 Loading data from: {file_path}")
        
        try:
            # Read Excel file
            self.df = pd.read_excel(file_path)
            print(f"✅ Loaded {len(self.df)} rows, {len(self.df.columns)} columns")
            
            # Clean column names (remove extra spaces, newlines)
            self.df.columns = [str(col).strip().replace('\n', ' ') for col in self.df.columns]
            
            # Process the data
            self.processed_df = self._process_data(self.df)
            
            return self.processed_df
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            raise
    
    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the data"""
        df_processed = df.copy()
        
        # Convert DATE column to datetime
        if 'DATE' in df_processed.columns:
            df_processed['DATE'] = pd.to_datetime(df_processed['DATE'], errors='coerce')
        
        # Convert numeric columns
        numeric_cols = [
            'Actual Production Qty', 'Shortage', 'Cake Production Qty',
            'Slag Qty (MT)', 'MnO%', 'SiO2%', 'Feo%', 'Cao%', 'Mgo%', 'Al2O3%',
            'Basicity', 'Input Qty(Ore PLC)(MT)', 'Input Qty(Coke PLC)(MT)',
            'Furnace Power Consumption', 'Specific Power Consumption',
            'MN Recovery PLC', 'SI Recovery PLC', 'Total Cost PLC', 'Target cost'
        ]
        
        for col in numeric_cols:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Fill missing values with 0 for certain columns
        zero_fill_cols = ['Shortage', 'Under Size Generation', 'Total Breakdown Mins']
        for col in zero_fill_cols:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].fillna(0)
        
        # Calculate derived metrics
        df_processed = self._calculate_metrics(df_processed)
        
        return df_processed
    
    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate key performance metrics"""
        df_calc = df.copy()
        
        # Cost per ton
        if 'Total Cost PLC' in df_calc.columns and 'Actual Production Qty' in df_calc.columns:
            df_calc['cost_per_ton'] = df_calc['Total Cost PLC'] / df_calc['Actual Production Qty']
        
        # Power cost per ton
        if 'Power Cost' in df_calc.columns and 'Actual Production Qty' in df_calc.columns:
            df_calc['power_cost_per_ton'] = df_calc['Power Cost'] / df_calc['Actual Production Qty']
        
        # Yield percentage
        if 'Actual Production Qty' in df_calc.columns and 'Cake Production Qty' in df_calc.columns:
            df_calc['yield_percentage'] = (df_calc['Actual Production Qty'] / df_calc['Cake Production Qty']) * 100
        
        # Ore efficiency
        if 'Actual Production Qty' in df_calc.columns and 'Input Qty(Ore PLC)(MT)' in df_calc.columns:
            df_calc['ore_efficiency'] = df_calc['Actual Production Qty'] / df_calc['Input Qty(Ore PLC)(MT)']
        
        # Operational availability (24 hours = 1440 minutes)
        if 'Total Breakdown Mins' in df_calc.columns:
            df_calc['operational_availability'] = ((1440 - df_calc['Total Breakdown Mins']) / 1440) * 100
        
        return df_calc
    
    def get_summary(self) -> Dict:
        """Get summary of the data"""
        if self.processed_df is None:
            return {}
        
        summary = {
            'total_rows': len(self.processed_df),
            'date_range': {
                'start': self.processed_df['DATE'].min().strftime('%Y-%m-%d'),
                'end': self.processed_df['DATE'].max().strftime('%Y-%m-%d')
            } if 'DATE' in self.processed_df.columns else {},
            'furnaces': list(self.processed_df['Furnace'].unique()) if 'Furnace' in self.processed_df.columns else [],
            'total_production': self.processed_df['Actual Production Qty'].sum() if 'Actual Production Qty' in self.processed_df.columns else 0,
            'avg_cost_per_ton': self.processed_df['cost_per_ton'].mean() if 'cost_per_ton' in self.processed_df.columns else 0
        }
        
        return summary
    
    def get_furnace_performance(self) -> pd.DataFrame:
        """Get performance metrics for each furnace"""
        if self.processed_df is None or 'Furnace' not in self.processed_df.columns:
            return pd.DataFrame()
        
        # Group by furnace
        metrics = ['cost_per_ton', 'Specific Power Consumption', 'MN Recovery PLC', 
                  'SI Recovery PLC', 'operational_availability', 'Actual Production Qty']
        
        available_metrics = [m for m in metrics if m in self.processed_df.columns]
        
        if not available_metrics:
            return pd.DataFrame()
        
        furnace_stats = self.processed_df.groupby('Furnace')[available_metrics].agg(['mean', 'std']).round(2)
        
        # Flatten column names
        furnace_stats.columns = ['_'.join(col).strip() for col in furnace_stats.columns.values]
        furnace_stats = furnace_stats.reset_index()
        
        return furnace_stats
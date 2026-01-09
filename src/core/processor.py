# src/core/processor.py - Production data processor
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

class FurnaceDataProcessor:
    """Process furnace data for production use"""
    
    def __init__(self):
        self.raw_df = None
        self.processed_df = None
        self.metrics_df = None
        
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw furnace data
        
        Args:
            df: Raw DataFrame from Excel
            
        Returns:
            Processed DataFrame with all calculated metrics
        """
        self.raw_df = df.copy()
        
        # Step 1: Clean data
        df_clean = self._clean_data(df)
        
        # Step 2: Calculate all metrics
        df_metrics = self._calculate_all_metrics(df_clean)
        
        # Step 3: Add derived insights
        df_final = self._add_derived_features(df_metrics)
        
        self.processed_df = df_final
        return df_final
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data"""
        df_clean = df.copy()
        
        # Clean column names
        df_clean.columns = [str(col).strip() for col in df_clean.columns]
        
        # Ensure DATE is datetime
        if 'DATE' in df_clean.columns:
            df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = [
            'Actual Production Qty', 'Shortage', 'Cake Production Qty',
            'Slag Qty (MT)', 'MnO%', 'SiO2%', 'Feo%', 'Cao%', 'Mgo%', 'Al2O3%',
            'Basicity', 'Input Qty(Ore PLC)(MT)', 'Input Qty(Coke PLC)(MT)',
            'Furnace Power Consumption', 'Specific Power Consumption',
            'MN Recovery PLC', 'SI Recovery PLC',
            'Ore Cost Feeding', 'Coke Cost Feeding', 'Fluxes Feeding',
            'Power Cost', 'Total Cost Feeding',
            'Ore Cost PLC', 'Coke Cost PLC', 'Fluxes PLC', 'Total Cost PLC',
            'Target cost', 'Grade MN', 'Grade SI', 'C%',
            'Load Factor', 'Power Factor'
        ]
        
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Fill missing values
        zero_fill_cols = ['Shortage', 'Total Breakdown Mins']
        for col in zero_fill_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(0)
        
        return df_clean
    
    def _calculate_all_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all performance metrics"""
        df_metrics = df.copy()
        
        # 1. Cost metrics
        if 'Total Cost PLC' in df_metrics.columns and 'Actual Production Qty' in df_metrics.columns:
            df_metrics['cost_per_ton'] = df_metrics['Total Cost PLC'] / df_metrics['Actual Production Qty']
        
        if 'Power Cost' in df_metrics.columns and 'Actual Production Qty' in df_metrics.columns:
            df_metrics['power_cost_per_ton'] = df_metrics['Power Cost'] / df_metrics['Actual Production Qty']
        
        # 2. Efficiency metrics
        if 'Actual Production Qty' in df_metrics.columns and 'Cake Production Qty' in df_metrics.columns:
            df_metrics['yield_percentage'] = (df_metrics['Actual Production Qty'] / df_metrics['Cake Production Qty']) * 100
        
        if 'Actual Production Qty' in df_metrics.columns and 'Input Qty(Ore PLC)(MT)' in df_metrics.columns:
            df_metrics['ore_efficiency'] = df_metrics['Actual Production Qty'] / df_metrics['Input Qty(Ore PLC)(MT)']
        
        if 'Actual Production Qty' in df_metrics.columns and 'Input Qty(Coke PLC)(MT)' in df_metrics.columns:
            df_metrics['coke_efficiency'] = df_metrics['Actual Production Qty'] / df_metrics['Input Qty(Coke PLC)(MT)']
        
        # 3. Quality scores
        if 'Grade MN' in df_metrics.columns:
            df_metrics['grade_mn_score'] = np.where(
                (df_metrics['Grade MN'] >= 65) & (df_metrics['Grade MN'] <= 75),
                100 - abs(df_metrics['Grade MN'] - 70) * 10,  # Score based on deviation from 70%
                0
            )
        
        if 'Basicity' in df_metrics.columns:
            df_metrics['basicity_score'] = np.where(
                (df_metrics['Basicity'] >= 1.2) & (df_metrics['Basicity'] <= 1.5),
                100 - abs(df_metrics['Basicity'] - 1.35) * 40,  # Score based on deviation from 1.35
                0
            )
        
        # 4. Performance score (0-100)
        score_components = []
        
        if 'cost_per_ton' in df_metrics.columns:
            # Lower cost is better
            cost_score = 100 - (df_metrics['cost_per_ton'] / df_metrics['cost_per_ton'].mean() - 1) * 50
            cost_score = cost_score.clip(0, 100)
            score_components.append(cost_score)
        
        if 'MN Recovery PLC' in df_metrics.columns:
            # Higher recovery is better
            recovery_score = df_metrics['MN Recovery PLC']
            score_components.append(recovery_score)
        
        if 'Specific Power Consumption' in df_metrics.columns:
            # Lower power is better
            power_score = 100 - (df_metrics['Specific Power Consumption'] / 
                               df_metrics['Specific Power Consumption'].mean() - 1) * 50
            power_score = power_score.clip(0, 100)
            score_components.append(power_score)
        
        if score_components:
            df_metrics['performance_score'] = pd.DataFrame(score_components).mean()
        
        return df_metrics
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for analysis"""
        df_features = df.copy()
        
        # Add month, week, day features
        if 'DATE' in df_features.columns:
            df_features['Year'] = df_features['DATE'].dt.year
            df_features['Month'] = df_features['DATE'].dt.month
            df_features['Week'] = df_features['DATE'].dt.isocalendar().week
            df_features['Day'] = df_features['DATE'].dt.day
            df_features['DayOfWeek'] = df_features['DATE'].dt.dayofweek
        
        # Add shift information if not present
        if 'Incharge' in df_features.columns:
            # Map incharges to shifts if possible
            pass
        
        return df_features
    
    def get_furnace_summary(self) -> pd.DataFrame:
        """Get summary statistics for each furnace"""
        if self.processed_df is None or 'Furnace' not in self.processed_df.columns:
            return pd.DataFrame()
        
        # Key metrics to summarize
        metrics = [
            'Actual Production Qty', 'cost_per_ton', 'Specific Power Consumption',
            'MN Recovery PLC', 'SI Recovery PLC', 'yield_percentage',
            'ore_efficiency', 'performance_score', 'Total Cost PLC'
        ]
        
        # Filter to available metrics
        available_metrics = [m for m in metrics if m in self.processed_df.columns]
        
        if not available_metrics:
            return pd.DataFrame()
        
        # Calculate summary statistics
        summary = self.processed_df.groupby('Furnace')[available_metrics].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).round(2)
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
        summary = summary.reset_index()
        
        # Calculate ranking
        if 'cost_per_ton_mean' in summary.columns:
            summary['cost_rank'] = summary['cost_per_ton_mean'].rank()
        
        if 'performance_score_mean' in summary.columns:
            summary['performance_rank'] = summary['performance_score_mean'].rank(ascending=False)
        
        return summary
    
    def get_daily_performance(self) -> pd.DataFrame:
        """Get daily performance metrics"""
        if self.processed_df is None or 'DATE' not in self.processed_df.columns:
            return pd.DataFrame()
        
        # Group by date
        daily_metrics = ['Actual Production Qty', 'cost_per_ton', 'Specific Power Consumption']
        available_daily = [m for m in daily_metrics if m in self.processed_df.columns]
        
        if not available_daily:
            return pd.DataFrame()
        
        daily_summary = self.processed_df.groupby('DATE')[available_daily].agg(['sum', 'mean']).round(2)
        daily_summary.columns = ['_'.join(col).strip() for col in daily_summary.columns.values]
        daily_summary = daily_summary.reset_index()
        
        # Add moving averages
        for col in daily_summary.columns:
            if 'mean' in col:
                daily_summary[f'{col}_7d_avg'] = daily_summary[col].rolling(7).mean()
        
        return daily_summary
    
    def detect_anomalies(self, threshold_std: float = 2.0) -> pd.DataFrame:
        """Detect anomalous data points"""
        if self.processed_df is None:
            return pd.DataFrame()
        
        anomalies = []
        
        # Check for anomalies in key metrics
        check_metrics = ['cost_per_ton', 'Specific Power Consumption', 'MN Recovery PLC']
        
        for metric in check_metrics:
            if metric in self.processed_df.columns:
                # Calculate z-score
                mean_val = self.processed_df[metric].mean()
                std_val = self.processed_df[metric].std()
                
                if std_val > 0:
                    z_score = abs((self.processed_df[metric] - mean_val) / std_val)
                    metric_anomalies = self.processed_df[z_score > threshold_std].copy()
                    metric_anomalies['anomaly_type'] = metric
                    metric_anomalies['z_score'] = z_score[z_score > threshold_std]
                    
                    anomalies.append(metric_anomalies)
        
        if anomalies:
            return pd.concat(anomalies, ignore_index=True)
        else:
            return pd.DataFrame()
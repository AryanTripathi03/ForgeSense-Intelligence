# test_capacity.py - Test capacity-based system
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("🧪 Testing Capacity-Based Furnace Analysis")
print("=" * 60)

# Create sample data
dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
data = []

for date in dates:
    for furnace in ['F1', 'F2', 'F3']:
        base_prod = np.random.uniform(80, 120)
        data.append({
            'Furnace': furnace,
            'DATE': date,
            'Actual Production Qty': round(base_prod, 2),
            'Total Cost PLC': round(base_prod * np.random.uniform(45000, 55000), 2),
            'Specific Power Consumption': round(np.random.uniform(2300, 2700), 2),
            'MN Recovery PLC': round(np.random.uniform(75, 85), 2),
            'Grade MN': round(np.random.uniform(68, 72), 2),
            'Grade SI': round(np.random.uniform(16, 18), 2),
            'C%': round(np.random.uniform(6.5, 7.5), 2),
            'Basicity': round(np.random.uniform(1.2, 1.5), 2),
            'Total Breakdown Mins': np.random.choice([0, 30, 60, 120], p=[0.6, 0.3, 0.08, 0.02]),
            'Load Factor': round(np.random.uniform(75, 90), 2),
        })

df = pd.DataFrame(data)
df.to_excel('test_capacity_data.xlsx', index=False)

print(f"✅ Created test data with {len(df)} records")
print(f"📁 Saved to: test_capacity_data.xlsx")
print("\n📊 Sample data:")
print(df[['Furnace', 'DATE', 'Actual Production Qty', 'Total Cost PLC']].head())

print("\n" + "=" * 60)
print("🎯 CAPACITY-BASED ANALYSIS READY")
print("=" * 60)
print("\nTo use the system:")
print("1. Run: streamlit run app_capacity_based.py")
print("2. Upload: test_capacity_data.xlsx")
print("3. Input capacities:")
print("   - F1: 12.5 MVA, 100 MT/day design")
print("   - F2: 12.5 MVA, 100 MT/day design")
print("   - F3: 12.5 MVA, 100 MT/day design")
print("4. Get capacity-based insights!")
# create_sample.py - Create sample furnace data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("Creating sample furnace data...")

# Create sample data matching your columns
data = []

# Create 30 days of data for 4 furnaces
for day in range(30):
    date = datetime(2024, 1, 1) + timedelta(days=day)
    
    for furnace in ['F1', 'F2', 'F3', 'F4']:
        # Base production with some variation
        base_prod = np.random.uniform(80, 120)
        
        row = {
            'Furnace': furnace,
            'DATE': date.strftime('%Y-%m-%d'),
            'Incharge': f'Manager_{np.random.choice(["A", "B", "C"])}',
            'Actual Production Qty': round(base_prod, 2),
            'Cake Production Qty': round(base_prod * 1.05, 2),
            'Slag Qty (MT)': round(base_prod * 0.3, 2),
            'MnO%': round(np.random.uniform(5, 15), 2),
            'SiO2%': round(np.random.uniform(30, 40), 2),
            'Cao%': round(np.random.uniform(35, 45), 2),
            'Mgo%': round(np.random.uniform(5, 10), 2),
            'Al2O3%': round(np.random.uniform(10, 20), 2),
            'Basicity': round(np.random.uniform(1.2, 1.5), 2),
            'Input Qty(Ore PLC)(MT)': round(base_prod * 1.8, 2),
            'Input Qty(Coke PLC)(MT)': round(base_prod * 0.25, 2),
            'Furnace Power Consumption': round(base_prod * np.random.uniform(2000, 3000), 2),
            'Specific Power Consumption': round(np.random.uniform(2200, 2800), 2),
            'MN Recovery PLC': round(np.random.uniform(75, 85), 2),
            'SI Recovery PLC': round(np.random.uniform(45, 55), 2),
            'Ore Cost PLC': round(base_prod * np.random.uniform(18000, 23000), 2),
            'Coke Cost PLC': round(base_prod * np.random.uniform(14000, 19000), 2),
            'Power Cost': round(base_prod * np.random.uniform(15000, 20000), 2),
            'Total Cost PLC': round(base_prod * np.random.uniform(65000, 80000), 2),
            'Total Breakdown Mins': np.random.choice([0, 30, 60, 120]),
            'Target cost': 50000,
            'Week': date.isocalendar()[1],
            'Month': date.month
        }
        
        data.append(row)

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'sample_furnace_data.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created sample data with {len(df)} rows")
print(f"📁 Saved to: {output_file}")
print("\n📊 Sample of data:")
print(df[['Furnace', 'DATE', 'Actual Production Qty', 'Total Cost PLC']].head())

print("\nTo run the app:")
print("1. First install: pip install pandas streamlit plotly openpyxl")
print("2. Then run: streamlit run app.py")
print("3. Upload the file: sample_furnace_data.xlsx")
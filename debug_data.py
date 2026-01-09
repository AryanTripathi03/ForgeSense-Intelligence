# debug_data.py - Debug your actual data
import pandas as pd
import numpy as np
import os

print("🔍 DEBUGGING YOUR FURNACE DATA")
print("=" * 80)

# Find Excel files
files = [f for f in os.listdir('.') if f.lower().endswith(('.xlsx', '.xls'))]
if not files:
    print("❌ No Excel files found!")
    exit()

file = files[0]
print(f"📁 Analyzing: {file}")
print("=" * 80)

# Read the file
df = pd.read_excel(file)
print(f"✅ Loaded: {len(df)} rows, {len(df.columns)} columns")

# Show ALL columns with their first value
print("\n📋 ALL COLUMNS WITH SAMPLE VALUES:")
print("-" * 80)
for i, col in enumerate(df.columns, 1):
    sample = df.iloc[0][col] if len(df) > 0 else "N/A"
    if pd.isna(sample):
        sample = "NULL"
    print(f"{i:3}. {col:50} → {str(sample)[:50]}")

# Find and analyze key columns
print("\n🔑 ANALYZING KEY METRICS:")
print("-" * 80)

# Function to find column by partial name
def find_column(df, keywords):
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in keywords):
            return col
    return None

# 1. Production
prod_col = find_column(df, ['production', 'prod', 'qty', 'quantity'])
if prod_col:
    print(f"\n📊 PRODUCTION DATA ({prod_col}):")
    print(f"   First value: {df.iloc[0][prod_col]}")
    print(f"   Data type: {df[prod_col].dtype}")
    print(f"   Non-null: {df[prod_col].notna().sum()}/{len(df)}")
    print(f"   Summary: Min={df[prod_col].min():.2f}, Max={df[prod_col].max():.2f}, Mean={df[prod_col].mean():.2f}")
    print(f"   Total: {df[prod_col].sum():,.2f}")
else:
    print("❌ PRODUCTION column not found!")

# 2. Cost
cost_col = find_column(df, ['total cost', 'cost plc', 'cost'])
if cost_col:
    print(f"\n💰 COST DATA ({cost_col}):")
    print(f"   First value: {df.iloc[0][cost_col]}")
    print(f"   Data type: {df[cost_col].dtype}")
    print(f"   Summary: Min={df[cost_col].min():,.2f}, Max={df[cost_col].max():,.2f}, Mean={df[cost_col].mean():,.2f}")
    print(f"   Total: {df[cost_col].sum():,.2f}")
    
    # Calculate cost per ton
    if prod_col:
        mask = (df[prod_col] > 0) & (df[cost_col].notna())
        if mask.any():
            cost_per_ton = df.loc[mask, cost_col] / df.loc[mask, prod_col]
            print(f"   Cost per ton: Min=₹{cost_per_ton.min():,.2f}, Max=₹{cost_per_ton.max():,.2f}, Avg=₹{cost_per_ton.mean():,.2f}")
else:
    print("❌ COST column not found!")

# 3. Power
power_col = find_column(df, ['specific power', 'power consumption', 'kwh'])
if power_col:
    print(f"\n⚡ POWER DATA ({power_col}):")
    print(f"   First value: {df.iloc[0][power_col]}")
    print(f"   Data type: {df[power_col].dtype}")
    print(f"   Summary: Min={df[power_col].min():,.2f}, Max={df[power_col].max():,.2f}, Mean={df[power_col].mean():,.2f}")
else:
    print("❌ POWER column not found!")

# 4. MN Recovery
mn_col = find_column(df, ['mn recovery', 'recovery plc', 'mn%'])
if mn_col:
    print(f"\n🔬 MN RECOVERY DATA ({mn_col}):")
    print(f"   First value: {df.iloc[0][mn_col]}")
    print(f"   Data type: {df[mn_col].dtype}")
    print(f"   Summary: Min={df[mn_col].min():.2f}%, Max={df[mn_col].max():.2f}%, Mean={df[mn_col].mean():.2f}%")
else:
    print("❌ MN RECOVERY column not found!")

# 5. Furnace column
furnace_col = find_column(df, ['furnace', 'unit', 'plant'])
if furnace_col:
    print(f"\n🏭 FURNACE DATA ({furnace_col}):")
    print(f"   Unique values: {df[furnace_col].unique()}")
    print(f"   Count: {df[furnace_col].nunique()} furnaces")

# 6. Check data types
print("\n📈 DATA TYPE ANALYSIS:")
print("-" * 80)
numeric_cols = df.select_dtypes(include=[np.number]).columns
print(f"   Numeric columns: {len(numeric_cols)}")
print(f"   Object columns: {len(df.select_dtypes(include=['object']).columns)}")

# 7. Show first few rows of data
print("\n👀 FIRST 3 ROWS OF ACTUAL DATA:")
print("-" * 80)
print(df.head(3).to_string())

# 8. Manual calculation verification
print("\n🧮 MANUAL CALCULATION VERIFICATION:")
print("-" * 80)

if prod_col and cost_col:
    print("Calculating Cost per Ton manually:")
    for i in range(min(3, len(df))):
        prod = df.iloc[i][prod_col]
        cost = df.iloc[i][cost_col]
        if pd.notna(prod) and pd.notna(cost) and prod > 0:
            calc = cost / prod
            print(f"  Row {i}: {cost:,.2f} / {prod:.2f} = ₹{calc:,.2f} per ton")

print("\n" + "=" * 80)
print("🎯 ISSUE DIAGNOSIS:")
print("=" * 80)

# Diagnose the issue
issues = []

if prod_col:
    avg_prod = df[prod_col].mean()
    if avg_prod < 10:
        issues.append(f"Production values too small (avg: {avg_prod:.2f}). Might be in wrong units.")
    
if cost_col:
    avg_cost = df[cost_col].mean()
    if avg_cost < 100000:  # Less than 1 lakh
        issues.append(f"Cost values too small (avg: ₹{avg_cost:,.2f}). Might be in thousands?")

if power_col:
    avg_power = df[power_col].mean()
    if avg_power < 100:
        issues.append(f"Power values too small (avg: {avg_power:.2f}). Should be 2000-3000 kWh/MT.")

if mn_col:
    avg_mn = df[mn_col].mean()
    if avg_mn < 10:
        issues.append(f"MN Recovery too small (avg: {avg_mn:.2f}%). Should be 70-85%.")

if issues:
    print("❌ POTENTIAL ISSUES FOUND:")
    for issue in issues:
        print(f"  • {issue}")
    print("\n💡 SUGGESTIONS:")
    print("  1. Check if values are scaled (e.g., in thousands)")
    print("  2. Check if decimal points are wrong")
    print("  3. Check if units are correct")
else:
    print("✅ No obvious data issues found")

print("\n📋 TO FIX THE APP:")
print("1. We need to see your actual column names")
print("2. We need to see your actual values")
print("3. We'll adjust the calculations accordingly")
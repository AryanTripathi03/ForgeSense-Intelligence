# analyze_my_data.py - Analyze your actual data structure
import pandas as pd
import numpy as np
import os

def analyze_data_structure(file_path):
    """Analyze the structure of your furnace data"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📊 Analyzing: {file_path}")
    print("=" * 60)
    
    # Read the file
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Clean column names
    df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]
    
    # Show all columns
    print("\n📋 ALL COLUMNS:")
    print("-" * 40)
    for i, col in enumerate(df.columns, 1):
        print(f"{i:3}. {col}")
    
    # Categorize columns
    print("\n🔍 COLUMN CATEGORIZATION:")
    print("-" * 40)
    
    categories = {
        'Furnace Identification': [],
        'Date/Time': [],
        'Production': [],
        'Cost': [],
        'Power': [],
        'Chemistry': [],
        'Recovery': [],
        'Breakdown': [],
        'Other': []
    }
    
    for col in df.columns:
        col_lower = str(col).lower()
        
        if any(word in col_lower for word in ['furnace', 'unit', 'plant']):
            categories['Furnace Identification'].append(col)
        elif any(word in col_lower for word in ['date', 'time', 'day', 'month', 'week']):
            categories['Date/Time'].append(col)
        elif any(word in col_lower for word in ['prod', 'qty', 'quantity', 'output', 'yield']):
            categories['Production'].append(col)
        elif any(word in col_lower for word in ['cost', 'price', 'expense', '₹', 'rs']):
            categories['Cost'].append(col)
        elif any(word in col_lower for word in ['power', 'electric', 'kwh', 'mw', 'load']):
            categories['Power'].append(col)
        elif any(word in col_lower for word in ['mn', 'si', 'c%', 'fe', 'cao', 'sio2', 'chemistry']):
            categories['Chemistry'].append(col)
        elif any(word in col_lower for word in ['recovery', 'efficiency', 'ratio']):
            categories['Recovery'].append(col)
        elif any(word in col_lower for word in ['breakdown', 'bd', 'downtime', 'mins', 'stop']):
            categories['Breakdown'].append(col)
        else:
            categories['Other'].append(col)
    
    # Print categorized columns
    for category, cols in categories.items():
        if cols:
            print(f"\n{category} ({len(cols)} columns):")
            for col in cols[:5]:  # Show first 5
                print(f"  • {col}")
            if len(cols) > 5:
                print(f"  ... and {len(cols) - 5} more")
    
    # Data quality check
    print("\n📈 DATA QUALITY CHECK:")
    print("-" * 40)
    
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Missing values
    missing_data = df.isnull().sum()
    cols_with_missing = missing_data[missing_data > 0]
    
    if len(cols_with_missing) > 0:
        print(f"\n⚠️ Columns with missing values:")
        for col, missing_count in cols_with_missing.items():
            missing_pct = (missing_count / len(df)) * 100
            print(f"  • {col}: {missing_count} missing ({missing_pct:.1f}%)")
    else:
        print("✅ No missing values found")
    
    # Data types
    print(f"\n📊 Data types:")
    dtypes = df.dtypes.value_counts()
    for dtype, count in dtypes.items():
        print(f"  • {dtype}: {count} columns")
    
    # Sample data
    print("\n👀 SAMPLE DATA (first row):")
    print("-" * 40)
    for col in df.columns[:10]:  # First 10 columns
        print(f"{col}: {df.iloc[0][col] if pd.notnull(df.iloc[0][col]) else 'NaN'}")
    
    if len(df.columns) > 10:
        print(f"... and {len(df.columns) - 10} more columns")
    
    # Suggestions for analysis
    print("\n💡 SUGGESTIONS FOR ANALYSIS:")
    print("-" * 40)
    
    if categories['Production']:
        prod_col = categories['Production'][0]
        print(f"1. Use '{prod_col}' as production column")
    
    if categories['Cost']:
        cost_col = categories['Cost'][0]
        print(f"2. Use '{cost_col}' as cost column")
    
    if categories['Furnace Identification']:
        furnace_col = categories['Furnace Identification'][0]
        print(f"3. Use '{furnace_col}' as furnace identifier")
    
    if categories['Date/Time']:
        date_col = categories['Date/Time'][0]
        print(f"4. Use '{date_col}' as date column")
    
    return df

if __name__ == "__main__":
    # Test with sample data first
    print("Testing with sample data...")
    df_sample = analyze_data_structure('sample_furnace_data.xlsx')
    
    print("\n" + "=" * 60)
    print("🎯 To analyze YOUR actual data:")
    print("1. Place your Excel file in the project folder")
    print("2. Update the file name below")
    print("3. Run: python analyze_my_data.py")
    print("\nExample:")
    print('analyze_data_structure("YOUR_COMPANY_DATA.xlsx")')
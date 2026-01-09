@echo off
echo ========================================
echo   ENTERPRISE FURNACE INTELLIGENCE SYSTEM
echo ========================================
echo.

REM Create directory structure
if not exist src (
    mkdir src
    mkdir src\core
    mkdir src\intelligence
)

echo.
echo Installing required packages...
pip install pandas numpy streamlit plotly openpyxl

echo.
echo Creating module files...
echo Please create the Python files from the code above
echo.

echo Setup ready!
echo.
echo To run the system:
echo 1. streamlit run app_enterprise.py
echo 2. Upload your complete furnace data
echo 3. Input only MVA capacities
echo 4. Get comprehensive analysis
echo.
pause
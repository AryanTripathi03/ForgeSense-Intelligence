@echo off
echo ========================================
echo   CAPACITY-BASED FURNACE INTELLIGENCE
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo Installing required packages...
pip install pandas numpy streamlit plotly openpyxl

echo.
echo Creating directory structure...
if not exist src (
    mkdir src
    mkdir src\core
    mkdir src\intelligence
)

echo.
echo Setup complete!
echo.
echo To run the system:
echo 1. Make sure virtual environment is active
echo 2. Run: streamlit run app_capacity_based.py
echo 3. Upload your furnace data Excel file
echo 4. Input furnace capacity parameters
echo.
pause
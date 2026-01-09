@echo off
echo Installing Furnace Intelligence System...
echo.

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
pip install --upgrade pip
pip install pandas==2.1.4
pip install numpy==1.24.3
pip install streamlit==1.28.1
pip install plotly==5.18.0
pip install openpyxl==3.1.2
pip install statsmodels==0.14.0
pip install scipy==1.11.4

REM Create sample data
python create_sample.py

echo.
echo Installation complete!
echo.
echo To run the system:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the app: streamlit run app_production.py
echo.
pause
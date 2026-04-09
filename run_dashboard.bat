@echo off
echo Starting PCI DSS Compliance Dashboard...
echo.
echo Dashboard Features:
echo - Real-time scan execution with animated progress
echo - Live progress tracking and status updates  
echo - Interactive charts and visualizations
echo - Executive compliance reporting
echo - Live scan logs display
echo.
echo Opening dashboard at http://localhost:8501
echo Press Ctrl+C to stop the dashboard
echo.
streamlit run dashboard.py --server.port 8501
pause
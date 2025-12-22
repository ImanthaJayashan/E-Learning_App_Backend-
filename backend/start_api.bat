@echo off
cls
echo ======================================================================
echo  HEARING DISABILITY PREDICTION API SERVER
echo ======================================================================
echo.
echo Starting the prediction API server...
echo.
echo The API will be available at:
echo   - http://localhost:5000
echo   - http://127.0.0.1:5000
echo.
echo Press CTRL+C to stop the server
echo.
echo ======================================================================
echo.

py prediction_api.py

.\venv\Scripts\python.exe -m click_analyzer.statistics_collector >out_statistics_collector.txt
if %ERRORLEVEL% neq 0 (
    echo Statistics collector failed with exit code %ERRORLEVEL%. Aborting.
    exit /b %ERRORLEVEL%
)
rem .\venv\Scripts\python.exe -m click_analyzer.test_calculate_metrics >test_calculate_metrics.py.txt 2>err_test_calculate_metrics.py.txt
.\venv\Scripts\python.exe d:\content-team\click-data\one_drive_client\one_drive_client.py --upload="d:\content-team\click-data\Work\metrics\metrics_report.csv" --tokens="d:\content-team\click-data\one_drive_client\tokens_data.txt"
if %ERRORLEVEL% neq 0 (
    echo Upload failed with exit code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)
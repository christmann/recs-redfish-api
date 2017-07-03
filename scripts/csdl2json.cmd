@echo off

SET PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python36-32\python.exe

SET PROJECT_DIR=..
SET APPLICATION=%PROJECT_DIR%\applications\csdl-to-json-convertor\service.py
SET CSDL_DIR=%PROJECT_DIR%\csdlSchemas
SET JSON_DIR=%PROJECT_DIR%\schemas\OEM
SET LOG_DIR=%PROJECT_DIR%\logs
SET LOG_FILE=%LOG_DIR%\csdl2json.log

"%PYTHON_EXE%" "%APPLICATION%" --directory "%CSDL_DIR%" --outdir "%JSON_DIR%" > "%LOG_FILE%" 2>&1

if errorlevel 1 (
  echo Failed
  "%LOG_FILE%"
  exit /b %errorlevel%
) else (
  rem delete empty schema
  del "%JSON_DIR%\Validation.v1_0_0.json" >> "%LOG_FILE%" 2>&1
  echo Success
)
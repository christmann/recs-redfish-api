@echo off

SET PYTHON_EXE=C:\Users\bil.CIM\AppData\Local\Programs\Python\Python36-32\python.exe

SET REDFISH_TOOLS_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api\Redfish-Tools
SET CONVERTOR_APP_DIR=%REDFISH_TOOLS_DIR%\csdl-to-json-convertor
SET CONVERTOR_SCRIPT=%CONVERTOR_APP_DIR%\service.py

SET PROJECT_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api
SET CSDL_DIR=%PROJECT_DIR%\csdlSchemas
SET JSON_DIR=%PROJECT_DIR%\schemas
SET LOG_DIR=%PROJECT_DIR%\logs
SET LOG_FILE=%LOG_DIR%\csdl2json.log

"%PYTHON_EXE%" "%CONVERTOR_SCRIPT%" --directory "%CSDL_DIR%" --outdir "%JSON_DIR%" > "%LOG_FILE%" 2>&1

rem delete empty schema
del "%JSON_DIR%\Validation.v1_0_0.json" >> "%LOG_FILE%" 2>&1

"%LOG_FILE%"

@echo off

SET PYTHON_EXE=C:\Users\bil.CIM\AppData\Local\Programs\Python\Python36-32\python.exe

SET REDFISH_TOOLS_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api\Redfish-Tools
SET DOC_APP_DIR=%REDFISH_TOOLS_DIR%\doc-generator
SET DOC_SCRIPT=%DOC_APP_DIR%\doc_generator.py

SET PROJECT_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api
SET CONF_DIR=%PROJECT_DIR%\config
SET DOC_SUPP_FILE=%CONF_DIR%\customsupplement.dokuwiki.md
SET JSON_DIR=%PROJECT_DIR%\schemas
SET DOC_DIR=%PROJECT_DIR%\documentation
SET DOC_FILE=%DOC_DIR%\recsbox-redfish-api.schema.dokuwiki
SET LOG_DIR=%PROJECT_DIR%\logs
SET LOG_FILE=%LOG_DIR%\json2dokuwiki-schema.log

"%PYTHON_EXE%" "%DOC_SCRIPT%" --format dokuwiki-schema --out "%DOC_FILE%" --sup "%DOC_SUPP_FILE%" "%JSON_DIR%" > "%LOG_FILE%" 2>&1

if errorlevel 1 (
  echo Failed
  "%LOG_FILE%"
  exit /b %errorlevel%
) else (
  echo Success
  "%DOC_FILE%"
)

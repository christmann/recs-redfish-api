@echo off

SET PYTHON_EXE=C:\Users\bil.CIM\AppData\Local\Programs\Python\Python36-32\python.exe

SET REDFISH_TOOLS_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api\Redfish-Tools
SET DOC_APP_DIR=%REDFISH_TOOLS_DIR%\doc-generator
SET DOC_SCRIPT=%DOC_APP_DIR%\doc_generator.py

SET PROJECT_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api
SET CONF_DIR=%PROJECT_DIR%\config
SET DOC_SUPP_FILE=%CONF_DIR%\customsupplement.dokuwiki.md
SET REF_FILE=%CONF_DIR%\schema-reference-properties.json
SET JSON_DIR=%PROJECT_DIR%\schemas
SET DOC_DIR=%PROJECT_DIR%\documentation
SET INTRO_DOC_FILE=%DOC_DIR%\recsbox-redfish-api.main.dokuwiki
SET SCHEMA_DOC_FILE=%DOC_DIR%\recsbox-redfish-api.schema.dokuwiki
SET LOG_DIR=%PROJECT_DIR%\logs
SET LOG_FILE=%LOG_DIR%\json2dokuwiki.log

"%PYTHON_EXE%" "%DOC_SCRIPT%" --format dokuwiki --out "%SCHEMA_DOC_FILE%" --sup "%DOC_SUPP_FILE%" --add %REF_FILE% "%JSON_DIR%" > "%LOG_FILE%" 2>&1

if errorlevel 1 (
  echo Failed
  "%LOG_FILE%"
  exit /b %errorlevel%
) else (
  echo Success
  "%REF_FILE%"
  "%INTRO_DOC_FILE%"
  "%SCHEMA_DOC_FILE%"
)

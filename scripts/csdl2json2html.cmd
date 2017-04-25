@echo off

SET PYTHON_EXE=C:\Users\bil.CIM\AppData\Local\Programs\Python\Python36-32\python.exe

SET REDFISH_TOOLS_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api\Redfish-Tools
SET CONVERTOR_APP_DIR=%REDFISH_TOOLS_DIR%\csdl-to-json-convertor
SET CONVERTOR_SCRIPT=%CONVERTOR_APP_DIR%\service.py
SET DOC_APP_DIR=%REDFISH_TOOLS_DIR%\doc-generator
SET DOC_SCRIPT=%DOC_APP_DIR%\doc_generator.py
SET DOC_SUPP_FILE=%DOC_APP_DIR%\customsupplement.md

SET PROJECT_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api
SET CSDL_DIR=%PROJECT_DIR%\csdlSchemas
SET JSON_DIR=%PROJECT_DIR%\schemas
SET DOC_DIR=%PROJECT_DIR%\documentation
SET DOC_FILE=%DOC_DIR%\recsbox-redfish-api.html
SET LOG_DIR=%PROJECT_DIR%\logs
SET LOG_FILE=%LOG_DIR%\csdl2json2html.log

"%PYTHON_EXE%" "%CONVERTOR_SCRIPT%" --directory "%CSDL_DIR%" --outdir "%JSON_DIR%" > "%LOG_FILE%" 2>&1

rem delete empty schema
del "%JSON_DIR%\Validation.v1_0_0.json"

"%PYTHON_EXE%" "%DOC_SCRIPT%" --format html --out "%DOC_FILE%" --sup "%DOC_SUPP_FILE%" "%JSON_DIR%" >> "%LOG_FILE%" 2>&1

"%DOC_FILE%"
"%LOG_FILE%"

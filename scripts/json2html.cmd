@echo off

SET JAVA_EXE=java.exe

SET PROJECT_DIR=..
SET APPLICATION=%PROJECT_DIR%\applications\redfish-documentor\RedfishDocumentor.jar
SET CSDL_DIR=%PROJECT_DIR%\csdlSchemas
SET JSON_DIR=%PROJECT_DIR%\schemas
SET DOC_DIR=%PROJECT_DIR%\docs
SET CODE_DIR=%PROJECT_DIR%\code
SET TEST_DIR=%CODE_DIR%\test
SET CONF_DIR=%PROJECT_DIR%\config
SET FILTER_FILE=%CONF_DIR%\filter.json
SET URIFILTER_FILE=%CONF_DIR%\uri.json
SET OPERATIONS_FILE=%CONF_DIR%\operations.json
SET LITERALS_FILE=%CONF_DIR%\literals.json
SET MAPPING_FILE=%CONF_DIR%\class-mapping.json
SET OEM_PREFIXES=EID_47597_RECSBox

"%JAVA_EXE%" -jar "%APPLICATION%" --json "%JSON_DIR%" --csdl "%CSDL_DIR%" --doc "%DOC_DIR%" --oem "%OEM_PREFIXES%" --filter "%FILTER_FILE%" --urifilter "%URIFILTER_FILE%" --operations "%OPERATIONS_FILE%" --literals "%LITERALS_FILE%" --generatecode "%CODE_DIR%" --generateimpl --generatetest "%TEST_DIR%" --mapping "%MAPPING_FILE%" 2>&1

if errorlevel 1 (
  echo Generation of the documentation failed!
  exit /b %errorlevel%
)

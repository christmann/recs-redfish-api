@echo off

SET JAVA_EXE=C:\Program Files\Java\jdk1.8.0_131\bin\java.exe

SET APP_JAR=C:\Users\bil.CIM\workspace\java\redfish-documentor\redfish-documentor-launcher\dist\RedfishDocumentor.jar

SET PROJECT_DIR=C:\Users\bil.CIM\workspace\other\recs-redfish-api
rem SET CONF_DIR=%PROJECT_DIR%\config
rem SET DOC_SUPP_FILE=%CONF_DIR%\customsupplement.md
SET JSON_DIR=%PROJECT_DIR%\schemas
SET CSDL_DIR=%PROJECT_DIR%\csdlSchemas
SET DOC_DIR=%PROJECT_DIR%\documentation
SET OEM_PREFIXES=EID_47597_RECSBox

"%JAVA_EXE%" -jar "%APP_JAR%" --json "%JSON_DIR%" --csdl "%CSDL_DIR%" --doc "%DOC_DIR%" --oem "%OEM_PREFIXES%" 2>&1

if errorlevel 1 (
  echo Generation of the documentation failed!
  exit /b %errorlevel%
)

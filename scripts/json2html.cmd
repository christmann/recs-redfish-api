@echo off

SET JAVA_EXE=%ProgramFiles%\Java\jdk1.8.0_131\bin\java.exe

SET PROJECT_DIR=..
SET APPLICATION=%PROJECT_DIR%\applications\redfish-documentor\RedfishDocumentor.jar
SET CSDL_DIR=%PROJECT_DIR%\csdlSchemas
SET JSON_DIR=%PROJECT_DIR%\schemas
SET DOC_DIR=%PROJECT_DIR%\documentation
SET CONF_DIR=%PROJECT_DIR%\config
SET OEM_PREFIXES=EID_47597_RECSBox

"%JAVA_EXE%" -jar "%APPLICATION%" --json "%JSON_DIR%" --csdl "%CSDL_DIR%" --doc "%DOC_DIR%" --oem "%OEM_PREFIXES%" 2>&1

if errorlevel 1 (
  echo Generation of the documentation failed!
  exit /b %errorlevel%
)

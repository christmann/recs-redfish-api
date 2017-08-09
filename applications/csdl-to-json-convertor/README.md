# CSDL-to-JSON-Convertor

The CSDL-to-JSON-Convertor is a **Python 3** application, with which JSON schema files can be generated from CSDL files. It is part of the [Redfish-Tools](https://github.com/DMTF/Redfish-Tools).

## Usage

The application can be started by running the **service.py** with Python 3.  
One can adapt the **csdl2json.cmd** file in the **scripts** folder to conveniently run this application on a Windows system.

### Parameters

#### --directory

This parameter specifies the source folder, which contains the CSDL schema files.

#### --outdir

This parameter points to the folder where the JSON schema files will be generated in.

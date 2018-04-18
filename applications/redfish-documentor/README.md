# Redfish Documentor

The Redfish Documentor is a **Java 8** application, with which a HTML documatation can be generated from a set of JSON- and CSDL schema files.

## Usage

The application can be started by running the **RedfishDocumentor.jar** with Java 8.  
One can adapt the **json2html.cmd** file in the **scripts** folder to conveniently run this application on a Windows system.

### Parameters

#### --json

This parameter specifies the source folder, which contains the JSON schema files.

#### --csdl

This parameter specifies the source folder, which contains the CSDL schema files.

#### --doc

This parameter points to the folder where the HTML documentation files will be generated in. This folder will be cleared automatically before new documentation is generated.

#### --oem

This optional parameter accepts a comma-separared list of prefixes to identify OEM extension namespaces.

#### --filter

This optional parameter points to a filter file, which specifies the properties to be ignored during the documentation generation. It has to be a valid JSON file. An example can be seen in the **config** folder.  
Note: Setting the value __true__ for a property within that filter file will completely ignore the corresponding property, whereas properties with the value __false__ will be documented but greyed out in the documentation.

#### --operations

This optional parameter points to a operations file, which specifies the available operations (other than GET) per defined Resource. If not specified, only GET operations will be available.

#### --schema

This optional parameter points to the folder where the used schema files will be copied to. If not specified, no schema files will be copied.

#### --generatecode

This optional parameter points to the base folder where the java files will be generated. This folder will be cleared automatically before new code is generated. If not specified, no code is generated.

#### --basepackage

This optional parameter specifies the name of the base java package for the generated java classes. This parameter has to be set, if 'generatecode' is set.


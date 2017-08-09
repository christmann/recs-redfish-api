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

This parameter accepts a comma-separared list of prefixes to identify OEM extension namespaces.

#### --filter

This parameter points to a filter file, which specifies the properties to be ignored during the documentation generation. It has to be a valid JSON file. An example can be seen in the **config** folder.  
Note: Setting the value __true__ for a property within that filter file will completely ignore the corresponding property, whereas properties with the value __false__ will be documented but greyed out in the documentation.

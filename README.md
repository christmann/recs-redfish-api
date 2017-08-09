# RECS|Box Redfish API

This project contains the RECS|Box Redfish API and tools to generate JSON schema files and a HTML documentation.


The schema files of the Redfish API are located in the folders **schemas** (JSON) and **csdlSchemas** (CSDL). The OEM schemas, extending the original Redfish API are located in the **OEM** subfolders of these two schema folders.  
There are two tools in the **applications** folder. The first one is the **sdl-to-json-convertor**, which is used to generate the JSON schema files from the CSDL schema files. The second one is the **redfish-documentor**, which creates the HTML documentation for the schema files located in the two schema folders mentioined above. The usage of both tools is decribed in teh README.md files in their corresponding folders. There is a filter file in the **config** folder, which can be utilised by the redfish-documentor to filter out properties of the complete API. Adittionally, two CMD scripts for Windows are located in the **scripts** folder, which can be adapted an used to conveniently use the two aforementioned applications.  
Finally, the generated HTML documentation of the current state of the RECS|Box Redfish API is located in the **documentation** folder. It can be explored by opening the index.html file.
# RECS|Box Redfish API

This project contains the RECS|Box Redfish API and tools to generate JSON schema files and a HTML documentation.


The schema files of the Redfish API are located in the folders **schemas** (JSON) and **csdlSchemas** (CSDL). The OEM schemas, extending the original Redfish API are located in the **OEM** subfolders of these two schema folders.  
There are two tools in the **applications** folder. The first one is the **csdl-to-json-convertor**, which is used to generate the JSON schema files from the CSDL schema files. The second one is the **redfish-documentor**, which creates the HTML documentation for the schema files located in the two schema folders mentioined above. The usage of both tools is decribed in the README.md files in their corresponding folders. There is a filter file in the **config** folder, which can be utilised by the redfish-documentor to filter out properties of the complete API. Additionally, two CMD scripts for Windows are located in the **scripts** folder, which can be adapted and used to conveniently use the two aforementioned applications.  
Finally, the generated HTML documentation of the current state of the RECS|Box Redfish API is located in the **docs** folder. It can be explored by opening the index.html file locally or online at [https://christmann.github.io/recs-redfish-api/index.html](https://christmann.github.io/recs-redfish-api/index.html).

## Acknowledgements

*This software extension has been conducted within the project M2DC, started in January 2016.  This  project  has  received  funding  from  the  European  Union’s  Horizon  2020  research  and innovation programme under grant agreement No 688201.*
*This work has been supported by EU H2020 ICT project LEGaTO, contract #780681.*
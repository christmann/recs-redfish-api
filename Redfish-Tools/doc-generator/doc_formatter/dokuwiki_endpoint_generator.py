# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tools/LICENSE.md

"""
File : dokuwiki_endpoint_generator.py

Brief : This file contains definitions for the DokuwikiEndpointGenerator class.

Initial author: Second Rise LLC.
"""

import json
from json.decoder import JSONDecodeError
import math
from . import DocFormatter

class DokuwikiEndpointGenerator(DocFormatter):
    """Provides methods for generating dokuwiki endpoints from Redfish schemas.
    """

    link_basepath = 'documentation:redfish_api:endpoints:'
    space = '\ '
    
    references = dict()

    def __init__(self, property_data, traverser, config):
        super(DokuwikiEndpointGenerator, self).__init__(property_data, traverser, config)
        self.sections = []
        self.separators = {
            'inline': ', ',
            'linebreak': '\n'
            }
        
        try:
            addfile = open(config['addfile'], 'r')
        except (OSError) as ex:
            print('Unable to open', config['addfile'], 'to read:', ex)
        try:
            self.references = json.load(addfile)
        except (JSONDecodeError) as ex:
            print('Unable to JSON decode', config['addfile'], 'to read:', ex)

    def parse_property_info(self, schema_name, prop_name, traverser, prop_infos, current_depth):
        """Parse a list of one more more property info objects into strings for display.

        Returns a dict of 'prop_type', 'read_only', descr', 'prop_is_object', 'prop_is_ref',
        'prop_is_array', 'object_description', 'prop_details', 'item_description',
        'has_direct_prop_details'
        """

        if len(prop_infos) == 1:
            prop_info = prop_infos[0]
            if isinstance(prop_info, dict):
                return self._parse_single_property_info(schema_name, prop_name, prop_info, current_depth)
            else:
                return self.parse_property_info(schema_name, prop_name, prop_info, current_depth)

        parsed = {'prop_type': [],
                  'prop_units': False,
                  'prop_pattern': False,
                  'prop_format': False,
                  'prop_min': False,
                  'prop_max': False,
                  'read_only': False,
                  'descr': [],
                  'prop_is_object': False,
                  'prop_is_ref': False,
                  'prop_is_array': False,
                  'object_description': [],
                  'item_description': [],
                  'prop_details': {},
                  'has_direct_prop_details': False}

        anyOf_details = [self.parse_property_info(schema_name, prop_name, traverser, x, current_depth) for x in prop_infos]

        # Remove details for anyOf props with prop_type = 'null'.
        details = []
        has_null = False
        for det in anyOf_details:
            if len(det['prop_type']) == 1 and 'null' in det['prop_type']:
                has_null = True
            else:
                details.append(det)

        # Uniquify these properties and save as lists:
        props_to_combine = ['prop_type', 'descr', 'object_description', 'item_description']

        for property_name in props_to_combine:
            property_values = []
            for det in anyOf_details:
                if isinstance(det[property_name], list):
                    for val in det[property_name]:
                        if val and val not in property_values:
                            property_values.append(val)
                else:
                    val = det[property_name]
                    if val and val not in property_values:
                        property_values.append(val)

            parsed[property_name] = property_values

        # add back null if we found one:
        if has_null:
            parsed['prop_type'].append('null')

        # read_only and units should be the same for all
        parsed['read_only'] = details[0]['read_only']
        parsed['prop_units'] = details[0]['prop_units']
        parsed['prop_pattern'] = details[0]['prop_pattern']
        parsed['prop_format'] = details[0]['prop_format']
        parsed['prop_min'] = details[0]['prop_min']
        parsed['prop_max'] = details[0]['prop_max']

        for det in details:
            parsed['prop_is_object'] |= det['prop_is_object']
            parsed['prop_is_ref'] |= det['prop_is_ref']
            parsed['prop_is_array'] |= det['prop_is_array']
            parsed['has_direct_prop_details'] |= det['has_direct_prop_details']
            parsed['prop_details'].update(det['prop_details'])

        return parsed


    def _parse_single_property_info(self, schema_name, prop_name, prop_info, current_depth):
        """Parse definition of a specific property into strings for display.

        Returns a dict of 'prop_type', 'prop_units', 'read_only', descr', 'prop_is_object', 'prop_is_ref',
        'prop_is_array', 'object_description', 'prop_details', 'item_description',
        'has_direct_prop_details'
        """

        traverser = self.traverser

        # type may be a string or a list.
        prop_details = {}
        prop_type = prop_info.get('type', [])
        prop_is_object = False; object_description = ''
        prop_is_ref = False
        prop_is_array = False; item_description = ''
        has_prop_details = False

        if isinstance(prop_type, list):
            prop_is_object = 'object' in prop_type
            prop_is_array = 'array' in prop_type
        else:
            prop_is_object = prop_type == 'object'
            prop_is_array = prop_type == 'array'
            prop_type = [ prop_type ]

        if prop_is_object:
            prop_properties = prop_info.get('properties', [])
            prop_is_ref = '@odata.id' in prop_properties
            if prop_is_ref:
                prop_is_object = False
                prop_type = [ 'reference' ]

        prop_units = prop_info.get('units')
        prop_pattern = prop_info.get('pattern')
        prop_format = prop_info.get('format')
        prop_min = prop_info.get('minimum')
        prop_max = prop_info.get('maximum')

        read_only = prop_info.get('readonly')
        if self.config['normative'] and 'longDescription' in prop_info:
            descr = prop_info.get('longDescription', '')
        else:
            descr = prop_info.get('description', '')

        # Items, if present, will have a definition with either an object or a $ref:
        prop_item = prop_info.get('items')
        if isinstance(prop_item, dict):
            prop_items = self.extend_property_info(schema_name, prop_item, traverser)

        # Enumerations go into Property Details
        prop_enum = prop_info.get('enum')
        supplemental_details = None

        if 'supplemental' in self.config and 'Property Details' in self.config['supplemental']:
            detconfig = self.config['supplemental']['Property Details']
            if schema_name in detconfig and prop_name in detconfig[schema_name]:
                supplemental_details = detconfig[schema_name][prop_name]

        if prop_enum or supplemental_details:
            has_prop_details = True

            if self.config['normative'] and 'enumLongDescriptions' in prop_info:
                prop_enum_details = prop_info.get('enumLongDescriptions')
            else:
                prop_enum_details = prop_info.get('enumDescriptions')
            prop_details[prop_name] = self.format_property_details(prop_name, prop_type, prop_enum, prop_enum_details,
                                                              supplemental_details)

        # embedded object:
        if current_depth < self.max_drilldown and prop_is_object:
            object_formatted = self.format_object_description(schema_name, prop_info, traverser, current_depth)
            object_description = object_formatted['rows']
            if object_formatted['details']:
                prop_details.update(object_formatted['details'])

        # embedded items:
        if current_depth < self.max_drilldown and prop_is_array:
            item_formatted = self.format_list_of_object_descriptions(schema_name, prop_items, traverser, current_depth)
            item_description = item_formatted['rows']
            if item_formatted['details']:
                prop_details.update(item_formatted['details'])

        return {'prop_type': prop_type,
                'prop_units': prop_units,
                'prop_pattern': prop_pattern,
                'prop_format': prop_format,
                'prop_min': prop_min,
                'prop_max': prop_max,
                'read_only': read_only,
                'descr': descr,
                'prop_is_object': prop_is_object,
                'prop_is_ref': prop_is_ref,
                'prop_is_array': prop_is_array,
                'object_description': object_description,
                'item_description': item_description,
                'prop_details': prop_details,
                'has_direct_prop_details': has_prop_details}


    def format_property_row(self, schema_name, prop_name, prop_info, meta=None, current_depth=0):
        """Format information for a single property. Returns an object with 'row' and 'details'.

        'row': content for the main table being generated.
        'details': content for the Property Details section.

        This may include embedded objects with their own properties.
        """

        traverser = self.traverser
        formatted = []     # The row itself
        indentation_string = self.space * 6 * current_depth

        if not meta:
            meta = {}

        formatted_details = self.parse_property_info(schema_name, prop_name, traverser, prop_info, current_depth)

        # Eliminate dups in these these properties and join with a delimiter:
        props = {
            'prop_type': self.separators['inline'],
            'descr': self.separators['linebreak'],
            'object_description': self.separators['linebreak'],
            'item_description': self.separators['linebreak']
            }

        for property_name, delim in props.items():
            if isinstance(formatted_details[property_name], list):
                property_values = []
                for val in formatted_details[property_name]:
                    if val and val not in property_values:
                        property_values.append(val)
                formatted_details[property_name] = delim.join(property_values)

        name_and_version = self.escape_for_dokuwiki(prop_name, self.config['escape_chars'])

        collection_postfix = 'Collection'
        
        if formatted_details['prop_is_ref']:
            entity_name = name_and_version
            if meta and 'entity_type' in meta:
                entity_name = meta['entity_type']
                if entity_name and entity_name.endswith(collection_postfix):
                    formatted_details['prop_details'] = False
                if not schema_name in self.references:
                    self.references[schema_name] = dict()
                if not prop_name in self.references[schema_name]:
                    self.references[schema_name][prop_name] = dict()
                    self.references[schema_name][prop_name]['type'] = entity_name
                    self.references[schema_name][prop_name]['description'] = formatted_details['descr']
                    endpoint_name = entity_name
                    if endpoint_name.endswith(collection_postfix):
                        endpoint_name = endpoint_name[:-len(collection_postfix)]
                        if not endpoint_name.endswith('s'):
                            endpoint_name += 's'
                    if schema_name != 'ServiceRoot':
                        if schema_name.endswith('Service'):
                            endpoint_name = schema_name + '/' + endpoint_name
                        else:
                            endpoint_name = schema_name + '/{' + schema_name + 'ID}/' + endpoint_name
                    self.references[schema_name][prop_name]['endpoint'] = '/redfish/v1/' + endpoint_name
            
            name_and_version = '**[[' + self.link_basepath + entity_name.lower() + '|' + name_and_version + ']]**'
        else:
            name_and_version = '**' + self.escape_for_dokuwiki(prop_name, self.config['escape_chars']) + '**'

        if formatted_details['prop_is_object']:
            if formatted_details['object_description'] == '':
                name_and_version += ' {}'
            else:
                name_and_version += ' {'

        if formatted_details['prop_is_array']:
            if formatted_details['item_description'] == '':
                name_and_version += ' [ {} ]'
            else:
                name_and_version += ' [ {} ]'

        if formatted_details['prop_units']:
            formatted_details['descr'] += '\\\\ unit: ' + formatted_details['prop_units']
        if formatted_details['prop_pattern']:
            formatted_details['descr'] += '\\\\ pattern: ' + formatted_details['prop_pattern']
        if formatted_details['prop_format']:
            formatted_details['descr'] += '\\\\ format: ' + formatted_details['prop_format']
        if formatted_details['prop_min']:
            formatted_details['descr'] += '\\\\ minimum: ' + str(formatted_details['prop_min'])
        if formatted_details['prop_max']:
            formatted_details['descr'] += '\\\\ maximum: ' + str(formatted_details['prop_max'])

        # If there are prop_details (enum details), add a note to the description:
        if formatted_details['has_direct_prop_details']:
            formatted_details['descr'] += '\\\\ *See Property Details, below, for more information about this property.*'

        prop_type = formatted_details['prop_type']

        prop_perm = ''
        if formatted_details['read_only']:
            prop_perm = 'read-only'
        else:
            prop_perm = 'read-write'

        

        row = []
        row.append(indentation_string + name_and_version)
        row.append(prop_type)
        row.append(prop_perm)
        row.append(formatted_details['descr'])

        formatted.append('| ' + ' | '.join(row) + ' |')

        if len(formatted_details['object_description']) > 0:
            formatted.append(formatted_details['object_description'])
            formatted.append('| ' + indentation_string + '} |   |   |')

#        if len(formatted_details['item_description']) > 0:
#            formatted.append(formatted_details['item_description'])
#            formatted.append('| ' + indentation_string + '} ] |   |   |')

        return({'row': '\n'.join(formatted), 'details':formatted_details['prop_details']})


    def format_property_details(self, prop_name, prop_type, enum, enum_details, supplemental_details):
        """Generate a formatted table of enum information for inclusion in Property Details."""

        contents = []
        contents.append('== ' + prop_name + ' ==\n')

        if isinstance(prop_type, list):
            prop_type = ', '.join(prop_type)

        if supplemental_details:
            contents.append('\n' + supplemental_details + '\n')

        if enum_details:
            contents.append('^ ' + prop_type + ' ^ Description ^')
            enum.sort()
            for enum_item in enum:
                contents.append('| ' + enum_item + ' | ' + enum_details.get(enum_item, '') + ' |')

        elif enum:
            contents.append('^ ' + prop_type + ' ^')
            for enum_item in enum:
                contents.append('| ' + enum_item + ' | ')

        return '\n'.join(contents) + '\n'


    def format_list_of_object_descriptions(self, schema_name, prop_items, traverser, current_depth):
        """Format a (possibly nested) list of embedded objects.

        We expect this to amount to one definition, usually for 'items' in an array."""

        if isinstance(prop_items, dict):
            return self.format_object_description(schema_name, prop_items, traverser, current_depth)

        rows = []
        details = {}
        if isinstance(prop_items, list):
            for prop_item in prop_items:
                formatted = self.format_list_of_object_descriptions(schema_name, prop_item, traverser, current_depth)
                rows.extend(formatted['rows'])
                details.update(formatted['details'])
            return ({'rows': rows, 'details': details})

        return None


    def emit(self):
        """ Output contents thus far """

        endpoints = dict()
        
        for schema_name in self.references:
            for prop_name in self.references[schema_name]:
                endpoint = self.references[schema_name][prop_name]['endpoint']
                type = self.references[schema_name][prop_name]['type']
                description = self.references[schema_name][prop_name]['description']
                if not type in endpoints:
                    endpoints[type] = dict()
                if not schema_name in endpoints[type]:
                    endpoints[type][schema_name] = dict()
                if not prop_name in endpoints[type][schema_name]:
                    endpoints[type][schema_name][prop_name] = dict()
                endpoints[type][schema_name][prop_name]['description'] = description
                endpoints[type][schema_name][prop_name]['endpoint'] = endpoint

        contents = []
        
        contents.append('===== Endpoint Definition =====\n')
        
        contents.append('^ Schema ^ URI ^')
        contents.append('| [[' +  self.link_basepath + 'protocol_version|Protocol Version]] | /redfish |')
        contents.append('| [[' +  self.link_basepath + 'metadata|Metadata]] | /redfish/v1/$metadata |')
        contents.append('| [[' +  self.link_basepath + 'odata|OData]] | /redfish/v1/odata |')
        contents.append('| [[' +  self.link_basepath + 'service_root|ServiceRoot]] | /redfish/v1 |')
        
        for type in endpoints:
            firstTypeRow = True
            for schema_name in endpoints[type]:
                for prop_name in endpoints[type][schema_name]:
                    description = endpoints[type][schema_name][prop_name]['description']
                    endpoint = endpoints[type][schema_name][prop_name]['endpoint']
                    #endpoint_name = endpoint.rsplit('/', 1)[1]
                    #endpoint_link = 'xxxTODOxxx/{' + schema_name + 'ID}/' + endpoint_name
                    #link_path = self.link_basepath + endpoint.replace('/redfish/v1/', '', 1).replace('/', '_').lower()
                    link_path = self.link_basepath + type.lower()
                    schema_col = ':::'
                    if firstTypeRow:
                        schema_col = '[[' +  link_path + '|' + type + ']]'
                    contents.append('| ' +  schema_col + ' | ' + endpoint + ' | ')
                    lastSchema = schema_name
                    firstTypeRow = False

        return '\n'.join(contents)


    def output_document(self):
        """Return full contents of document"""
        return self.emit()

    def add_section(self, text):
        """ Add a top-level heading """
        text = text.split(' ')[0]
        self.this_section = {'head': text,
                             'heading': '\n===== ' + text + ' =====\n',
                             'properties': [],
                             'property_details': []
                             }

        self.sections.append(self.this_section)


    def add_description(self, text):
        """ Add the schema description """
        self.this_section['description'] = text + '\n'


    def add_json_payload(self, json_payload):
        """ Add a JSON payload for the current section """
        if json_payload:
            self.this_section['json_payload'] = '\n' + json_payload + '\n'
        else:
            self.this_section['json_payload'] = None


    def add_property_row(self, formatted_text):
        """Add a row (or group of rows) for an individual property in the current section/schema.

        formatted_row should be a chunk of text already formatted for output"""
        self.this_section['properties'].append(formatted_text)


    def add_property_details(self, formatted_details):
        """Add a chunk of property details information for the current section/schema."""
        self.this_section['property_details'].append(formatted_details)


    @staticmethod
    def escape_for_dokuwiki(text, chars):
        """Escape selected characters in text to prevent auto-formatting in dokuwiki."""
        for char in chars:
            text = text.replace(char, '\\' + char)
        return text

    def generate_output(self):
        """Generate formatted from schemas and supplemental data.

        Iterates through property_data and traverses schemas for details.
        Format of output will depend on the format_* methods of the class.
        """
        
        property_data = self.property_data
        traverser = self.traverser
        config = self.config

        schema_names = [x for x in property_data.keys()]
        schema_names.sort()
        schema_supplement = config.get('schema_supplement', {})

        for schema_name in schema_names:
            # Skip schemas in the excluded list:
            if self.skip_schema(schema_name):
                continue
            details = property_data[schema_name]

            # Look up supplemental details for this schema/version
            version = details.get('latest_version', '1')
            major_version = version.split('.')[0]
            schema_key = schema_name + '_' + major_version
            supplemental = schema_supplement.get(schema_key, {})

            if 'doc_generator_meta' not in details:
                print("WARNING: no meta data for", schema_name)
                continue
            doc_generator_meta = details['doc_generator_meta']
            definitions = details['definitions']
            properties = details['properties']

            # No output for definition-only schema.
            if len(properties) == 0:
                continue

            self.add_section(details['name_and_version'])

            # Normative docs prefer longDescription to description
            if config['normative'] and 'longDescription' in definitions[schema_name]:
                description = definitions[schema_name].get('longDescription')
            else:
                description = definitions[schema_name].get('description')

            # Override with supplemental schema description, if provided
            description = supplemental.get('Description', description)

            if description:
                self.add_description(description)

            self.add_json_payload(supplemental.get('JSONPayload'))

            if 'properties' in details.keys():
                prop_details = {}

                properties = details['properties']
                prop_names = [x for x in properties.keys()]
                prop_names = self.organize_prop_names(prop_names)
                for prop_name in prop_names:

                    meta = doc_generator_meta.get(prop_name, {})
                    prop_info = properties[prop_name]
                    prop_class = ''
                    prop_ref = prop_info.get('$ref', None)
                    prop_anyOf = prop_info.get('anyOf', None)
                    if prop_ref:
                        meta['entity_type'] = prop_ref.rsplit('/', 1)[1].strip()
                    elif prop_anyOf:
                        for item in prop_anyOf:
                            if '$ref' in item:
                                meta['entity_type'] = item['$ref'].rsplit('/', 1)[1].strip()
                                break;

                    prop_info = self.extend_property_info(schema_name, prop_info, traverser)

                    formatted = self.format_property_row(schema_name, prop_name, prop_info, meta)
                    if formatted:
                        self.add_property_row(formatted['row'])
                        if formatted['details']:
                            prop_details.update(formatted['details'])

                if len(prop_details) and (not schema_name.endswith('Collection')):
                    prop_details_sorted = []
                    detail_names = [x for x in prop_details.keys()]
                    detail_names.sort()
                    for x in detail_names:
                        self.add_property_details(prop_details[x])

        write_json_to_file(self.references, config['addfile'])
        return self.output_document()

def write_json_to_file(json_object, outfile_name):
    """Write content to a file."""
    
    try:
        outfile = open(outfile_name, 'w')
        print(json.dumps(json_object, indent=4, sort_keys=True), file=outfile)
    except (OSError) as ex:
        print('Unable to open', config['addfile'], 'to writer:', ex)
    outfile.close()
    print(outfile.name, "written.")

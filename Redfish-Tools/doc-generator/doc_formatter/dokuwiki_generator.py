# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tools/LICENSE.md

"""
File : dokuwiki_generator.py

Brief : This file contains definitions for the DokuwikiGenerator class.

Initial author: Second Rise LLC.
"""

import math
from . import DocFormatter

class DokuwikiGenerator(DocFormatter):
    """Provides methods for generating dokuwiki content from Redfish schemas.
    """


    def __init__(self, property_data, traverser, config):
        super(DokuwikiGenerator, self).__init__(property_data, traverser, config)
        self.max_drilldown = 2
        self.sections = []
        self.separators = {
            'inline': ', ',
            'linebreak': '\n'
            }
        self.special_chars = {
            'bold': '**',
            'italic': '//',
            'underline': '__',
            'hcell_delimiter': '^',
            'cell_delimiter': '|',
            'whitespace': '\ ',
            'linebreak': '\\\\ '
            }
        
        for special_char in self.special_chars.values():
            if not special_char in config['escape_chars']:
                config['escape_chars'].append(special_char)
        
        self.schema_link_basepath = 'documentation:redfish_api:schema_definition#'
        #self.endpoint_link_basepath = 'documentation:redfish_api:endpoints:'
        
        schema_filename = config['outfile']
        self.intro_filename = schema_filename.replace('.schema.', '.main.')
        
        self.preprocess_property_data()


    def preprocess_property_data(self):
        """Adds additional meta information to the properties
        """
        
        for schema_name in self.property_data:
            if self.skip_schema(schema_name):
                continue
            
            schema_details = self.property_data[schema_name]
            
            if 'doc_generator_meta' not in schema_details:
                schema_details['doc_generator_meta'] = {}
            
            doc_generator_meta = schema_details['doc_generator_meta']
            
            required = []
            requiredOnCreate = []
            
            if 'definitions' in schema_details.keys() and schema_name in schema_details['definitions']:
                definition = schema_details['definitions'][schema_name]
                
                required = definition.get('required', [])
                requiredOnCreate = definition.get('requiredOnCreate', [])
            
            if 'properties' in schema_details.keys():
                prop_details = {}

                for prop_name in schema_details['properties']:
                    if self.skip_property(prop_name):
                        continue
                    
                    if prop_name not in doc_generator_meta:
                        doc_generator_meta[prop_name] = {}
                    
                    meta = doc_generator_meta[prop_name]
                    prop_info = schema_details['properties'][prop_name]
                    
                    prop_ref = prop_info.get('$ref', None)
                    prop_anyOf = prop_info.get('anyOf', None)
                    prop_items = prop_info.get('items', None)
                    
                    ref_target = ''
                    
                    if prop_ref:
                        ref_target = prop_ref
                    elif prop_anyOf:
                        for element in prop_anyOf:
                            if '$ref' in element:
                                ref_target = element['$ref']
                                break;
                    elif prop_items:
                        prop_ref = prop_items.get('$ref', None)
                        prop_anyOf = prop_items.get('anyOf', None)
                        if prop_ref:
                            ref_target = prop_ref
                        elif prop_anyOf:
                            for element in prop_anyOf:
                                if '$ref' in element:
                                    ref_target = element['$ref']
                                    break;
                    
                    if ref_target:
                        meta['ref_type'] = ref_target.rsplit('/', 1)[1].strip()
                        meta['is_ref_resource'] = meta['ref_type'] in self.property_data.keys()
                    
                    meta['required'] = prop_name in required
                    meta['required_on_create'] = prop_name in requiredOnCreate


    def skip_property(self, prop_name):
        if prop_name in self.config['excluded_properties']:
            return True
        for pattern in self.config['excluded_by_match']:
            if pattern in prop_name:
                return True
        return False


    def parse_property_info(self, schema_name, prop_name, traverser, prop_infos, current_depth):
        """Parse a list of one more more property info objects into strings for display.

        Returns a dict of 'prop_type', 'read_only', descr', 'prop_is_object',
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
                  'prop_is_array': False,
                  'prop_is_nullable': False,
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
            
        if 'null' in parsed['prop_type']:
            parsed['prop_is_nullable'] = True

        # read_only and units should be the same for all
        parsed['read_only'] = details[0]['read_only']
        parsed['prop_units'] = details[0]['prop_units']
        parsed['prop_pattern'] = details[0]['prop_pattern']
        parsed['prop_format'] = details[0]['prop_format']
        parsed['prop_min'] = details[0]['prop_min']
        parsed['prop_max'] = details[0]['prop_max']

        for det in details:
            parsed['prop_is_object'] |= det['prop_is_object']
            parsed['prop_is_array'] |= det['prop_is_array']
            parsed['has_direct_prop_details'] |= det['has_direct_prop_details']
            parsed['prop_details'].update(det['prop_details'])

        return parsed


    def _parse_single_property_info(self, schema_name, prop_name, prop_info, current_depth):
        """Parse definition of a specific property into strings for display.

        Returns a dict of 'prop_type', 'prop_units', 'read_only', descr', 'prop_is_object',
        'prop_is_array', 'object_description', 'prop_details', 'item_description',
        'has_direct_prop_details'
        """

        traverser = self.traverser

        # type may be a string or a list.
        prop_details = {}
        prop_type = prop_info.get('type', [])
        prop_is_object = False; object_description = ''
        prop_is_array = False; item_description = ''
        has_prop_details = False

        if isinstance(prop_type, list):
            prop_is_object = 'object' in prop_type
            prop_is_array = 'array' in prop_type
        else:
            prop_is_object = prop_type == 'object'
            prop_is_array = prop_type == 'array'
            prop_type = [ prop_type ]

        prop_units = prop_info.get('units')
        prop_pattern = prop_info.get('pattern')
        prop_format = prop_info.get('format')
        prop_min = prop_info.get('minimum')
        prop_max = prop_info.get('maximum')
        
        prop_is_nullable = False
        if 'null' in prop_type:
            prop_is_nullable = True

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
                'prop_is_array': prop_is_array,
                'prop_is_nullable': prop_is_nullable,
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
        indentation_string = self.special_chars['whitespace'] * 6 * current_depth

        if not meta:
            meta = {}

        is_ref_resource = 'is_ref_resource' in meta and meta['is_ref_resource']

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
                
        name_and_version = self.bold(self.escape_for_dokuwiki(prop_name, self.config['escape_chars']))

        if formatted_details['prop_is_object'] and not is_ref_resource:
            if formatted_details['object_description'] == '':
                name_and_version += ' {}'
            else:
                name_and_version += ' {'

        if formatted_details['prop_is_array'] and not is_ref_resource:
            if formatted_details['item_description'] == '':
                name_and_version += ' [ {} ]'
            else:
                name_and_version += ' [ {'

        if formatted_details['prop_units']:
            formatted_details['descr'] += self.special_chars['linebreak'] + 'unit: ' + self.escape_for_dokuwiki(formatted_details['prop_units'], self.config['escape_chars'])
        if formatted_details['prop_pattern']:
            formatted_details['descr'] += self.special_chars['linebreak'] + 'pattern: ' + self.escape_for_dokuwiki(formatted_details['prop_pattern'], self.config['escape_chars'])
        if formatted_details['prop_format']:
            formatted_details['descr'] += self.special_chars['linebreak'] + 'format: ' + self.escape_for_dokuwiki(formatted_details['prop_format'], self.config['escape_chars'])
        if formatted_details['prop_min']:
            formatted_details['descr'] += self.special_chars['linebreak'] + 'minimum: ' + self.escape_for_dokuwiki(str(formatted_details['prop_min']), self.config['escape_chars'])
        if formatted_details['prop_max']:
            formatted_details['descr'] += self.special_chars['linebreak'] + 'maximum: ' + self.escape_for_dokuwiki(str(formatted_details['prop_max']), self.config['escape_chars'])

        # If there are prop_details (enum details), add a note to the description:
        if formatted_details['has_direct_prop_details']:
            formatted_details['descr'] += self.special_chars['linebreak'] + self.italic('See Property Details, below, for more information about this property.')

        prop_type = formatted_details['prop_type']
        if is_ref_resource:
            ref_type = meta.get('ref_type', None)
            if prop_type == 'object':
                prop_type = 'reference'
                if ref_type:
                    prop_type += '(' + self.link(self.schema_link_basepath + ref_type.lower(), ref_type) + ')'
            elif prop_type == 'array':
                prop_type += '(reference)'
                if ref_type:
                    prop_type = prop_type.replace('reference', 'reference(' + self.link(self.schema_link_basepath + ref_type.lower(), ref_type) + ')')

        prop_type = prop_type.replace('null', '').strip(', ')
        
        prop_perm = ''
        if formatted_details['read_only']:
            prop_perm = 'read-only'
        else:
            prop_perm = 'read-write'
        
        prop_nullable = ''
        if formatted_details['prop_is_nullable']:
            prop_nullable = 'Yes'
        
        prop_required = []
        if 'required' in meta and meta['required']:
            prop_required.append('GET')
        if 'required_on_create' in meta and meta['required_on_create']:
            prop_required.append('POST')
        
        row = []
        row.append(indentation_string + name_and_version)
        row.append(prop_type)
        row.append(prop_nullable)
        row.append(', '.join(prop_required))
        row.append(prop_perm)
        row.append(formatted_details['descr'])

        formatted.append(self.table_row(row))

        if len(formatted_details['object_description']) > 0 and not is_ref_resource:
            formatted.append(formatted_details['object_description'])
            formatted.append(self.table_row([indentation_string + '}', '', '']))

        if len(formatted_details['item_description']) > 0 and not is_ref_resource:
            formatted.append(formatted_details['item_description'])
            formatted.append(self.table_row([indentation_string + '} ]', '', '']))

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
            contents.append(self.table_header([prop_type, 'Description']))
            enum.sort()
            for enum_item in enum:
                contents.append(self.table_row([enum_item, enum_details.get(enum_item, '')]))

        elif enum:
            contents.append(self.table_header(prop_type))
            for enum_item in enum:
                contents.append(self.table_row(enum_item))

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

    def write_intro_file(self):
        """ Output contents for intro site """

        contents = []
        
        contents.append('===== Schema Definition =====\n')
        
        contents.append('<WRAP group><WRAP quarter column>')

        i = 1
        num_sections = len(self.sections)
        quarter = math.ceil(num_sections / 4)
        
        for section in self.sections:
            section_name = self.escape_for_dokuwiki(section['head'], self.config['escape_chars'])
            contents.append('  * ' + self.link(self.schema_link_basepath + section_name.lower(), section_name))
            if i % quarter == 0 and i < num_sections:
                contents.append('</WRAP><WRAP quarter column>')
            i += 1
        
        contents.append('</WRAP></WRAP>\n')
        
        self.write_to_file(self.separators['linebreak'].join(contents), self.intro_filename)
        

    def emit(self):
        """ Output contents thus far """

        contents = []
        
        contents.append('\n====== Schema Definition ======\n')

        for section in self.sections:
            contents.append(section['heading'])
            if section['description']:
                contents.append(section['description'])
            if section['json_payload']:
                contents.append(section['json_payload'])
            # something is awry if there are no properties, but ...
            if section['properties']:
                contents.append(self.table_header(['Property', 'Type', 'Nullable', 'Required', 'Permission', 'Description']))
                contents.append('\n'.join(section['properties']))
            if section['property_details'] and not section['head'].endswith('Collection'):
                contents.append('\n=== Property Details ===\n')
                contents.append('\n'.join(section['property_details']))

        return self.separators['linebreak'].join(contents)


    def output_document(self):
        """Return full contents of document"""
        
        self.write_intro_file()
        
        return self.emit()


    def extend_property_info(self, schema_name, prop_info, traverser):
        """If prop_info contains a $ref or anyOf attribute, extend it with that information.

        Returns an array of objects. Arrays of arrays of objects are possible but not expected.
        """

        prop_ref = prop_info.get('$ref', None)
        prop_anyOf = prop_info.get('anyOf', None)
        prop_infos = []

        # Properties to carry through from parent when a ref is extended:
        parent_props = ['description', 'longDescription', 'readonly']

        if prop_ref:

            if '#/definitions/idRef' in prop_ref:
                # Bit of a hack here, because we don't currently parse odata
                ref_info = {
                    "type": "object",
                    "properties" :
                    {
                        "@odata.id": {
                            "type": "string",
                            "format": "uri",
                            "readonly": True,
                            "description": "The unique identifier for a resource.",
                            "longDescription": "The value of this property shall be the unique identifier for the resource and it shall be of thee form defined in the Redfish specification."
                        }
                    },
                    "description": "A reference to a resource.",
                    "longDescription": "The value of this property shall be used for references to a resource."
                    }

            else:
                prop_ref = traverser.parse_ref(prop_ref, schema_name)
                ref_info = traverser.find_ref_data(prop_ref)

            if ref_info:
                # if specific attributes were defined in addition to a $ref, update with them:
                for x in prop_info.keys():
                    if x in parent_props:
                        ref_info[x] = prop_info[x]

                prop_info = ref_info

                if '$ref' in ref_info or 'anyOf' in ref_info:
                    return self.extend_property_info(ref_info['_from_schema_name'], ref_info, traverser)

            prop_infos.append(prop_info)

        elif prop_anyOf:
            for elt in prop_anyOf:
                if '$ref' in elt:
                    for x in prop_info.keys():
                        if x in parent_props:
                            elt[x] = prop_info[x]

                elt = self.extend_property_info(schema_name, elt, traverser)
                prop_infos.append(elt)

        else:
            prop_infos.append(prop_info)

        return prop_infos


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

    def link(self, uri, text):
        """Formats a dokuwiki link"""
        if not uri:
            uri = ''
        if not text:
            text = uri
        return '[[' + uri + '|' + text + ']]'
        
    def bold(self, text):
        """Formats a text bold"""
        return self.enclose(text, self.special_chars['bold'])
    
    def italic(self, text):
        """Formats a text italic"""
        return self.enclose(text, self.special_chars['italic'])
        
    def underline(self, text):
        """Formats a text underline"""
        return self.enclose(text, self.special_chars['underline'])

    def table_row(self, content):
        """Formats a list to a dokuwiki table row"""
        if not content:
            content = ''
        if not isinstance(content, list):
            content = [ content ]
        char = self.special_chars['cell_delimiter']
        return self.enclose((' ' + char + ' ').join(['' if value is None else value for value in content]), char, True)

    def table_header(self, content):
        """Formats a list to a dokuwiki table header row"""
        if not content:
            content = ''
        if not isinstance(content, list):
            content = [ content ]
        char = self.special_chars['hcell_delimiter']
        return self.enclose((' ' + char + ' ').join(['' if value is None else value for value in content]), char, True)
        
    
    @staticmethod
    def enclose(text, wrapper, gap=False):
        """Encloses a text with the wrappertext as pre- and postfix."""
        if not text:
            text = ''
        if not wrapper:
            wrapper = ''
        space = ''
        if gap:
            space = ' '
        return wrapper + space + text + space + wrapper

    @staticmethod
    def escape_for_dokuwiki(text, chars):
        """Escape selected characters in text to prevent auto-formatting in dokuwiki."""
        for char in chars:
            text = text.replace(char, '%%' + char + '%%')
        return text
    
    @staticmethod
    def write_to_file(content, outfile_name):
        """Write content to a file."""
        
        try:
            outfile = open(outfile_name, 'w')
            print(content, file=outfile)
        except (OSError) as ex:
            print('Unable to open', outfile_name, 'to write:', ex)
        outfile.close()
        
        print(outfile_name, "written.")


#!/usr/bin/env python

import sys
import json
import datetime

import clang.cindex



plugin_functions = []


class PluginFunction:
    def __init__(self, fn):
        self.result_type = fn.type.get_result().spelling
        self.pointer_name = 'PFN' + fn.spelling.upper()
        self.comment = fn.raw_comment

        # XXX(pajlada): We might need to return void in case length of ret is 0
        if include_argument_name:
            self.arguments = ', '.join(arg.type.spelling + ' ' + arg.displayname for arg in fn.get_arguments())
        else:
            self.arguments = ', '.join(arg.type.spelling for arg in fn.get_arguments())

        self.function_name = fn.spelling

def traverse(node, level=0):
    # Skip any namespaces
    if node.kind == clang.cindex.CursorKind.NAMESPACE:
        return

    for child in node.get_children():
        traverse(child, level+1)

    if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        if function_prefix in node.displayname:
            # Parse out the relevant data from a clang node to a PluginFunction
            plugin_functions.append(PluginFunction(node))

# TODO: Put this in the "main" function (google xd)

index = clang.cindex.Index.create()

template_file = 'template.h'
output_file = 'generated.h'
config_file = 'config.json'

if len(sys.argv) < 2:
    print('Usage: {} PATH_TO_INPUT_FILE (PATH_TO_TEMPLATE_FILE) (PATH_TO_OUTPUT_FILE) (PATH_TO_CONFIG_FILE)'.format(sys.argv[0]))
    sys.exit(1)

if len(sys.argv) >= 3:
    template_file = sys.argv[2]

    if len(sys.argv) >= 4:
        output_file = sys.argv[3]

        if len(sys.argv) >= 5:
            config_file = sys.argv[4]

# Configurable variables
try:
    config = json.loads(open(config_file).read())
except Exception as e:
    config = {}

procs_variable_name = config.get('procs_variable_name', 'pajladaProcs')
lib_variable_name = config.get('lib_variable_name', 'libPajlada')
dll_error_name = config.get('dll_error_name', 'PajladaResult_DLLError')
function_prefix = config.get('function_prefix', 'Pajlada')
include_argument_name = config.get('include_argument_name', False)
include_generation_timestamp = config.get('include_generation_timestamp', True)
include_dirs = config.get('include_dirs', ['include'])

translation_unit = index.parse(sys.argv[1], args=[''.join('-I' + i for i in include_dirs)], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD+clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

traverse(translation_unit.cursor)

date_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
new_data = ''
if include_generation_timestamp:
    new_data += '// THIS FILE WAS AUTOGENERATED {}\n'.format(date_string)
else:
    new_data += '// THIS FILE WAS AUTOGENERATED\n'
new_data += '// NO MANUAL MODIFICATIONS IN THIS FILE WILL PERSIST NEXT TIME THIS FILE IS GENERATED\n'
new_data += '// TO MAKE CHANGES, MODIFY THE TEMPLATE FILE AND RUN THE GENERATION SCRIPT AGAIN\n\n\n'

with open(template_file, 'r') as fh:
    command = None
    for line in fh:
        if '// >>' in line:
            command = line.split('--')[0].split('>>')[1].lower().strip()
            command_pending = True
        elif '// <<' in line:
            command = None

        if not command:
            new_data += line
            continue

        if not command_pending:
            # Ensure old lines within these autogenerated lines are not re-added
            continue

        # Re-add the old line
        new_data += line

        if command == 'function pointer definitions':
            new_data += '\n'

            for fn in plugin_functions:
                if fn.comment:
                    new_data += fn.comment + '\n'
                new_data += 'typedef {fn.result_type} (*{fn.pointer_name})({fn.arguments});'.format(fn=fn)
                new_data += '\n\n'

        elif command == 'function pointer in struct':
            new_data += '\n'

            for fn in plugin_functions:
                new_data += '    {fn.pointer_name} {fn.function_name};\n\n'.format(fn=fn)

        elif command == 'function pointer loading':
            new_data += '\n'

            for fn in plugin_functions:
                new_data += '    {procs_variable_name}.{fn.function_name} = ({fn.pointer_name})GetProcAddress({lib_variable_name}, "{fn.function_name}");\n'.format(
                        procs_variable_name=procs_variable_name, lib_variable_name=lib_variable_name, fn=fn)
                new_data += '    if ({procs_variable_name}.{fn.function_name} == nullptr) {{ return {dll_error_name}; }}'.format(
                        procs_variable_name=procs_variable_name, dll_error_name=dll_error_name, fn=fn)
                new_data += '\n\n'

        elif command == 'function pointer defines':
            new_data += '\n'

            for fn in plugin_functions:
                new_data += '#define {fn.function_name} {procs_variable_name}.{fn.function_name}\n'.format(
                        procs_variable_name=procs_variable_name, fn=fn)

            new_data += '\n'

        command_pending = False

with open(output_file, 'w+') as fh:
    fh.write(new_data)

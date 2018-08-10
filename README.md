# dynamic-dll

tool for generating boilerplate code to dynamically load a dll file, when only given a source file

## install
it's probably smart to do this in a virtual environment  
tested with clang 6  
`pip install clang`

## usage
`./main.py src/main.cpp (PATH_TO_TEMPLATE_FILE template.h by default) (PATH_TO_OUTPUT_FILE generated.h by default)`

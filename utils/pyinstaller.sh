#!/bin/bash

pyinstaller --onefile -n dynamic-dll --add-data 'libclang.dll;.' main.py

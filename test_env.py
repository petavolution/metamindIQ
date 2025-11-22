#!/usr/bin/env python3
import sys
import importlib as importlib_module
import importlib.metadata

def check_module(name):
    try:
        module = importlib_module.import_module(name)
        version = getattr(module, '__version__', 'unknown')
        if version == 'unknown':
            try:
                version = importlib.metadata.version(name.replace('._', '.').split('.')[0])
            except:
                pass
        print(f"✅ {name}: {version}")
        return True
    except ImportError:
        print(f"❌ {name}: Not installed")
        return False

print(f"Python version: {sys.version}")
print(f"Virtual environment: {sys.prefix}")
print("\nChecking required packages:")

modules = [
    'numpy', 
    'PIL', 
    'pygame', 
    'flask', 
    'flask_cors', 
    'flask_socketio', 
    'eventlet', 
    'dotenv', 
    'pathlib'
]

all_passed = all(check_module(module) for module in modules)

if all_passed:
    print("\n✅ All required packages are installed")
else:
    print("\n❌ Some packages are missing") 
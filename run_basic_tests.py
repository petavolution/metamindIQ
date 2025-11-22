#!/usr/bin/env python3
"""
Basic MVC Module Test Launcher

This script provides a simple menu to launch any of the three basic test modules:
- Symbol Memory
- Morph Matrix
- Expand Vision

Each test module is a standalone pygame implementation that doesn't rely on complex imports.
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("=" * 60)
    print("{:^60}".format("MetaMind IQ Train - Basic Test Launcher"))
    print("=" * 60)
    print("\nThis launcher allows you to run any of the three basic test modules.")
    print("Each module is a standalone implementation with pygame that doesn't")
    print("require complex imports.\n")

def print_menu():
    """Print the menu options."""
    print("-" * 60)
    print("Available modules to test:")
    print("-" * 60)
    print("1. Symbol Memory  - Pattern recognition and working memory test")
    print("2. Morph Matrix   - Pattern manipulation and transformation test")
    print("3. Expand Vision  - Visual exploration and search test")
    print("Q. Quit")
    print("-" * 60)

def get_script_path(choice):
    """Get the path to the selected test script."""
    base_dir = Path(__file__).parent
    
    if choice == "1":
        return base_dir / "basic_symbol_memory_test.py"
    elif choice == "2":
        return base_dir / "basic_morph_matrix_test.py"
    elif choice == "3":
        return base_dir / "basic_expand_vision_test.py"
    else:
        return None

def run_script(script_path):
    """Run the selected test script."""
    if not script_path.exists():
        print(f"Error: Script not found at {script_path}")
        input("\nPress Enter to continue...")
        return
    
    # Make the script executable (Unix-like systems)
    if os.name != 'nt':
        try:
            os.chmod(script_path, 0o755)
        except Exception as e:
            print(f"Warning: Could not make script executable: {e}")
    
    print(f"\nLaunching {script_path.name}...\n")
    
    try:
        # Run the script in the same process
        if os.name == 'nt':
            subprocess.call([sys.executable, script_path])
        else:
            subprocess.call([script_path])
        
        print(f"\n{script_path.name} completed.")
    except Exception as e:
        print(f"Error running script: {e}")
    
    input("\nPress Enter to return to menu...")

def main():
    """Main function to run the menu loop."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("\nEnter your choice: ").strip().upper()
        
        if choice == "Q":
            print("\nExiting... Goodbye!")
            break
        
        if choice in ["1", "2", "3"]:
            script_path = get_script_path(choice)
            run_script(script_path)
        else:
            print("\nInvalid choice. Please select from the menu options.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
        sys.exit(0) 
#
# ForgeX4 COSMOS-Ω - Diagnostic Script
#
# File: check_pycparser_headers.py
#
# Description:
# This script validates the installation of pycparser by locating and
# inspecting the 'fake_libc_include' directory. This is used to debug
# pre-processor errors.
#
import os
import pycparser

def main():
    """Finds, prints, and validates the fake libc path."""
    print("--- Pycparser Header Diagnostic ---")
    try:
        # 1. Get the root path of the installed pycparser library
        pycparser_path = os.path.dirname(pycparser.__file__)
        print(f"Found pycparser installation at: {pycparser_path}")

        # 2. Construct the expected path to the fake headers
        fake_libc_path = os.path.join(pycparser_path, 'utils', 'fake_libc_include')
        print(f"Constructed fake libc path: {fake_libc_path}")

        # 3. Validate the path and its contents
        if not os.path.isdir(fake_libc_path):
            print("\nERROR: The fake libc directory does not exist or is not a directory.")
            print("This indicates a corrupted pycparser installation.")
            print("Recommendation: Run 'pip uninstall pycparser' then 'pip install pycparser --no-cache-dir'")
            return

        print("\nSUCCESS: The fake libc directory exists.")

        # 4. List the contents and check for key files
        contents = os.listdir(fake_libc_path)
        print(f"Directory contents ({len(contents)} files):")
        # Print first 5 files for brevity
        for item in contents[:5]:
            print(f"  - {item}")
        
        print("  ...")

        # 5. Check for the specific headers we need
        if 'stdio.h' in contents and 'string.h' in contents:
            print("\nSUCCESS: 'stdio.h' and 'string.h' were found in the directory.")
            print("--- Diagnostic Complete: The pycparser installation is valid. ---")
        else:
            print("\nERROR: 'stdio.h' or 'string.h' is missing from the fake libc directory.")
            print("This indicates a corrupted pycparser installation.")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
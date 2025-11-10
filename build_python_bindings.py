#!/usr/bin/env python3
"""
Build script for vectro-plus Python bindings.
This helps work around common PyO3 linking issues on macOS.
"""
import os
import sys
import subprocess
import sysconfig
from pathlib import Path


def get_python_info():
    """Get Python version and library information."""
    version = sysconfig.get_python_version()
    config_dir = sysconfig.get_path('stdlib')
    prefix = sysconfig.get_config_var('prefix')
    
    print(f"Python version: {version}")
    print(f"Python prefix: {prefix}")
    print(f"Python config dir: {config_dir}")
    
    # Find Python library
    lib_dir = sysconfig.get_config_var('LIBDIR')
    if not lib_dir:
        lib_dir = os.path.join(prefix, 'lib')
    
    print(f"Python lib dir: {lib_dir}")
    return version, prefix, lib_dir


def build_with_cargo():
    """Build the Rust extension with proper environment."""
    version, prefix, lib_dir = get_python_info()
    
    # Set environment variables for linking
    env = os.environ.copy()
    
    # Try to find Python library
    python_lib_name = f"python{version}"
    
    # Set library path
    if 'LIBRARY_PATH' in env:
        env['LIBRARY_PATH'] = f"{lib_dir}:{env['LIBRARY_PATH']}"
    else:
        env['LIBRARY_PATH'] = lib_dir
        
    # Set dynamic library path for macOS
    if 'DYLD_LIBRARY_PATH' in env:
        env['DYLD_LIBRARY_PATH'] = f"{lib_dir}:{env['DYLD_LIBRARY_PATH']}"
    else:
        env['DYLD_LIBRARY_PATH'] = lib_dir
    
    print(f"Building with library path: {lib_dir}")
    
    # Try building
    try:
        result = subprocess.run([
            'cargo', 'build', '--release', '-p', 'vectro_py'
        ], env=env, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print("Output:", result.stdout)
            return True
        else:
            print("❌ Build failed")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"Error running cargo: {e}")
        return False


def setup_python_package():
    """Setup the Python package using setup.py."""
    try:
        # Change to the project directory
        os.chdir(Path(__file__).parent)
        
        result = subprocess.run([
            sys.executable, 'setup.py', 'build_ext', '--inplace'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python package setup successful!")
            return True
        else:
            print("❌ Python package setup failed")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"Error running setup.py: {e}")
        return False


def main():
    print("🚀 Building vectro-plus Python bindings...")
    
    # First try building with cargo directly
    print("\n📦 Building Rust extension...")
    cargo_success = build_with_cargo()
    
    if not cargo_success:
        print("\n🔄 Trying Python setup.py approach...")
        setup_success = setup_python_package()
        
        if not setup_success:
            print("\n❌ Both build approaches failed.")
            print("This is likely due to PyO3 linking issues on macOS.")
            print("\nPossible solutions:")
            print("1. Install Python via pyenv or conda")
            print("2. Ensure Python development headers are installed")
            print("3. Try setting PYO3_PYTHON environment variable")
            return False
    
    print("\n✅ Build completed successfully!")
    print("You can now import the vectro_py module from Python.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
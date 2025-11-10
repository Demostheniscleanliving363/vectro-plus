#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension


class CargoExtension(Extension):
    def __init__(self, name, cargo_toml_path):
        super().__init__(name, sources=[])
        self.cargo_toml_path = cargo_toml_path


class BuildCargoExt(build_ext):
    def build_extension(self, ext):
        if isinstance(ext, CargoExtension):
            self.build_cargo_extension(ext)
        else:
            super().build_extension(ext)

    def build_cargo_extension(self, ext):
        # Build the Rust extension using Cargo
        cargo_toml_dir = Path(ext.cargo_toml_path).parent
        target_dir = Path(self.build_temp) / "cargo_target"
        
        # Determine the target architecture
        target = None
        if sys.platform == "darwin":
            import platform
            if platform.machine() == "arm64":
                target = "aarch64-apple-darwin"
            else:
                target = "x86_64-apple-darwin"
        elif sys.platform.startswith("linux"):
            target = "x86_64-unknown-linux-gnu"
        elif sys.platform.startswith("win"):
            target = "x86_64-pc-windows-msvc"

        # Build command
        cmd = ["cargo", "build", "--release", "--manifest-path", str(cargo_toml_dir / "Cargo.toml")]
        if target:
            cmd.extend(["--target", target])
        cmd.extend(["--target-dir", str(target_dir)])

        print(f"Building Rust extension with: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cargo_toml_dir)
        
        if result.returncode != 0:
            raise RuntimeError("Cargo build failed")

        # Find the built library
        if target:
            lib_dir = target_dir / target / "release"
        else:
            lib_dir = target_dir / "release"

        # Copy the library to the correct location
        if sys.platform == "darwin":
            lib_name = f"lib{ext.name.split('.')[-1]}.dylib"
        elif sys.platform.startswith("linux"):
            lib_name = f"lib{ext.name.split('.')[-1]}.so"
        elif sys.platform.startswith("win"):
            lib_name = f"{ext.name.split('.')[-1]}.dll"

        lib_path = lib_dir / lib_name
        
        if not lib_path.exists():
            # Try .so extension as well (common for Python extensions)
            lib_name = f"lib{ext.name.split('.')[-1]}.so"
            lib_path = lib_dir / lib_name

        if not lib_path.exists():
            raise RuntimeError(f"Could not find built library at {lib_path}")

        # Determine destination
        dest_dir = Path(self.get_ext_fullpath(ext.name)).parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_name = f"{ext.name.split('.')[-1]}.so"
        if sys.platform == "darwin":
            dest_name = f"{ext.name.split('.')[-1]}.so"
        elif sys.platform.startswith("win"):
            dest_name = f"{ext.name.split('.')[-1]}.pyd"

        dest_path = dest_dir / dest_name
        
        print(f"Copying {lib_path} to {dest_path}")
        import shutil
        shutil.copy2(lib_path, dest_path)


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_version():
    # Read version from Cargo.toml
    cargo_toml_path = Path(__file__).parent / "vectro_py" / "Cargo.toml"
    if cargo_toml_path.exists():
        with open(cargo_toml_path, "r") as f:
            for line in f:
                if line.startswith("version = "):
                    return line.split('"')[1]
    return "1.1.0"


# Check if we have Rust/Cargo available
def check_cargo():
    try:
        result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def main():
    if not check_cargo():
        print("Error: Cargo (Rust build system) not found.")
        print("Please install Rust from https://rustup.rs/")
        sys.exit(1)

    setup(
        name="vectro-plus",
        version=get_version(),
        author="Wesley Scholl",
        author_email="wesley.scholl@example.com",
        description="Python bindings for Vectro+ high-performance vector compression and search",
        long_description=read_file("README.md") if Path("README.md").exists() else "",
        long_description_content_type="text/markdown",
        url="https://github.com/wesleyscholl/vectro-plus",
        packages=find_packages(where="python"),
        package_dir={"": "python"},
        ext_modules=[
            CargoExtension("vectro_plus.vectro_py", "vectro_py/Cargo.toml")
        ],
        cmdclass={
            "build_ext": BuildCargoExt,
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Rust",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: Hardware",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Microsoft :: Windows",
        ],
        keywords=[
            "embeddings",
            "vector-search", 
            "quantization",
            "compression",
            "rust",
            "performance",
            "similarity-search",
            "machine-learning",
        ],
        python_requires=">=3.8",
        install_requires=[
            "numpy>=1.20.0",
        ],
        extras_require={
            "dev": [
                "pytest>=7.0",
                "pytest-cov",
                "black",
                "isort",
                "mypy",
            ],
            "benchmark": [
                "scikit-learn>=1.0",
                "matplotlib>=3.5",
                "pandas>=1.3",
            ],
        },
        zip_safe=False,
        include_package_data=True,
    )


if __name__ == "__main__":
    main()
import os
import subprocess
import sys


def build_app():
    print("Starting build process...")

    # Ensure PyInstaller is available via uv run
    # Create the spec file or just build directly
    build_cmd = [
        "uv",
        "run",
        "pyinstaller",
        "--name",
        "PDFTranslator",
        "--windowed",  # Don't open console window on Windows
        "--noconfirm",  # Overwrite existing build
        "--clean",
        "--add-data",
        f"src{os.pathsep}src",  # Include src folder
        "src/app.py",
    ]

    try:
        print(f"Executing: {' '.join(build_cmd)}")
        subprocess.run(build_cmd, check=True)
        print("Build completed successfully!")
        print("Executables are in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build_app()

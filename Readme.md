# Notes on VS Code

When running or debugging a file using the Run > Start debugging, the root directory is always the project directory, even if the python file is in a subdirectory. Thus you should only use relative paths if they are relative to the project directory.


# Build command

Newest command:

Note: --include-data-dir causes the clean dir to be copied into the MacOS dir in the application package on Mac.

python3 -m nuitka --mode=app \
    --enable-plugin=pyside6 \
    --macos-app-icon=./icon/icon.icns \
    --output-dir=build \
    --include-data-dir=./clean=clean \
    ./qaudio.py

# Creating and building icons

Use the script in make_icon.sh


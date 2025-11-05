#!/bin/bash

# --- Configuration ---
SOURCE_IMAGE="icon.png"   # Your 1024x1024 source PNG
OUTPUT_ICNS="icon.icns"        # Desired output .icns filename
# ---------------------

# Create a temporary folder for the icon set
ICONSET_NAME="temp.iconset"
rm -rf "$ICONSET_NAME" # Ensure a clean start
mkdir "$ICONSET_NAME"

echo "Creating icon set from $SOURCE_IMAGE..."

# Generate all the required sizes using sips
# Standard sizes
sips -z 16 16     "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_16x16.png"
sips -z 32 32     "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_32x32.png"
sips -z 64 64     "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_64x64.png" # 64x64 is often 32x32@2x
sips -z 128 128   "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_128x128.png"
sips -z 256 256   "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_256x256.png"
sips -z 512 512   "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_512x512.png"

# Retina (@2x) sizes
sips -z 32 32     "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_16x16@2x.png"  # 16pt * 2x = 32px
sips -z 64 64     "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_32x32@2x.png"  # 32pt * 2x = 64px
sips -z 256 256   "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_128x128@2x.png" # 128pt * 2x = 256px
sips -z 512 512   "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_256x256@2x.png" # 256pt * 2x = 512px
# THIS IS THE CRITICAL ONE for Retina 512pt icons (1024x1024 actual pixels)
sips -z 1024 1024 "$SOURCE_IMAGE" --out "${ICONSET_NAME}/icon_512x512@2x.png"

# Convert the icon set into an .icns file
echo "Converting to .icns..."
iconutil -c icns "$ICONSET_NAME" -o "$OUTPUT_ICNS"

# Clean up the temporary folder
rm -R "$ICONSET_NAME"

echo "Done. $OUTPUT_ICNS created."
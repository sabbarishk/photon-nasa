#!/bin/bash
# Builds the Lambda Layer zip containing pandas, numpy, and matplotlib.
# Run this on Linux/macOS or in WSL. On Windows, use create_layer.ps1 instead.
set -e

LAYER_DIR="lambda_layer"
ZIP_NAME="photon-layer.zip"

echo "Cleaning up previous build..."
rm -rf "$LAYER_DIR"
rm -f "$ZIP_NAME"

echo "Creating $LAYER_DIR/python/ ..."
mkdir -p "$LAYER_DIR/python"

echo "Installing packages (Linux binaries, Python 3.11)..."
pip install pandas numpy matplotlib \
    -t "$LAYER_DIR/python/" \
    --platform manylinux2014_x86_64 \
    --only-binary=:all: \
    --python-version 3.11

echo "Zipping (python/ at zip root)..."
# Zip from inside lambda_layer/ so the root entry is python/, not lambda_layer/python/
# Lambda requires python/ at the zip root or imports will fail.
cd "$LAYER_DIR"
zip -r "../$ZIP_NAME" python/
cd ..

echo ""
echo "File size:"
ls -lh "$ZIP_NAME"
echo ""
echo "Done. Upload $ZIP_NAME to AWS Lambda Layers."
echo "  aws lambda publish-layer-version \\"
echo "    --layer-name photon-data-science \\"
echo "    --zip-file fileb://$ZIP_NAME \\"
echo "    --compatible-runtimes python3.11 \\"
echo "    --region us-east-1"

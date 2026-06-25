# Builds the Lambda Layer zip containing pandas, numpy, and matplotlib.
# Must use --platform and --only-binary flags so pip downloads Linux binaries.
# Lambda runs on Amazon Linux 2 (x86_64) — Windows binaries will not work.

$LayerDir = "lambda_layer"
$ZipName  = "photon-layer.zip"

Write-Host "Cleaning up previous build..."
if (Test-Path $LayerDir) { Remove-Item -Recurse -Force $LayerDir }
if (Test-Path $ZipName)  { Remove-Item -Force $ZipName }

Write-Host "Creating $LayerDir\python\ ..."
New-Item -ItemType Directory -Force -Path "$LayerDir\python" | Out-Null

Write-Host "Installing packages (Linux binaries, Python 3.11)..."
python -m pip install pandas numpy matplotlib `
    -t "$LayerDir\python" `
    --platform manylinux2014_x86_64 `
    --only-binary=:all: `
    --python-version 3.11

if (-not $?) {
    Write-Error "pip install failed. Check the output above."
    exit 1
}

Write-Host ""
Write-Host "Zipping (structure: python\ at zip root)..."
# Compress-Archive uses old COM zip APIs that fail on AV-locked files.
# ZipFile.CreateFromDirectory uses FileShare.Read and handles it correctly.
# Zipping lambda_layer\ (not lambda_layer\python) so python\ appears at the zip root.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$fullLayerDir = (Resolve-Path $LayerDir).Path
$fullZipPath  = [System.IO.Path]::Combine((Get-Location).Path, $ZipName)
[System.IO.Compression.ZipFile]::CreateFromDirectory($fullLayerDir, $fullZipPath)

$bytes = (Get-Item $ZipName).Length
$mb    = [math]::Round($bytes / 1MB, 1)
Write-Host ""
Write-Host "photon-layer.zip size: $mb MB ($bytes bytes)"
Write-Host ""
Write-Host "Done. Upload $ZipName to AWS Lambda Layers."
Write-Host "  aws lambda publish-layer-version ``"
Write-Host "    --layer-name photon-data-science ``"
Write-Host "    --zip-file fileb://$ZipName ``"
Write-Host "    --compatible-runtimes python3.11 ``"
Write-Host "    --region us-east-1"

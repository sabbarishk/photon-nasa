# Builds the Lambda Layer zip containing pandas, numpy, and matplotlib.
# Lambda requires python/ at the zip root — packages live at python/pandas/, etc.
# Must use --platform and --only-binary flags so pip downloads Linux binaries.
# Lambda runs on Amazon Linux 2 (x86_64) — Windows binaries will not work.

$ZipName = "photon-layer.zip"

Write-Host "Cleaning up previous build..."
Remove-Item -Recurse -Force python -ErrorAction SilentlyContinue
Remove-Item -Force $ZipName -ErrorAction SilentlyContinue

Write-Host "Creating python\ directory..."
New-Item -ItemType Directory -Name python | Out-Null

Write-Host "Installing packages (Linux binaries, Python 3.11)..."
python -m pip install pandas numpy matplotlib `
    -t python `
    --platform manylinux2014_x86_64 `
    --only-binary=:all: `
    --python-version 3.11

if (-not $?) {
    Write-Error "pip install failed. Check the output above."
    exit 1
}

Write-Host ""
Write-Host "Zipping (python\ becomes zip root entry)..."
# Compress-Archive fails on AV-locked files after a fresh pip install.
# ZipFile.CreateFromDirectory uses FileShare.Read and handles it correctly.
# We zip the PARENT of python\ (the cwd) so the zip contains python\...
# but we only want python\ — so we use the overload that accepts includeBaseDirectory.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$pythonDir  = [System.IO.Path]::Combine((Get-Location).Path, "python")
$fullZipPath = [System.IO.Path]::Combine((Get-Location).Path, $ZipName)
# includeBaseDirectory = $true means the zip root entry is "python/" not the contents directly
[System.IO.Compression.ZipFile]::CreateFromDirectory($pythonDir, $fullZipPath, [System.IO.Compression.CompressionLevel]::Optimal, $true)

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

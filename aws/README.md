# AWS infrastructure for Photon

## What is a Lambda Layer?

A Lambda Layer is a zip file containing Python packages that AWS Lambda
attaches to your function's filesystem before it runs. Think of it as a
shared `site-packages/` directory that your function can import from.

Lambda's base Python 3.11 runtime only includes the standard library — no
pandas, no numpy, no matplotlib. The layer is how those packages get in.

**The required zip structure:**

```
photon-layer.zip
└── python/
    ├── pandas/
    ├── numpy/
    ├── matplotlib/
    └── (their dependencies — pillow, pytz, six, etc.)
```

Lambda looks for `python/` at the zip root and mounts it as part of the
Python path. Any other structure and imports will fail silently.

## Why Linux binaries?

Lambda runs on **Amazon Linux 2 (x86_64)**. Packages that contain compiled
C extensions (pandas, numpy, matplotlib all do) must be compiled for that
target OS and CPU architecture. A Windows `.pyd` file will not load on
Amazon Linux.

The pip flags that handle this:

| Flag | What it does |
|------|--------------|
| `--platform manylinux2014_x86_64` | Download wheels built for Amazon Linux 2 |
| `--only-binary=:all:` | Never compile from source — only pre-built wheels |
| `--python-version 3.11` | Fetch wheels for the Lambda Python 3.11 runtime |

These flags let you build a Linux-compatible layer from any OS (Windows,
macOS, Linux) without needing a Linux VM or Docker.

## Build the layer

**Windows (PowerShell):**

```powershell
cd d:\Photon\photon_initial
.\aws\create_layer.ps1
```

**Linux / macOS / WSL:**

```bash
cd /path/to/photon_initial
bash aws/create_layer.sh
```

Both scripts produce `photon-layer.zip` in the repo root. The scripts clean
up any previous `lambda_layer/` directory and zip before rebuilding.

## Upload the layer to AWS

After the script finishes, upload via the AWS CLI:

```bash
aws lambda publish-layer-version \
  --layer-name photon-data-science \
  --zip-file fileb://photon-layer.zip \
  --compatible-runtimes python3.11 \
  --region us-east-1
```

Copy the `LayerVersionArn` from the output — you will attach it to the
`photon-code-executor` function.

## Attach the layer to the Lambda function

```bash
aws lambda update-function-configuration \
  --function-name photon-code-executor \
  --layers <LayerVersionArn from above> \
  --region us-east-1
```

## Files not committed to git

`lambda_layer/` and `photon-layer.zip` are build artifacts. They are listed
in `.gitignore` and should never be committed. The scripts regenerate them
from scratch in minutes.

import base64
import json
import os
import subprocess
import sys


def lambda_handler(event, context):
    code = event.get("code", "")
    job_id = event.get("job_id", "unknown")
    file_content = event.get("file_content")
    file_extension = event.get("file_extension", ".csv")

    if not code:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No code provided"}),
        }

    # Write embedded file content to /tmp so generated code can read it
    if file_content:
        file_bytes = base64.b64decode(file_content)
        file_path = f"/tmp/uploaded_data{file_extension}"
        with open(file_path, "wb") as f:
            f.write(file_bytes)

    # Write the generated code to /tmp
    code_file = f"/tmp/photon_job_{job_id}.py"
    with open(code_file, "w") as f:
        f.write(code)

    # Execute in subprocess with the data science layer on PYTHONPATH
    env = {**os.environ, "PYTHONPATH": "/opt/python", "MPLBACKEND": "Agg"}
    try:
        result = subprocess.run(
            [sys.executable, code_file],
            capture_output=True,
            text=True,
            timeout=25,
            env=env,
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "stdout": "",
                "stderr": "Execution timed out after 25 seconds",
                "exit_code": 1,
                "output_image": None,
            }),
        }
    finally:
        try:
            os.remove(code_file)
        except OSError:
            pass

    # Read and encode the output image if it was produced
    output_image = None
    image_path = "/tmp/output.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            output_image = base64.b64encode(f.read()).decode()
        try:
            os.remove(image_path)
        except OSError:
            pass

    return {
        "statusCode": 200,
        "body": json.dumps({
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "output_image": output_image,
        }),
    }

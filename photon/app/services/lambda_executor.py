import json
import logging
import uuid

import boto3

from app.services import upload_store

log = logging.getLogger(__name__)

_FUNCTION_NAME = "photon-code-executor"
_REGION = "us-east-1"


def execute_via_lambda(code: str, source: str = "") -> dict:
    """Send code to the Lambda sandbox and return the execution result.

    Returns a dict with keys: stdout, stderr, exit_code, output_image (str|None).
    Raises RuntimeError if Lambda cannot be reached (caller maps this to 503).
    """
    client = boto3.client("lambda", region_name=_REGION)
    job_id = str(uuid.uuid4())

    payload: dict = {"code": code, "job_id": job_id}

    # For uploaded files, embed the file content so Lambda can write it to /tmp
    if source.startswith("photon-upload://"):
        upload_id = source.removeprefix("photon-upload://")
        try:
            data = upload_store.get(upload_id)
            payload["file_content"] = data["content"]
            payload["file_extension"] = data["extension"]
        except KeyError:
            log.error("Upload %s not found when building Lambda payload", upload_id)

    response = client.invoke(
        FunctionName=_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    if response.get("FunctionError"):
        raw = json.loads(response["Payload"].read())
        error_msg = raw.get("errorMessage", "Lambda execution error")
        log.error("Lambda FunctionError for job %s: %s", job_id, error_msg)
        return {
            "stdout": "",
            "stderr": error_msg,
            "exit_code": 1,
            "output_image": None,
        }

    result = json.loads(response["Payload"].read())
    return json.loads(result["body"])

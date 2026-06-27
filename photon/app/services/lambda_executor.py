import json
import logging
import uuid

import boto3

log = logging.getLogger(__name__)

_FUNCTION_NAME = "photon-code-executor"
_REGION = "us-east-1"


def execute_via_lambda(code: str) -> dict:
    """Send code to the Lambda sandbox and return the execution result.

    Returns a dict with keys: stdout, stderr, exit_code, output_image (str|None).
    Raises RuntimeError if Lambda cannot be reached (caller maps this to 503).
    """
    client = boto3.client("lambda", region_name=_REGION)
    job_id = str(uuid.uuid4())

    response = client.invoke(
        FunctionName=_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"code": code, "job_id": job_id}),
    )

    if response.get("FunctionError"):
        # Lambda ran but the handler itself raised an unhandled exception
        # (e.g. timeout, OOM, import error in the handler — not in user code).
        payload = json.loads(response["Payload"].read())
        error_msg = payload.get("errorMessage", "Lambda execution error")
        log.error("Lambda FunctionError for job %s: %s", job_id, error_msg)
        return {
            "stdout": "",
            "stderr": error_msg,
            "exit_code": 1,
            "output_image": None,
        }

    result = json.loads(response["Payload"].read())
    return json.loads(result["body"])

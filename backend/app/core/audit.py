"""Structured audit logging."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("audit.log")
file_handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(file_handler)

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(stdout_handler)


def log_event(user_id: str, action: str, resource: str, result: str, ip_address: str = "", user_agent: str = "") -> None:
    """Log an audit event as structured JSON. Never logs passwords, tokens, or card numbers."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "result": result,
        "ip_address": ip_address,
        "user_agent": user_agent,
    }
    audit_logger.info(json.dumps(event))

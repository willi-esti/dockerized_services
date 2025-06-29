from fastapi import APIRouter, HTTPException
from config.logger import force_log_rotation, get_log_status, logger
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/logs")

@router.get("/status")
def get_logs_status() -> Dict[str, Any]:
    """Get current log rotation status and file information."""
    try:
        status = get_log_status()
        if 'error' in status:
            raise HTTPException(status_code=500, detail=status['error'])
        return status
    except Exception as e:
        logger(f"Failed to get log status: {e}", 'ERROR')
        raise HTTPException(status_code=500, detail="Failed to retrieve log status")

@router.post("/rotate")
def rotate_logs_manually() -> Dict[str, str]:
    """Manually trigger log rotation."""
    try:
        result = force_log_rotation()
        logger(f"Manual log rotation triggered: {result}", 'INFO')
        return {"message": result}
    except Exception as e:
        logger(f"Failed to rotate logs manually: {e}", 'ERROR')
        raise HTTPException(status_code=500, detail="Failed to rotate logs")

@router.get("/settings")
def get_log_settings() -> Dict[str, Any]:
    """Get current log settings."""
    import os
    return {
        "log_path": os.getenv('LOG_PATH', '/app/logs'),
        "log_level": os.getenv('LOG_LEVEL', 'INFO'),
        "retention_days": int(os.getenv('LOG_RETENTION_DAYS', '7')),
        "dev_mode": os.getenv('DEV_MODE', 'false').lower() == 'true'
    }

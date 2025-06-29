# Log Rotation Configuration

The logging system now supports daily log rotation with compression. Configure the following environment variables:

## Environment Variables

```bash
# Log settings
LOG_PATH=/app/logs                    # Directory where logs are stored
LOG_LEVEL=INFO                        # Log level: DEBUG, INFO, WARNING, ERROR
LOG_RETENTION_DAYS=7                  # Number of days to keep rotated logs
DEV_MODE=false                        # Enable console output in development

# Example docker-compose.yml environment section:
environment:
  - LOG_PATH=/app/logs
  - LOG_LEVEL=INFO
  - LOG_RETENTION_DAYS=30
  - DEV_MODE=true
```

## Features

### Daily Log Rotation
- Automatically rotates logs daily when the first log entry of a new day is written
- Old logs are moved to `app-YYYY-MM-DD.log` format
- Immediately compressed to `app-YYYY-MM-DD.log.gz` to save disk space

### Automatic Cleanup
- Compressed logs older than `LOG_RETENTION_DAYS` are automatically deleted
- Configurable retention period (default: 7 days)

### Thread Safety
- Log rotation is thread-safe using locks
- Multiple processes can safely write to logs simultaneously

### Error Handling
- Robust error handling prevents log rotation failures from affecting application
- Fallback logging to console if file operations fail

## API Endpoints

### Get Log Status
```bash
GET /api/v1/logs/status
```
Returns current log file sizes, rotation status, and file list.

### Manual Log Rotation
```bash
POST /api/v1/logs/rotate
```
Manually trigger log rotation (useful for maintenance or testing).

### Get Log Settings
```bash
GET /api/v1/logs/settings
```
Returns current log configuration settings.

## File Structure

```
/app/logs/
├── app.log                    # Current log file
├── app-2025-06-28.log.gz     # Compressed rotated log
├── app-2025-06-27.log.gz     # Compressed rotated log
└── app-2025-06-26.log.gz     # Compressed rotated log
```

## Example Usage

```python
from config.logger import logger, force_log_rotation, get_log_status

# Normal logging
logger("Application started", "INFO")
logger("Database connection failed", "ERROR")

# Manual rotation
result = force_log_rotation()
print(result)

# Check status
status = get_log_status()
print(f"Total log size: {status['total_size_mb']} MB")
```

## Benefits

1. **Disk Space Management**: Automatic compression reduces storage requirements
2. **Performance**: Old logs don't slow down current logging operations
3. **Maintenance**: Automatic cleanup prevents disk space issues
4. **Monitoring**: API endpoints for log management and monitoring
5. **Reliability**: Thread-safe operations and error handling

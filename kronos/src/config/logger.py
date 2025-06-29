import os
import gzip
import shutil
from dotenv import load_dotenv
from datetime import datetime, timedelta
import inspect
import glob
import threading

# Color codes for terminal output
class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Load environment variables from .env file in the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Load environment variables from .env file in the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Global lock for thread-safe log rotation
_rotation_lock = threading.Lock()

def rotate_logs(log_path, max_days=7):
    """Rotate logs daily and compress old ones."""
    try:
        with _rotation_lock:
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Find current log file
            current_log = os.path.join(log_path, 'app.log')
            
            if not os.path.exists(current_log):
                return
            
            # Check if log file was modified today
            log_mtime = datetime.fromtimestamp(os.path.getmtime(current_log))
            log_date = log_mtime.strftime('%Y-%m-%d')
            
            # If log is from a previous day, rotate it
            if log_date < current_date:
                # Create rotated log filename
                rotated_log = os.path.join(log_path, f'app-{log_date}.log')
                
                # Move current log to dated version
                if not os.path.exists(rotated_log):
                    shutil.move(current_log, rotated_log)
                    
                    # Compress the rotated log
                    compress_log(rotated_log)
            
            # Clean up old logs (older than max_days)
            cleanup_old_logs(log_path, max_days)
            
    except Exception as e:
        # Fallback logging to avoid infinite recursion
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [logger.py] Log rotation failed: {e}")

def compress_log(log_file):
    """Compress a log file using gzip."""
    try:
        compressed_file = f"{log_file}.gz"
        
        with open(log_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original file after compression
        os.remove(log_file)
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [logger.py] Log compression failed: {e}")

def cleanup_old_logs(log_path, max_days):
    """Remove compressed logs older than max_days."""
    try:
        cutoff_date = datetime.now() - timedelta(days=max_days)
        
        # Find all compressed log files
        pattern = os.path.join(log_path, 'app-*.log.gz')
        old_logs = glob.glob(pattern)
        
        for log_file in old_logs:
            try:
                # Extract date from filename (app-YYYY-MM-DD.log.gz)
                basename = os.path.basename(log_file)
                date_str = basename.split('-', 1)[1].split('.')[0]  # Extract YYYY-MM-DD
                log_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if log_date < cutoff_date:
                    os.remove(log_file)
                    
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                continue
                
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [logger.py] Log cleanup failed: {e}")

def ensure_log_directory(log_path):
    """Ensure log directory exists."""
    try:
        os.makedirs(log_path, exist_ok=True)
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [logger.py] Failed to create log directory: {e}")

def logger(message, level=os.getenv('LOG_LEVEL', 'INFO').upper(), log_file=None):
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    log_path = os.getenv('LOG_PATH', '/app/logs')
    max_log_days = int(os.getenv('LOG_RETENTION_DAYS', '7'))
    
    # Ensure log directory exists
    ensure_log_directory(log_path)
    
    if log_file is None:
        log_file = os.path.join(log_path, 'app.log')
    
    # Perform log rotation check
    rotate_logs(log_path, max_log_days)
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = level.upper()
    
    # Get the caller's filename
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    filename = os.path.basename(caller_frame.f_code.co_filename)
    
    color = {
        'INFO': LogColors.OKCYAN,
        'SUCCESS': LogColors.OKGREEN,
        'WARNING': LogColors.WARNING,
        'ERROR': LogColors.FAIL,
        'DEBUG': LogColors.OKBLUE
    }.get(level, LogColors.ENDC)
    
    log_line = f"[{now}] [{level}] [{filename}] {message}"
    
    # Log to file (thread-safe)
    try:
        with open(log_file, 'a') as f:
            f.write(log_line + '\n')
    except Exception as e:
        # Fallback to console if file logging fails
        print(f"[{now}] [ERROR] [logger.py] Failed to write to log file: {e}")
        print(f"[{now}] [FALLBACK] {log_line}")
    
    # Print to screen if in dev mode
    if dev_mode:
        print(f"{color}{log_line}{LogColors.ENDC}")

def force_log_rotation(log_path=None):
    """Manually trigger log rotation (useful for testing or maintenance)."""
    if log_path is None:
        log_path = os.getenv('LOG_PATH', '/app/logs')
    
    max_log_days = int(os.getenv('LOG_RETENTION_DAYS', '7'))
    
    try:
        with _rotation_lock:
            current_log = os.path.join(log_path, 'app.log')
            
            if os.path.exists(current_log):
                # Force rotation with current timestamp
                current_date = datetime.now().strftime('%Y-%m-%d-%H%M%S')
                rotated_log = os.path.join(log_path, f'app-{current_date}.log')
                
                shutil.move(current_log, rotated_log)
                compress_log(rotated_log)
                
                # Clean up old logs
                cleanup_old_logs(log_path, max_log_days)
                
                return f"Log rotation completed. Rotated to app-{current_date}.log.gz"
            else:
                return "No log file found to rotate"
                
    except Exception as e:
        return f"Log rotation failed: {e}"

def get_log_status(log_path=None):
    """Get current log rotation status and file sizes."""
    if log_path is None:
        log_path = os.getenv('LOG_PATH', '/app/logs')
    
    try:
        status = {
            'log_path': log_path,
            'current_log': None,
            'rotated_logs': [],
            'total_size_mb': 0
        }
        
        # Check current log
        current_log = os.path.join(log_path, 'app.log')
        if os.path.exists(current_log):
            size_mb = os.path.getsize(current_log) / (1024 * 1024)
            status['current_log'] = {
                'file': 'app.log',
                'size_mb': round(size_mb, 2),
                'modified': datetime.fromtimestamp(os.path.getmtime(current_log)).strftime('%Y-%m-%d %H:%M:%S')
            }
            status['total_size_mb'] += size_mb
        
        # Check rotated logs
        pattern = os.path.join(log_path, 'app-*.log.gz')
        rotated_files = glob.glob(pattern)
        
        for log_file in sorted(rotated_files, reverse=True):
            size_mb = os.path.getsize(log_file) / (1024 * 1024)
            status['rotated_logs'].append({
                'file': os.path.basename(log_file),
                'size_mb': round(size_mb, 2),
                'modified': datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
            })
            status['total_size_mb'] += size_mb
        
        status['total_size_mb'] = round(status['total_size_mb'], 2)
        return status
        
    except Exception as e:
        return {'error': f"Failed to get log status: {e}"}
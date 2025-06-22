import os
from dotenv import load_dotenv
from datetime import datetime
import inspect

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

def logger(message, level=os.getenv('LOG_LEVEL', 'INFO').upper(), log_file=None):
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    log_path = os.getenv('LOG_PATH', '/app/logs')
    if log_file is None:
        log_file = os.path.join(log_path, 'app.log')
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
    # Log to file
    with open(log_file, 'a') as f:
        f.write(log_line + '\n')
    # Print to screen if in dev mode
    if dev_mode:
        print(f"{color}{log_line}{LogColors.ENDC}")
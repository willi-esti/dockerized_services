def check_env_vars(required_vars):
    """
    Checks if required environment variables are set and not empty.
    Prints an error message and returns False if any are missing or empty.
    Returns True if all are present and valid.
    """
    import os
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value is None or value.strip() == '' or value.startswith('/') is False:
            missing.append(var)
    if missing:
        print(f"❌ Error: The following environment variables are missing or invalid: {', '.join(missing)}")
        return False
    return True

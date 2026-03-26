# Date Fetching Tool

from datetime import datetime

def fetch_current_datetime():
    """Fetch and return the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    current_datetime = fetch_current_datetime()
    print(f"Current Date and Time: {current_datetime}")

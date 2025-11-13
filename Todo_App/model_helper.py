
from datetime import datetime, timezone, timedelta
import string
import secrets

def utc_now_naive():
    """Return current UTC datetime as naive (SQLite Compatible)"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


alphabet = string.ascii_uppercase + string.digits  # A-Z + 0-9

def generate_unique_short_id(length=6):
    from models import User
    while True:
        short_id = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        if not User.query.filter_by(public_id=short_id).first():
            return short_id
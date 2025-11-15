"""Wait for database tables to be created."""
import sys
import time
from sqlalchemy import create_engine, text
from app.config import settings

def wait_for_tables(max_attempts=30, delay=2):
    """Wait for neighborhoods table to exist."""
    engine = create_engine(settings.database_url)
    
    for attempt in range(max_attempts):
        try:
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'neighborhoods')"
                ))
                exists = result.scalar()
                if exists:
                    print("Tables created successfully!")
                    return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
    
    print("Timeout waiting for tables to be created")
    return False

if __name__ == "__main__":
    success = wait_for_tables()
    sys.exit(0 if success else 1)


import sqlite3
from datetime import datetime
import os

# Database setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
db_path = os.path.join(parent_dir, 'data', 'database.db')

# Database setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
data_dir = os.path.join(parent_dir, 'data')
db_path = os.path.join(data_dir, 'database.db')

# Diagnostic information
print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")
print(f"Data directory: {data_dir}")
print(f"Database path: {db_path}")

# Create the .data directory if it doesn't exist
if not os.path.exists(data_dir):
    try:
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    except Exception as e:
        print(f"Error creating directory {data_dir}: {e}")

# Check if the database file exists and is accessible
if os.path.exists(db_path):
    print(f"Database file exists at {db_path}")
    if os.access(db_path, os.R_OK):
        print("Database file is readable")
    else:
        print("Database file is not readable")
    if os.access(db_path, os.W_OK):
        print("Database file is writable")
    else:
        print("Database file is not writable")
else:
    print(f"Database file does not exist at {db_path}")

# Test file creation in the .data directory
test_file_path = os.path.join(data_dir, 'test.txt')
try:
    with open(test_file_path, 'w') as f:
        f.write('test')
    os.remove(test_file_path)
    print(f"Successfully created and deleted test file in {data_dir}")
except Exception as e:
    print(f"Error creating test file: {e}")

def create_connection():
    """Create a database connection to the SQLite database."""
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def create_table():
    """Create the TOKENS table if it doesn't exist."""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TOKENS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL UNIQUE,
            bot_name TEXT,
            username TEXT,
            status TEXT,
            submission_date TEXT,
            last_dumped_date TEXT
        )
        ''')
        conn.commit()

def add_token(token, bot_name=None, username=None):
    """
    Add a new token to the database.
    
    Args:
    token (str): The token to add.
    bot_name (str, optional): The name of the bot.
    username (str, optional): The username associated with the token.
    
    Returns:
    bool: True if the token was added successfully, False otherwise.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        status = "Online"
        submission_date = datetime.now().strftime('%Y-%m-%d')
        try:
            cursor.execute('''
            INSERT INTO TOKENS (token, bot_name, username, status, submission_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (token, bot_name, username, status, submission_date))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False

def remove_token(token):
    """
    Remove a token from the database.
    
    Args:
    token (str): The token to remove.
    
    Returns:
    bool: True if the token was removed, False if it wasn't found.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TOKENS WHERE token = ?", (token,))
        conn.commit()
        return cursor.rowcount > 0

def token_exists(token):
    """
    Check if a token already exists in the database.
    
    Args:
    token (str): The token to check.
    
    Returns:
    bool: True if the token exists, False otherwise.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE token = ?", (token,))
        count = cursor.fetchone()[0]
    return count > 0

def get_all_tokens():
    """
    Retrieve all tokens from the database.
    
    Returns:
    list: A list of dictionaries containing token information.
    """
    with create_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TOKENS")
        return [dict(row) for row in cursor.fetchall()]

def update_token_status(token, status):
    """
    Update the status of a token.
    
    Args:
    token (str): The token to update.
    status (str): The new status.
    
    Returns:
    bool: True if the token was updated, False if it wasn't found.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE TOKENS SET status = ? WHERE token = ?", (status, token))
        conn.commit()
        return cursor.rowcount > 0

def update_last_dumped_date(token):
    """
    Update the last dumped date of a token.
    
    Args:
    token (str): The token to update.
    
    Returns:
    bool: True if the token was updated, False if it wasn't found.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        last_dumped_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("UPDATE TOKENS SET last_dumped_date = ? WHERE token = ?", (last_dumped_date, token))
        conn.commit()
        return cursor.rowcount > 0

def get_token_count():
    """
    Get the total number of tokens in the database.
    
    Returns:
    int: The number of tokens.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM TOKENS")
        return cursor.fetchone()[0]

def get_token(token):
    """
    Retrieve a single token's information.
    
    Args:
    token (str): The token to retrieve.
    
    Returns:
    dict: The token's information, or None if not found.
    """
    with create_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TOKENS WHERE token = ?", (token,))
        row = cursor.fetchone()
        return dict(row) if row else None

# Initialize the database
create_table()
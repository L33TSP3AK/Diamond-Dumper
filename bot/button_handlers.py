import sqlite3
from main import *  # Import the bot instance from main.py
import datetime
today_date = datetime.date.today().strftime('%Y-%m-%d')


def list_tokens(call):
    """List all tokens in the database."""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT token FROM TOKENS")
        tokens = cursor.fetchall()
        conn.close()

        if tokens:
            token_list = "\n".join([t[0] for t in tokens])
            bot.send_message(call.message.chat.id, f"📃 List of Tokens:\n{token_list}")
        else:
            bot.send_message(call.message.chat.id, "No tokens found in the database.")
    except sqlite3.Error as e:
        bot.send_message(call.message.chat.id, f"Database error: {str(e)}")

def dump_tokens(call):
    """Dump tokens to a file or perform some action."""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT token FROM TOKENS")
        tokens = cursor.fetchall()
        
        # Example: Saving tokens to a text file
        with open('dumped_tokens.txt', 'w') as f:
            for token in tokens:
                f.write(f"{token[0]}\n")
        
        conn.close()
        bot.send_message(call.message.chat.id, "🚚 Tokens have been dumped successfully!")
    except sqlite3.Error as e:
        bot.send_message(call.message.chat.id, f"Database error: {str(e)}")

def bot_auth_check(call):
    """Check if the bot is authorized."""
    is_authorized = True  # Replace with actual check
    if is_authorized:
        bot.send_message(call.message.chat.id, "✅ The bot is authorized.")
    else:
        bot.send_message(call.message.chat.id, "❌ The bot is not authorized.")

def get_chat_history(call):
    """Retrieve and display chat history."""
    chat_history = "Chat history goes here..."  # Replace with actual retrieval logic
    bot.send_message(call.message.chat.id, chat_history)

def save_text_history(call):
    """Save text history."""
    bot.send_message(call.message.chat.id, "💬 Text history has been saved.")

def save_user_info(call):
    """Save user information."""
    bot.send_message(call.message.chat.id, "🔏 User information has been saved.")

def save_media_photo(call):
    """Save photos."""
    bot.send_message(call.message.chat.id, "📸 Photos have been saved.")

# Register callback handlers
def handle_query(call):
    if call.data == 'list_tokens':
        list_tokens(call)
    elif call.data == 'dump_tokens':
        dump_tokens(call)
    elif call.data == 'bot_auth':
        bot_auth_check(call)
    elif call.data == 'get_chat_history':
        get_chat_history(call)
    elif call.data == 'save_text_history':
        save_text_history(call)
    elif call.data == 'save_user_info':
        save_user_info(call)
    elif call.data == 'save_media_photo':
        save_media_photo(call)
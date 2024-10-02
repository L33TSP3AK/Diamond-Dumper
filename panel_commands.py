# panel_commands.py

from PyQt5.QtWidgets import QMessageBox

bot = None  # Placeholder for your bot instance

def set_bot_instance(bot_instance):
        """Execute command from console text response input."""
        
        # Check if bot manager input is filled
        bot_token = self.bot_manager_text_input.toPlainText().strip()
        
        if not bot_token:
            QMessageBox.warning(self, "Error", "Please enter your bot token or ID in the Bot Manager.")
            return
        
        # Set the bot instance (assuming you have a way to initialize it)
        set_bot_instance(bot_token)  # You would typically initialize your bot here

        message = self.console_text_response_input.toPlainText().strip()

        if message and message[-1] == '/':
            self.show_command_menu()  # Show tooltip when '/' is detected
            return
        
        if message.startswith("/"):
            parts = message.split()
            command = parts[0]
            if command == "/grant_user" and len(parts) == 3:
                user_id = parts[1]
                access_level = parts[2]
                response = grant_user(user_id, access_level)  # Call grant_user with parameters
                QMessageBox.information(self, "Command Response", response)  # Show response in a message box
                self.console_text_response_input.clear()  # Clear input after executing command
                self.command_menu_label.hide()  # Hide command menu after command execution
            elif command == "/remove_user" and len(parts) == 2:
                user_id = parts[1]
                response = remove_user(user_id)
                QMessageBox.information(self, "Command Response", response)
                self.console_text_response_input.clear()
                self.command_menu_label.hide()
            elif command == "/list_users":
                response = list_users()
                QMessageBox.information(self, "Command Response", response)
                self.console_text_response_input.clear()
                self.command_menu_label.hide()
            elif command == "/help":
                response = show_help()
                QMessageBox.information(self, "Help", response)
                self.console_text_response_input.clear()
                self.command_menu_label.hide()
            else:
                QMessageBox.warning(self, "Invalid Command", "Please enter a valid command.")
                self.console_text_response_input.clear()  # Clear invalid input

# Example of creating and passing your bot instance (replace with actual initialization)
class Bot:
    def send_message(self, user_id, message):
        print(f"Sending message to {user_id}: {message}")  # Simulate sending a message


def grant_user(user_id, access_level):
    """Function to grant user permissions."""
    # Here you would implement the logic to grant permissions
    # For demonstration, we'll just return a success message
    message = f"User {user_id} granted access level: {access_level}."
    
    # Send a congratulatory message to the user via the bot
    if bot:
        try:
            bot.send_message(user_id, f"Congratulations! You have been granted access level: {access_level}.")
        except Exception as e:
            return f"Failed to send message: {str(e)}"
    
    return message
def remove_user():
    """Function to remove user permissions."""
    return "User permissions removed."

def list_users():
    """Function to list users."""
    # In a real application, this would retrieve user data from a database or other source
    users = ["User1", "User2", "User3"]
    return f"Listing all users:\n" + "\n".join(users)

def show_help():
    """Function to show help information."""
    commands = [
        "/grant_user - Grants user permissions",
        "/remove_user - Removes user permissions",
        "/list_users - Lists all users",
        "/help - Shows this help message"
    ]
    return "\n".join(commands)
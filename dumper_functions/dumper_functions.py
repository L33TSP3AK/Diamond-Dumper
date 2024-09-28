# dumper_functions/dumper_functions.py

import os
from datetime import datetime
import aiofiles
import asyncio

class DumperFunctions:
    def __init__(self, console_text_edit_2, dumping_file_directory_textedit, get_selected_token):
        self.console_text_edit_2 = console_text_edit_2
        self.dumping_file_directory_textedit = dumping_file_directory_textedit
        self.get_selected_token = get_selected_token

    @staticmethod
    def log_to_console(func):
        async def wrapper(self, *args, **kwargs):
            self.console_text_edit_2.append(f"Starting {func.__name__}")
            result = await func(self, *args, **kwargs)
            self.console_text_edit_2.append(f"Finished {func.__name__}")
            return result
        return wrapper

    @log_to_console
    async def dumpMessages(self, messages_by_chat):
        self.create_dump_directory_structure()
        
        for m_chat_id, messages_dict in messages_by_chat.items():
            new_messages = messages_dict['buf']
            try:
                file_path = await self.save_text_history(m_chat_id, new_messages)
                if file_path:
                    self.console_text_edit_2.append(f"Saved to: {file_path}")
                    messages_by_chat[m_chat_id]['history'] += new_messages
                    messages_by_chat[m_chat_id]['buf'] = []
                else:
                    self.console_text_edit_2.append(f"Failed to save messages for chat {m_chat_id}")
            except Exception as e:
                self.console_text_edit_2.append(f"Error processing chat {m_chat_id}: {e}")
        return asyncio.sleep(0)

    async def save_text_history(self, chat_id, messages):
        """Saves messages to a text file."""
        base_path = self.dumping_file_directory_textedit.toPlainText().strip()
        if not base_path:
            self.console_text_edit_2.append("Error: No dump directory specified.")
            return None

        selected_token = self.get_selected_token()
        if not selected_token:
            self.console_text_edit_2.append("Error: No token selected.")
            return None

        current_date = datetime.now().strftime("%Y-%m-%d")
        root_dir = os.path.join(base_path, f"[{current_date}] {selected_token[:10]}")
        text_dir = os.path.join(root_dir, "Text")
        
        os.makedirs(text_dir, exist_ok=True)

        file_name = f"{chat_id}_history.txt"
        file_path = os.path.join(text_dir, file_name)

        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write('\n'.join(messages))
            self.console_text_edit_2.append(f"Text history saved to: {file_path}")
            return file_path
        except Exception as e:
            self.console_text_edit_2.append(f"Error saving text history: {str(e)}")
            return None

    def create_dump_directory_structure(self):
        base_path = self.dumping_file_directory_textedit.toPlainText().strip()
        if not base_path:
            self.console_text_edit_2.append("Error: No dump directory specified.")
            return

        current_date = datetime.now().strftime("%Y-%m-%d")
        token = self.get_selected_token()
        if not token:
            self.console_text_edit_2.append("Error: No token selected.")
            return

        root_dir = os.path.join(base_path, f"[{current_date}] {token[:10]}")

        directories = [
            os.path.join(root_dir, "Videos"),
            os.path.join(root_dir, "Videos", "UserID"),
            os.path.join(root_dir, "Images"),
            os.path.join(root_dir, "Images", "UserID"),
            os.path.join(root_dir, "Images", "All User Profiles"),
            os.path.join(root_dir, "Text"),
            os.path.join(root_dir, "Archives"),
            os.path.join(root_dir, "Data"),
            os.path.join(root_dir, "Statistics"),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        user_content_dir = os.path.join(root_dir, "[UserID] Content Folder")
        os.makedirs(user_content_dir, exist_ok=True)
        
        open(os.path.join(user_content_dir, "DevSig.txt"), 'a').close()
        open(os.path.join(user_content_dir, "Session.json"), 'a').close()

        self.console_text_edit_2.append(f"Directory structure created at: {root_dir}")
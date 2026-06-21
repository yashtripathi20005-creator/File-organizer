"""
File Organizer - GUI Module
Contains the main window class and UI components
"""

import os
import re
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget,
    QFileDialog, QMessageBox, QGroupBox, QComboBox,
    QSpinBox, QCheckBox, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from file_operations import FileOrganizer


class OrganizeThread(QThread):
    """Thread for organizing files to prevent UI freezing"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, folder_path, pattern_type, prefix, suffix, 
                 use_date, date_format, start_number, use_extension):
        super().__init__()
        self.folder_path = folder_path
        self.pattern_type = pattern_type
        self.prefix = prefix
        self.suffix = suffix
        self.use_date = use_date
        self.date_format = date_format
        self.start_number = start_number
        self.use_extension = use_extension
        
    def run(self):
        try:
            organizer = FileOrganizer()
            result = organizer.organize_files(
                folder_path=self.folder_path,
                pattern_type=self.pattern_type,
                prefix=self.prefix,
                suffix=self.suffix,
                use_date=self.use_date,
                date_format=self.date_format,
                start_number=self.start_number,
                use_extension=self.use_extension
            )
            
            if result['success']:
                self.finished.emit(True, f"Successfully organized {result['renamed']} files")
            else:
                self.finished.emit(False, result['error'])
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class PreviewThread(QThread):
    """Thread for previewing file changes"""
    preview_ready = pyqtSignal(list)
    status = pyqtSignal(str)
    
    def __init__(self, folder_path, pattern_type, prefix, suffix,
                 use_date, date_format, start_number, use_extension):
        super().__init__()
        self.folder_path = folder_path
        self.pattern_type = pattern_type
        self.prefix = prefix
        self.suffix = suffix
        self.use_date = use_date
        self.date_format = date_format
        self.start_number = start_number
        self.use_extension = use_extension
        
    def run(self):
        try:
            organizer = FileOrganizer()
            preview_list = organizer.preview_rename(
                folder_path=self.folder_path,
                pattern_type=self.pattern_type,
                prefix=self.prefix,
                suffix=self.suffix,
                use_date=self.use_date,
                date_format=self.date_format,
                start_number=self.start_number,
                use_extension=self.use_extension
            )
            self.preview_ready.emit(preview_list)
        except Exception as e:
            self.status.emit(f"Preview error: {str(e)}")


class FileOrganizerGUI(QMainWindow):
    """Main GUI window for File Organizer"""
    
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.organize_thread = None
        self.preview_thread = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("File Organizer")
        self.setGeometry(100, 100, 800, 700)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ===== Folder Selection =====
        folder_group = QGroupBox("Folder Selection")
        folder_layout = QHBoxLayout()
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        self.folder_label.setMinimumWidth(400)
        
        select_btn = QPushButton("Select Folder")
        select_btn.clicked.connect(self.select_folder)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_files)
        
        folder_layout.addWidget(QLabel("Folder:"))
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(select_btn)
        folder_layout.addWidget(refresh_btn)
        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)
        
        # ===== File List =====
        list_group = QGroupBox("Files in Folder")
        list_layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        list_layout.addWidget(self.file_list)
        
        list_group.setLayout(list_layout)
        main_layout.addWidget(list_group)
        
        # ===== Pattern Options =====
        pattern_group = QGroupBox("Renaming Pattern")
        pattern_layout = QVBoxLayout()
        
        # Pattern type selection
        pattern_type_layout = QHBoxLayout()
        pattern_type_layout.addWidget(QLabel("Pattern Type:"))
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "Custom Pattern",
            "Prefix Only",
            "Suffix Only",
            "Date Only",
            "Number Only",
            "Prefix + Number",
            "Prefix + Date",
            "Number + Suffix",
            "Date + Suffix",
            "Custom + Number",
            "Custom + Date"
        ])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern_ui)
        pattern_type_layout.addWidget(self.pattern_combo)
        pattern_type_layout.addStretch()
        pattern_layout.addLayout(pattern_type_layout)
        
        # Custom pattern fields
        fields_layout = QHBoxLayout()
        
        # Prefix
        prefix_layout = QVBoxLayout()
        prefix_layout.addWidget(QLabel("Prefix:"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("Enter prefix...")
        prefix_layout.addWidget(self.prefix_input)
        fields_layout.addLayout(prefix_layout)
        
        # Suffix
        suffix_layout = QVBoxLayout()
        suffix_layout.addWidget(QLabel("Suffix:"))
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("Enter suffix...")
        suffix_layout.addWidget(self.suffix_input)
        fields_layout.addLayout(suffix_layout)
        
        # Date options
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Date Format:"))
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "%Y%m%d",  # 20241225
            "%Y-%m-%d",  # 2024-12-25
            "%Y_%m_%d",  # 2024_12_25
            "%d%m%Y",  # 25122024
            "%d-%m-%Y",  # 25-12-2024
            "%m%d%Y",  # 12252024
            "%b%d%Y",  # Dec252024
            "%d%b%Y"   # 25Dec2024
        ])
        date_layout.addWidget(self.date_format_combo)
        fields_layout.addLayout(date_layout)
        
        # Number options
        number_layout = QVBoxLayout()
        number_layout.addWidget(QLabel("Start Number:"))
        self.start_number_spin = QSpinBox()
        self.start_number_spin.setRange(1, 9999)
        self.start_number_spin.setValue(1)
        number_layout.addWidget(self.start_number_spin)
        fields_layout.addLayout(number_layout)
        
        pattern_layout.addLayout(fields_layout)
        
        # Additional options
        options_layout = QHBoxLayout()
        self.use_date_check = QCheckBox("Include Date")
        self.use_date_check.setChecked(True)
        options_layout.addWidget(self.use_date_check)
        
        self.use_extension_check = QCheckBox("Keep Original Extension")
        self.use_extension_check.setChecked(True)
        options_layout.addWidget(self.use_extension_check)
        
        options_layout.addStretch()
        pattern_layout.addLayout(options_layout)
        
        pattern_group.setLayout(pattern_layout)
        main_layout.addWidget(pattern_group)
        
        # ===== Action Buttons =====
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview Changes")
        self.preview_btn.clicked.connect(self.preview_changes)
        self.preview_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        action_layout.addWidget(self.preview_btn)
        
        self.organize_btn = QPushButton("Organize Files")
        self.organize_btn.clicked.connect(self.organize_files)
        self.organize_btn.setStyleSheet("background-color: #2196F3; color: white;")
        action_layout.addWidget(self.organize_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_fields)
        action_layout.addWidget(self.reset_btn)
        
        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.clicked.connect(self.clear_file_list)
        action_layout.addWidget(self.clear_btn)
        
        action_group.setLayout(action_layout)
        main_layout.addWidget(action_group)
        
        # ===== Progress Bar =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # ===== Status / Preview Area =====
        status_group = QGroupBox("Status & Preview")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Apply initial state
        self.update_pattern_ui()
        
    def select_folder(self):
        """Open folder selection dialog"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Organize"
        )
        if folder:
            self.folder_path = folder
            self.folder_label.setText(folder)
            self.refresh_files()
            self.status_text.append(f"📁 Selected folder: {folder}")
    
    def refresh_files(self):
        """Refresh the file list"""
        if not self.folder_path:
            QMessageBox.warning(self, "Warning", "Please select a folder first!")
            return
        
        self.file_list.clear()
        try:
            files = [f for f in os.listdir(self.folder_path) 
                    if os.path.isfile(os.path.join(self.folder_path, f))]
            files.sort()
            for file in files:
                self.file_list.addItem(file)
            self.status_text.append(f"✅ Loaded {len(files)} files from folder")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read folder: {str(e)}")
    
    def update_pattern_ui(self):
        """Update UI based on selected pattern type"""
        pattern = self.pattern_combo.currentText()
        
        # Enable/disable fields based on pattern
        has_prefix = any(x in pattern for x in ["Prefix", "Custom"])
        has_suffix = any(x in pattern for x in ["Suffix", "Custom"])
        has_date = any(x in pattern for x in ["Date"])
        has_number = any(x in pattern for x in ["Number"])
        
        self.prefix_input.setEnabled(has_prefix)
        self.suffix_input.setEnabled(has_suffix)
        self.date_format_combo.setEnabled(has_date)
        self.start_number_spin.setEnabled(has_number)
        self.use_date_check.setEnabled(has_date)
    
    def preview_changes(self):
        """Generate and show preview of file changes"""
        if not self.validate_inputs():
            return
        
        self.status_text.append("\n--- PREVIEW ---")
        self.status_text.append("Generating preview...")
        self.preview_btn.setEnabled(False)
        self.organize_btn.setEnabled(False)
        
        # Start preview thread
        self.preview_thread = PreviewThread(
            folder_path=self.folder_path,
            pattern_type=self.pattern_combo.currentText(),
            prefix=self.prefix_input.text(),
            suffix=self.suffix_input.text(),
            use_date=self.use_date_check.isChecked(),
            date_format=self.date_format_combo.currentText(),
            start_number=self.start_number_spin.value(),
            use_extension=self.use_extension_check.isChecked()
        )
        self.preview_thread.preview_ready.connect(self.show_preview)
        self.preview_thread.status.connect(self.status_text.append)
        self.preview_thread.finished.connect(self.on_preview_finished)
        self.preview_thread.start()
    
    def show_preview(self, preview_list):
        """Display the preview results"""
        self.status_text.clear()
        self.status_text.append("📋 PREVIEW OF CHANGES:")
        self.status_text.append("-" * 50)
        
        if not preview_list:
            self.status_text.append("⚠️ No files found to rename")
            return
        
        for old_name, new_name in preview_list:
            self.status_text.append(f"📄 {old_name} → {new_name}")
        
        self.status_text.append("-" * 50)
        self.status_text.append(f"Total: {len(preview_list)} files")
    
    def on_preview_finished(self):
        """Handle preview completion"""
        self.preview_btn.setEnabled(True)
        self.organize_btn.setEnabled(True)
    
    def organize_files(self):
        """Start the file organization process"""
        if not self.validate_inputs():
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self, "Confirm",
            "Are you sure you want to rename these files?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        
        self.status_text.append("\n--- ORGANIZING ---")
        self.preview_btn.setEnabled(False)
        self.organize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Start organization thread
        self.organize_thread = OrganizeThread(
            folder_path=self.folder_path,
            pattern_type=self.pattern_combo.currentText(),
            prefix=self.prefix_input.text(),
            suffix=self.suffix_input.text(),
            use_date=self.use_date_check.isChecked(),
            date_format=self.date_format_combo.currentText(),
            start_number=self.start_number_spin.value(),
            use_extension=self.use_extension_check.isChecked()
        )
        self.organize_thread.status.connect(self.status_text.append)
        self.organize_thread.finished.connect(self.on_organize_finished)
        self.organize_thread.start()
    
    def on_organize_finished(self, success, message):
        """Handle organization completion"""
        self.progress_bar.setVisible(False)
        self.preview_btn.setEnabled(True)
        self.organize_btn.setEnabled(True)
        
        if success:
            self.status_text.append(f"✅ {message}")
            QMessageBox.information(self, "Success", message)
            self.refresh_files()  # Refresh the file list
        else:
            self.status_text.append(f"❌ {message}")
            QMessageBox.critical(self, "Error", message)
    
    def validate_inputs(self):
        """Validate user inputs before proceeding"""
        if not self.folder_path:
            QMessageBox.warning(self, "Warning", "Please select a folder first!")
            return False
        
        if not os.path.exists(self.folder_path):
            QMessageBox.warning(self, "Warning", "Selected folder does not exist!")
            return False
        
        # Check if there are files
        try:
            files = [f for f in os.listdir(self.folder_path) 
                    if os.path.isfile(os.path.join(self.folder_path, f))]
            if not files:
                QMessageBox.warning(self, "Warning", "No files found in the selected folder!")
                return False
        except:
            QMessageBox.warning(self, "Warning", "Cannot read the selected folder!")
            return False
        
        return True
    
    def reset_fields(self):
        """Reset all input fields to default values"""
        self.prefix_input.clear()
        self.suffix_input.clear()
        self.pattern_combo.setCurrentIndex(0)
        self.start_number_spin.setValue(1)
        self.date_format_combo.setCurrentIndex(0)
        self.use_date_check.setChecked(True)
        self.use_extension_check.setChecked(True)
        self.status_text.append("🔄 Fields reset to default values")
    
    def clear_file_list(self):
        """Clear the file list widget"""
        self.file_list.clear()
        self.status_text.append("🗑️ File list cleared")

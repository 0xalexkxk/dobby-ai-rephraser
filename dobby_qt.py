#!/usr/bin/env python3
import sys
import os
import json
import time
import threading
import requests
import pyperclip
import pyautogui
from pynput import keyboard

# Fix DPI awareness for Windows
if sys.platform == "win32":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class GradientLabel(QLabel):
    def __init__(self, text1, text2, color1="#1F1F1F", color2="#4F8CFF", parent=None):
        super().__init__(parent)
        self.text1 = text1
        self.text2 = text2
        self.color1 = QColor(color1)
        self.color2 = QColor(color2)
        self.setMinimumHeight(30)  # Increased back to 30 to prevent text cutoff
        self.setMinimumWidth(280)  # Slightly reduced width
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Font setup - compact size for header
        font = QFont("Inter", 18, QFont.Weight.Bold)  # Further reduced from 20 to 18
        if not QFont("Inter").exactMatch():
            font = QFont("Poppins", 18, QFont.Weight.Bold)
            if not QFont("Poppins").exactMatch():
                font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        
        painter.setFont(font)
        
        # Calculate text metrics
        fm = painter.fontMetrics()
        text1_width = fm.horizontalAdvance(self.text1)
        text2_width = fm.horizontalAdvance(self.text2)
        total_width = text1_width + text2_width
        
        # Force widget to be wide enough
        required_width = total_width + 20  # Extra padding
        if self.width() < required_width:
            self.setFixedWidth(required_width)
            self.updateGeometry()
        
        # Draw first part in solid color
        painter.setPen(self.color1)
        y_pos = (self.height() + fm.ascent() - fm.descent()) // 2  # Better vertical centering
        painter.drawText(0, y_pos, self.text1)
        
        # Create gradient for second part
        gradient = QLinearGradient(text1_width, 0, text1_width + text2_width, 0)
        gradient.setColorAt(0, QColor("#4F8CFF"))
        gradient.setColorAt(1, QColor("#AC61FF"))
        
        # Create brush with gradient
        brush = QBrush(gradient)
        painter.setPen(QPen(brush, 1))
        painter.drawText(text1_width, y_pos, self.text2)

# Check if config exists and has valid API key
config_exists = False
api_key_valid = False

try:
    from config import FIREWORKS_API_KEY, FIREWORKS_URL, MODEL_NAME, WRITING_STYLES, API_SETTINGS
    config_exists = True
    if FIREWORKS_API_KEY and FIREWORKS_API_KEY != "YOUR_API_KEY_HERE" and FIREWORKS_API_KEY != "":
        api_key_valid = True
except ImportError:
    print("Config file not found, will create one...")
    FIREWORKS_API_KEY = ""
    FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
    MODEL_NAME = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    WRITING_STYLES = {}
    API_SETTINGS = {}

class DobbyRephraser(QWidget):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    show_window_signal = pyqtSignal(str)
    
    def __init__(self, app_instance=None):
        super().__init__()
        print("🔍 DobbyRephraser.__init__() started")
        
        self.app_instance = app_instance
        self.original_text = ""
        self.selected_style = "friendly"
        self.is_processing = False
        
        print("🔍 Connecting signals...")
        self.result_ready.connect(self.show_result)
        self.error_occurred.connect(self.show_error)
        self.show_window_signal.connect(self.show_with_text)
        print("🔍 Signals connected")
        
        print("🔍 Starting init_ui()...")
        self.init_ui()
        print("🔍 init_ui() completed")
        
    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # Generous size to fit all components including result card with buttons
        self.setFixedSize(640, 720)  # Уменьшили с 725 до 720 после финальной оптимизации
        
        # Set gradient background and modern scrollbar
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:0.3 #ffffff, stop:0.7 #ffffff, stop:1 #fefbff);
            }
            
            /* Modern scrollbar styling */
            QScrollBar:vertical {
                background: #f5f5f5;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #999999;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background: #f5f5f5;
                height: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 5px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #999999;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
        """)
        
        # Main layout WITHOUT scroll area for more direct control
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4, 2, 4, 2)  # Минимальные отступы
        main_layout.setSpacing(0)  # No spacing between elements
        
        # Card frame with exact styling from React component
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.98),
                    stop:0.4 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(248, 250, 252, 0.98));
                border-radius: 12px;
                border: 1px solid rgba(226, 232, 240, 0.6);
            }
        """)
        
        # Add subtle shadow effect that integrates with the gradient background
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(99, 102, 241, 25))  # Subtle purple shadow
        self.card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)  # No margins at all
        card_layout.setSpacing(0)  # No spacing between card sections
        
        # Header widget - увеличиваем еще больше под новый логотип 70x70
        header_widget = QWidget()
        header_widget.setFixedHeight(70)  # Уменьшили с 75 до 70 чтобы убрать еще больше отступов
        header_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(16, 0, 16, 0)  # Минимальные отступы в header
        
        # Header content - horizontal layout
        header_content = QWidget()
        header_content_layout = QHBoxLayout(header_content)
        header_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header left - logo and title
        header_left = QWidget()
        header_left_layout = QHBoxLayout(header_left)
        header_left_layout.setContentsMargins(0, 0, 0, 0)
        header_left_layout.setSpacing(12)  # Reduced gap between logo and title
        header_left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertically center everything
        
        # Logo without any background - увеличиваем еще больше по просьбе пользователя
        logo_widget = QWidget()
        logo_widget.setFixedSize(70, 70)  # Увеличили с 55x55 до 70x70
        logo_widget.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel()
        try:
            # Try both Windows and Linux paths for the no-background image
            image_paths = [
                "./dobby_logo.png",
                "dobby_logo.png",
                "D:/desktop/dobby_logo.png",
                "/mnt/d/desktop/dobby_logo.png"
            ]
            import os
            pixmap = None
            print("🔍 Searching for Dobby image...")
            for path in image_paths:
                file_exists = os.path.exists(path)
                print(f"📁 Checking: {path} - {'EXISTS' if file_exists else 'NOT FOUND'}")
                
                if file_exists:
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        print(f"✅ Image loaded successfully from: {path}")
                        break
                    else:
                        print(f"❌ File exists but failed to load as image: {path}")
                else:
                    print(f"❌ File does not exist: {path}")
            
            if pixmap and not pixmap.isNull():
                # Since the image already has transparent background, just scale it
                scaled_pixmap = pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                # No need for circular mask since image is already transparent
                logo_label.setPixmap(scaled_pixmap)
                print(f"✅ Dobby transparent image loaded successfully from: {path}")
            else:
                logo_label.setText("🐶")
                logo_label.setStyleSheet("font-size: 50px;")  # Увеличили размер fallback эмодзи под новый логотип
                print("❌ Failed to load image, using emoji")
        except Exception as e:
            logo_label.setText("🐶")
            logo_label.setStyleSheet("font-size: 50px;")  # Увеличили размер fallback эмодзи под новый логотип
            print(f"❌ Image error: {e}")
        
        logo_label.setFixedSize(70, 70)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        logo_layout.addWidget(logo_label)
        header_left_layout.addWidget(logo_widget)
        
        # Title section - compact
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)  # Remove spacing between title and subtitle
        title_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Center vertically
        
        # Create modern title with gradient
        title_label = GradientLabel("Dobby AI ", "Rephraser")
        title_label.setStyleSheet("background: transparent;")
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        subtitle_label = QLabel("Make your text more friendly")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
            color: #6b7280;
            margin-top: 2px;
            background: transparent;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_left_layout.addWidget(title_section)
        
        header_content_layout.addWidget(header_left)
        # Remove addStretch() - it causes vertical expansion
        header_content_layout.addSpacing(20)  # Fixed spacing instead of stretch
        
        # Close button - improved design
        close_btn = QPushButton("×")
        close_btn.setFixedSize(34, 34)  # Уменьшили еще на 5% с 36x36 до 34x34
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #BBBBBB;
                font-size: 23px;
                font-weight: bold;
                border-radius: 17px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: #f0f0f0;
                color: #666666;
            }
        """)
        close_btn.clicked.connect(self.hide)
        header_content_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Add the header content widget to header layout
        header_layout.addWidget(header_content)
        
        # Make header draggable for frameless window
        self.drag_pos = None
        
        def mouse_press_event(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_pos = event.globalPosition().toPoint()
        
        def mouse_move_event(event):
            if self.drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
                self.drag_pos = event.globalPosition().toPoint()
        
        header_widget.mousePressEvent = mouse_press_event
        header_widget.mouseMoveEvent = mouse_move_event
        
        card_layout.addWidget(header_widget)
        
        # Content section - FIXED HEIGHT to prevent layout expansion
        content_widget = QWidget()
        # Recalculated: Original(130) + Styles(185) + Button(48) + Spacing(24) = 387px + margins (убрали еще больше spacing)
        content_widget.setFixedHeight(420)  # Уменьшили с 425 до 420 после агрессивной оптимизации
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 0, 16, 2)  # Минимальные отступы в content
        content_layout.setSpacing(6)  # Уменьшили spacing для компактности
        
        # Original text section - FIXED HEIGHT to prevent expansion
        original_section = QWidget()
        original_section.setFixedHeight(130)  # Увеличили с 125 до 130 чтобы показать нижнюю границу
        original_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        original_layout = QVBoxLayout(original_section)
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_layout.setSpacing(2)  # Еще меньше spacing между label и text field
        
        text_label = QLabel("Original Text")
        text_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: 500; 
            color: #6b7280;
            font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
        """)
        original_layout.addWidget(text_label)
        
        self.text_edit = QTextEdit()
        
        # ULTRA-AGGRESSIVE size control - ABSOLUTELY NEVER change size!
        self.text_edit.setFixedHeight(90)
        self.text_edit.setMinimumHeight(90)
        self.text_edit.setMaximumHeight(90)
        # Also fix width to prevent horizontal changes
        self.text_edit.setMinimumWidth(580)
        self.text_edit.setMaximumWidth(580)
        # Force size policy to absolutely prevent ANY resize whatsoever
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # COMPLETELY disable auto-resize - causes съезды!
        # self.text_edit.textChanged.connect(self.adjust_original_text_height)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 250, 252, 0.8),
                    stop:1 rgba(255, 255, 255, 0.9));
                padding: 8px;
                font-size: 14px;
                font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
                line-height: 1.4;
                color: #1f2937;
                height: 90px;
                min-height: 90px;
                max-height: 90px;
            }
            QTextEdit:focus {
                border: 2px solid #6366f1;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(240, 249, 255, 0.95));
                outline: none;
                padding: 7px;
                height: 90px;
                min-height: 90px;
                max-height: 90px;
            }
        """)
        original_layout.addWidget(self.text_edit)
        content_layout.addWidget(original_section)
        
        # Writing styles section - FIXED HEIGHT to prevent expansion
        styles_section = QWidget()
        styles_section.setFixedHeight(185)  # Fixed height to prevent layout changes
        styles_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Absolutely fixed
        styles_section_layout = QVBoxLayout(styles_section)
        styles_section_layout.setContentsMargins(0, 0, 0, 0)
        styles_section_layout.setSpacing(2)  # Еще меньше spacing для компактности
        
        styles_label = QLabel("Choose Writing Style")
        styles_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: 500; 
            color: #6b7280;
            font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
        """)
        styles_section_layout.addWidget(styles_label)
        
        # Styles grid - размер под кнопки 46px высотой
        styles_widget = QWidget()
        styles_widget.setMinimumHeight(140)  # Увеличили с 130 до 140 под кнопки 46px
        styles_layout = QGridLayout(styles_widget)
        styles_layout.setSpacing(6)  # Еще меньше spacing для более компактного layout
        
        self.style_buttons = {}
        # Exact colors from HTML file
        style_configs = {
            'friendly': {'bg': '#fff7ed', 'color': '#ea580c', 'emoji': '😊'},
            'professional': {'bg': '#f8fafc', 'color': '#6366f1', 'emoji': '💼'},
            'polite': {'bg': '#ecfdf5', 'color': '#15803d', 'emoji': '🙏'},
            'casual': {'bg': '#f3f4f6', 'color': '#7c3aed', 'emoji': '💬'},
            'supportive': {'bg': '#fdf2f8', 'color': '#ec4899', 'emoji': '🤗'},
            'playful': {'bg': '#fdf2f8', 'color': '#ec4899', 'emoji': '🎉'}
        }
        
        row, col = 0, 0
        for style_key, style_data in WRITING_STYLES.items():
            config = style_configs.get(style_key, {'bg': '#f3f4f6', 'color': '#6b7280', 'emoji': '💫'})
            
            # Remove "Human" from the button text and clean up extra emojis
            button_text = style_data['name'].replace(' & Human', '').replace(' Human', '')
            # Remove all emoji characters from button text to avoid duplicates
            import re
            button_text = re.sub(r'[^\w\s]', '', button_text).strip()
            
            # Fix specific button names as requested
            if 'Polite' in button_text and 'Respectful' in button_text:
                button_text = 'Polite'
            elif 'Casual' in button_text and 'Conversational' in button_text:
                button_text = 'Conversational'
            btn = QPushButton(f"{config['emoji']}  {button_text}")  # Only left emoji
            btn.setCheckable(True)
            btn.setMinimumHeight(46)  # Еще больше увеличили высоту кнопок чтобы были заметнее
            btn.setMaximumHeight(46)  # Кнопки заметно выше
            # Improved styling with gradients for better integration
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {config['bg']}, 
                        stop:1 rgba(255, 255, 255, 0.9));
                    color: {config['color']};
                    border: 1px solid rgba(226, 232, 240, 0.6);
                    border-radius: 6px;
                    padding: 12px 16px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{
                    border: 1px solid rgba(99, 102, 241, 0.4);
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {config['bg']}, 
                        stop:1 rgba(240, 249, 255, 0.95));
                }}
                QPushButton:checked {{
                    border: 2px solid #6366f1;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(240, 249, 255, 0.95),
                        stop:1 rgba(255, 255, 255, 1.0));
                }}
            """)
            
            btn.clicked.connect(lambda checked, style=style_key: self.select_style(style))
            self.style_buttons[style_key] = btn
            
            styles_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        styles_section_layout.addWidget(styles_widget)
        content_layout.addWidget(styles_section)
        
        # Add minimal spacing between style buttons and generate button
        content_layout.addSpacing(6)  # Уменьшили с 12 до 6 для компактности
        
        # Generate button - FIXED height and size policy
        self.generate_btn = QPushButton("Generate Text")
        self.generate_btn.setFixedHeight(48)  # height: 48px from HTML
        self.generate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Add custom icon to generate button
        try:
            # Try to load the custom magic icon
            magic_icon_paths = [
                "./button_icon.png",
                "button_icon.png",
                "D:/desktop/button_icon.png",
                "/mnt/d/desktop/button_icon.png"
            ]
            
            magic_pixmap = None
            for path in magic_icon_paths:
                if os.path.exists(path):
                    magic_pixmap = QPixmap(path)
                    if not magic_pixmap.isNull():
                        # Scale to emoji size (16x16)
                        magic_pixmap = magic_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        break
            
            if magic_pixmap and not magic_pixmap.isNull():
                magic_icon = QIcon(magic_pixmap)
                self.generate_btn.setIcon(magic_icon)
                self.generate_btn.setIconSize(QSize(16, 16))
                print("✅ Custom magic icon loaded successfully!")
            else:
                # Fallback: no icon, just text
                print("❌ Custom magic icon not found, using text only")
        except Exception as e:
            print(f"❌ Error loading custom magic icon: {e}")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #2563eb, stop:1 #7c3aed);
            }
            QPushButton:disabled {
                background: #9ca3af;
                opacity: 0.6;
            }
        """)
        self.generate_btn.clicked.connect(self.start_generation)
        content_layout.addWidget(self.generate_btn)
        
        # Убираем spacing после кнопки Generate Text чтобы не было пустого места
        # content_layout.addSpacing(4)  # Убрали чтобы не было лишнего места
        
        # Progress section - compact
        self.progress_section = QWidget()
        self.progress_section.setFixedHeight(50)  # Reduced from 60 to 50
        progress_layout = QVBoxLayout(self.progress_section)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(6)  # Reduced from 8 to 6
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setFixedHeight(8)  # height: 8px from HTML
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e5e7eb;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: #6366f1;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Creating your text...")
        self.progress_label.setStyleSheet("""
            font-size: 12px; 
            color: #6b7280; 
            text-align: center;
            font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
        """)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        self.progress_section.hide()
        content_layout.addWidget(self.progress_section)
        
        # Result card - adaptive height
        self.result_card = QFrame()
        # Fixed height to prevent layout jumping when shown/hidden  
        self.result_card.setFixedHeight(180)  # Уменьшили с 220 до 180 чтобы убрать лишние отступы
        self.result_card.setStyleSheet("""
            QFrame {
                border: 1px solid rgba(99, 102, 241, 0.3);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(240, 249, 255, 0.8), 
                    stop:0.5 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(248, 250, 252, 0.8));
                border-radius: 8px;
            }
        """)
        
        result_layout = QVBoxLayout(self.result_card)
        result_layout.setContentsMargins(12, 6, 12, 6)  # Еще меньше margins чтобы убрать лишние отступы
        result_layout.setSpacing(4)  # Уменьшаем spacing между элементами
        
        # Result header
        result_header_layout = QHBoxLayout()
        result_icon = QLabel("✨")
        result_title = QLabel("Generated Result")
        result_title.setStyleSheet("""
            font-weight: 600; 
            color: #6366f1;
            font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
        """)
        result_header_layout.addWidget(result_icon)
        result_header_layout.addWidget(result_title)
        result_header_layout.addStretch()
        result_layout.addLayout(result_header_layout)
        
        # Result text - FIXED height to prevent layout jumping
        self.result_text = QTextEdit()
        self.result_text.setFixedHeight(80)  # Уменьшили с 100 до 80 чтобы убрать лишние отступы
        # DON'T connect auto-resize - it causes layout jumping
        # self.result_text.textChanged.connect(self.adjust_result_text_height)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
                color: #374151;
                line-height: 1.5;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        # Result buttons
        result_buttons_layout = QHBoxLayout()
        
        self.again_btn = QPushButton("🔄 Again")
        self.again_btn.setStyleSheet("""
            QPushButton {
                background: #f0fdf4;
                color: #059669;
                border: 1px solid #d1fae5;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: #d1fae5;
            }
        """)
        self.again_btn.clicked.connect(self.start_generation)
        
        self.paste_btn = QPushButton("📝 Paste")
        self.paste_btn.setStyleSheet("""
            QPushButton {
                background: #f0fdfa;
                color: #0891b2;
                border: 1px solid #e0f2fe;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', 'Poppins', 'DM Sans', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: #cffafe;
            }
        """)
        self.paste_btn.clicked.connect(self.paste_result)
        
        result_buttons_layout.addWidget(self.again_btn)
        result_buttons_layout.addWidget(self.paste_btn)
        result_layout.addLayout(result_buttons_layout)
        
        # Add content widget to card first
        card_layout.addWidget(content_widget)
        
        # Add result card SEPARATELY to card layout (not inside content_widget!)
        card_layout.addWidget(self.result_card)
        self.result_card.hide()  # Hide initially
        
        # Removed spacer to eliminate excess white space
        
        # DON'T add stretch - it interferes with result card display
        # card_layout.addStretch()  # Removed - prevents result card from showing properly
        
        # Add card directly to main layout - no scroll area
        main_layout.addWidget(self.card)
        
        # DON'T add stretch to main layout - it interferes with proper sizing
        # main_layout.addStretch()  # Removed - prevents proper window sizing
        
        self.setLayout(main_layout)
        
        # Select default style
        self.select_style("friendly")
        
        # Make draggable
        self.drag_pos = None
        
        # Force initial layout update
        self.updateGeometry()
        
        # Ensure all widgets are properly initialized
        QTimer.singleShot(0, self.finalize_ui)
        
    def finalize_ui(self):
        """Final UI setup after all widgets are created"""
        print("🔍 finalize_ui started")
        
        self.text_edit.clear()  # Make sure text edit is empty initially
        print("🔍 Text edit cleared")
        
        self.text_edit.setPlaceholderText("Enter your text here...")  # Add placeholder text
        print("🔍 Placeholder text set")
        
        self.result_card.hide()  # Make sure result card is hidden initially
        self.progress_section.hide()  # Make sure progress section is hidden
        print("🔍 Cards hidden")
        
        # text_edit size is already locked during init - don't touch it!
        print("🔍 text_edit size already locked at 60px - not changing")
        
        # NO layout updates that could cause съезды
        # self.updateGeometry()      # Skip - causes съезды 
        # QApplication.processEvents() # Skip - causes съезды
        
        print("🔍 finalize_ui completed")
        
    def adjust_original_text_height(self):
        """Dynamically adjust Original Text field height based on content"""
        try:
            print("🔍 adjust_original_text_height called")
            
            text = self.text_edit.toPlainText()
            print(f"🔍 Text length: {len(text)}")
            
            # Force document to update its layout
            doc = self.text_edit.document()
            doc.documentLayout().documentSizeChanged.emit(doc.size())
            
            # Force the document to calculate its size with current width
            self.text_edit.document().setTextWidth(self.text_edit.viewport().width())
            
            # Get the actual document height after text wrapping
            doc_height = self.text_edit.document().size().height()
            print(f"🔍 Document height after wrapping: {doc_height}")
            
            # Count actual lines including wrapped lines
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            lines = cursor.blockNumber() + 1
            print(f"🔍 Actual line count (including wraps): {lines}")
            
            # Calculate height based on document size
            if len(text) == 0:
                # For empty text, force exactly 60px
                new_height = 60
            else:
                padding = 40  # Total padding (top + bottom)
                calculated_height = int(doc_height + padding)
                
                # Apply min/max constraints
                min_height = 60   # Minimum for one line + padding  
                max_height = 120  # Reasonable maximum to keep buttons visible
                
                # Set height within bounds
                new_height = max(min_height, min(calculated_height, max_height))
            
            if len(text) == 0:
                print(f"🔍 Calculated new height: {new_height} (empty text = fixed 60px)")
            else:
                print(f"🔍 Calculated new height: {new_height} (doc:{doc_height} + 40 padding)")
            
            current_height = self.text_edit.height()
            print(f"🔍 Current height: {current_height}, New height: {new_height}")
            
            # Simply set the fixed height without conflicting constraints
            print(f"🔍 FORCING height to {new_height}")
            self.text_edit.setFixedHeight(new_height)
            
            # Don't re-apply min/max constraints - they interfere with fixed height
            # Fixed height should be absolute and not overridden by constraints
            
            # Force immediate layout update
            self.updateGeometry()
            self.adjustSize()
            
            # Force parent updates to eliminate spacing
            if self.parent():
                self.parent().updateGeometry()
            
            print(f"🔍 Layout updated, actual height now: {self.text_edit.height()}")
                
        except Exception as e:
            print(f"❌ Error adjusting original text height: {e}")
            import traceback
            traceback.print_exc()
    
    def adjust_result_text_height(self):
        """Dynamically adjust Generated Result field height based on content"""
        try:
            # Get the document height
            doc = self.result_text.document()
            doc_height = doc.size().height()
            
            # Calculate required height (add padding and margins)
            required_height = int(doc_height + 30)  # 30px for padding/margins
            
            # Apply min/max constraints
            min_height = 80   # Minimum for result text
            max_height = 150  # Reduced to ensure buttons stay visible
            
            # Set height within bounds
            new_height = max(min_height, min(required_height, max_height))
            
            # Only update if height actually changed
            if abs(self.result_text.height() - new_height) > 5:
                self.result_text.setFixedHeight(new_height)
                
                # Update the window layout smoothly
                self.updateGeometry()
                
        except Exception as e:
            print(f"Error adjusting result text height: {e}")
        
    def select_style(self, style):
        self.selected_style = style
        for key, btn in self.style_buttons.items():
            btn.setChecked(key == style)
    
    def start_generation(self):
        text = self.text_edit.toPlainText().strip()
        if not text or not self.selected_style:
            QMessageBox.warning(self, "Missing Information", "Please enter text and select a writing style.")
            return
        
        self.original_text = text
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")
        self.result_card.hide()
        self.progress_section.show()  # Show progress section instead of individual elements
        
        # Start API call in thread
        threading.Thread(target=self.call_api, daemon=True).start()
    
    def call_api(self):
        try:
            if not FIREWORKS_API_KEY or len(FIREWORKS_API_KEY) < 10:
                self.error_occurred.emit("Please configure API key in config.py")
                return
            
            style_data = WRITING_STYLES[self.selected_style]
            prompt = style_data['prompt'].format(input_text=self.original_text)
            
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                **API_SETTINGS
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {FIREWORKS_API_KEY}"
            }
            
            response = requests.post(FIREWORKS_URL, 
                                   headers=headers, 
                                   data=json.dumps(payload),
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    generated_text = result['choices'][0]['message']['content'].strip()
                    self.result_ready.emit(generated_text)
                else:
                    self.error_occurred.emit("Invalid API response format")
            else:
                self.error_occurred.emit(f"API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")
    
    def show_result(self, text):
        self.progress_section.hide()  # Hide entire progress section
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Text")  # Icon is preserved automatically
        
        self.result_text.setPlainText(text)
        
        # NO height adjustment - fixed height prevents layout jumping!
        # QTimer.singleShot(100, self.adjust_result_text_height)
        
        self.result_card.show()
    
    def show_error(self, error):
        self.progress_section.hide()  # Hide entire progress section
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Text")  # Icon is preserved automatically
        
        QMessageBox.critical(self, "Error", error)
    
    def paste_result(self):
        text = self.result_text.toPlainText()
        if text:
            # Copy to clipboard
            pyperclip.copy(text)
            self.paste_btn.setText("✅ Pasted!")
            
            # Hide window and auto-paste
            self.hide()
            
            # Auto-paste after small delay
            def do_paste():
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'a')  # Select all
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')  # Paste
            
            import threading
            threading.Thread(target=do_paste, daemon=True).start()
            
            # Reset button text after 2 seconds
            QTimer.singleShot(2000, lambda: self.paste_btn.setText("📝 Paste"))
    
    
    def show_with_text(self, text):
        print(f"🔍 show_with_text called with: '{text[:50]}...'")
        
        # Hide result card and progress section first
        self.result_card.hide()
        self.progress_section.hide()
        print("🔍 Result card and progress hidden")
        
        # Set text without any layout changes
        self.text_edit.setPlainText(text)
        print(f"🔍 Text set: {len(text)} characters")
        
        # *** FORCE FULL LAYOUT CYCLE (ChatGPT совет) ***
        print("🔍 Forcing full layout cycle to fix 'кривость'...")
        
        # 1. Принудительно показать result_card с пустым содержимым чтобы layout рассчитался
        self.result_text.setPlainText("Layout calculation placeholder...")
        self.result_card.show()
        
        # 2. Принудительный полный цикл обновления layout (ключ к решению!)
        self.adjustSize()           # Пересчитать размеры виджета
        self.repaint()              # Принудительная перерисовка
        QApplication.processEvents() # Обработать все события
        
        # 3. Теперь скрыть result_card - layout уже рассчитан правильно!
        self.result_card.hide()
        QApplication.processEvents()
        
        print("🔍 Full layout cycle completed - кривость исправлена!")
        
        self.text_edit.setFocus()  # Give focus to text field
        print("🔍 Focus set to text edit")
        
        # Reset generate button state
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Text")
        
        # Position near cursor
        cursor_pos = QCursor.pos()
        screen = QApplication.primaryScreen().geometry()
        
        print(f"Cursor position: {cursor_pos}")
        print(f"Screen size: {screen}")
        
        # Simple center positioning for actual window size
        x = (screen.width() - 640) // 2
        y = (screen.height() - 720) // 2
        
        print(f"Moving window to: {x}, {y}")
        self.move(x, y)
        
        print("🔍 Calling self.show()...")
        self.show()
        
        # Дополнительный полный цикл обновления ПОСЛЕ показа окна (ChatGPT подход)
        QApplication.processEvents()  # Дать окну показаться
        self.adjustSize()             # Пересчитать после показа
        self.repaint()                # Принудительная перерисовка
        QApplication.processEvents()  # Финальная обработка
        print("🔍 Post-show layout cycle completed")
        print("🔍 Window shown, calling self.raise_()...")
        self.raise_()
        print("🔍 Window raised, calling self.activateWindow()...")
        self.activateWindow()
        print("🔍 Window activated")
        
        # Light update to ensure text is displayed properly
        self.updateGeometry()
        
        # Make sure text is visible
        QTimer.singleShot(100, lambda: self.text_edit.setFocus())
        
        # NO force_layout_compaction - causes съезды even when "safe"
        print("🔍 Skipping force_layout_compaction to prevent any съезды")
        
        print(f"Window visible: {self.isVisible()}")
        print(f"Window position: {self.pos()}")
        print(f"Window size: {self.size()}")
        
        # Force window to front
        self.setWindowState(Qt.WindowState.WindowActive)
        print("Window should be visible now!")
    
    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead of exit"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            # Hide window instead of closing
            event.ignore()
            self.hide()
            
            # Show tray message on first hide
            if not hasattr(self, '_tray_message_shown'):
                self._tray_message_shown = True
                
                # Show tray notification if we have access to the app instance
                if self.app_instance and hasattr(self.app_instance, 'tray_icon'):
                    self.app_instance.tray_icon.showMessage(
                        "Dobby AI Rephraser",
                        "Application minimized to system tray. Right-click the tray icon to exit.",
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
        else:
            # If no system tray, allow normal close
            event.accept()
        
    def force_layout_compaction(self):
        """Force aggressive layout compaction to eliminate spacing issues"""
        try:
            print("🔍 force_layout_compaction called")
            
            # Ensure result card and progress are hidden
            self.result_card.hide()
            self.progress_section.hide()
            
            # DON'T touch text_edit size - it's already locked!
            print("🔍 Skipping text_edit size changes - already locked at 60px")
            
            # NO layout adjustments that could affect text_edit size
            # self.updateGeometry()  # Skip - causes съезды
            # self.adjustSize()      # Skip - causes съезды
            print("🔍 Skipping layout adjustments to prevent съезды")
            
            print("🔍 Aggressive layout compaction completed")
        except Exception as e:
            print(f"❌ Error in layout compaction: {e}")
            import traceback
            traceback.print_exc()
    
    def debug_layout_sizes(self):
        """Debug current layout sizes to find spacing issues"""
        print("\n🔍 === LAYOUT DEBUG ===")
        print(f"Window size: {self.size()}")
        print(f"Card size: {self.card.size()}")
        print(f"Text edit size: {self.text_edit.size()}")
        print(f"Text edit height: {self.text_edit.height()}")
        
        # Find header widget
        header = None
        for child in self.card.children():
            if isinstance(child, QWidget) and child.minimumHeight() == 55:
                header = child
                break
        
        if header:
            print(f"Header size: {header.size()}")
            print(f"Header height: {header.height()}")
        
        print("🔍 === END DEBUG ===\n")

class DobbyApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.window = DobbyRephraser(app_instance=self)
        
        # Set up system tray
        self.setup_system_tray()
        
        # Set up global hotkey listener with pynput
        self.setup_hotkeys()
        
        print("🚀 === DOBBY AI REPHRASER PYQT6 (DEBUG MODE) ===")
        print("🔧 Features:")
        print("  Modern PyQt6 Interface")
        print("  Exact React Component Design")
        print("  Native Dobby Dog Image")
        print("  Powered by Fireworks AI")
        print("")
        print(f"🔌 API: {'Connected' if FIREWORKS_API_KEY and len(FIREWORKS_API_KEY) > 10 else 'Configure in config.py'}")
        print("")
        print("✅ App initialized successfully!")
        print("🎯 Ready! Press F2 when you have text selected...")
        print("🔍 Debug mode enabled - watching for issues...")
    
    def setup_hotkeys(self):
        """Setup global hotkeys using pynput"""
        def on_press(key):
            try:
                # F2 key
                if key == keyboard.Key.f2:
                    self.show_menu_hotkey()
                # ESC key
                elif key == keyboard.Key.esc:
                    self.hide_window()
            except Exception as e:
                print(f"Hotkey error: {e}")
        
        # Start keyboard listener in background thread
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()
    
    def setup_system_tray(self):
        """Setup system tray icon with context menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Try to use the same icon as the app
        try:
            # Try both Windows and Linux paths for the logo
            icon_paths = [
                "./dobby_logo.png",
                "dobby_logo.png", 
                "D:/desktop/dobby_logo.png",
                "/mnt/d/desktop/dobby_logo.png"
            ]
            
            icon_set = False
            for path in icon_paths:
                if os.path.exists(path):
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        # Scale to appropriate tray icon size
                        scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.tray_icon.setIcon(QIcon(scaled_pixmap))
                        icon_set = True
                        break
            
            if not icon_set:
                # Fallback to default icon
                self.tray_icon.setIcon(self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        except Exception as e:
            # Fallback to default icon
            self.tray_icon.setIcon(self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            print(f"❌ Error setting tray icon: {e}")
        
        # Create context menu
        tray_menu = QMenu()
        
        # Show action
        show_action = QAction("Show Dobby AI Rephraser", self.app)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # Exit action  
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        # Set context menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Set tooltip
        self.tray_icon.setToolTip("Dobby AI Rephraser - Press F2 to rephrase selected text")
        
        # Handle tray icon activation (double-click)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        print("✅ System tray icon created successfully!")
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show the main window"""
        if self.window.isVisible():
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()
    
    def quit_application(self):
        """Completely quit the application"""
        print("👋 Exiting Dobby AI Rephraser...")
        self.tray_icon.hide()
        self.app.quit()
        sys.exit(0)
    
    def show_menu_hotkey(self):
        print("🔥 F2 PRESSED! Starting text capture...")
        try:
            # Auto-copy selected text
            print("📋 Sending Ctrl+C...")
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)  # Increased delay
            
            current_text = pyperclip.paste()
            print(f"📋 Clipboard content: '{current_text[:100]}...'")
            print(f"📏 Clipboard length: {len(current_text)}")
            
            if current_text and len(current_text.strip()) > 3:
                import re
                current_text = re.sub(r'[^\x20-\x7E\r\n\t]', '', current_text).strip()
                print(f"🧹 Cleaned text length: {len(current_text)}")
                
                if current_text and any(c.isalnum() for c in current_text):
                    print("✅ Valid text found! Emitting show_window_signal...")
                    self.window.show_window_signal.emit(current_text)
                    print("📡 Signal emitted successfully")
                else:
                    print("❌ No valid alphanumeric text found")
            else:
                print("❌ Text too short or empty")
        except Exception as e:
            print(f"💥 F2 Error: {e}")
            import traceback
            traceback.print_exc()
    
    def hide_window(self):
        self.window.hide()
    
    def run(self):
        sys.exit(self.app.exec())

def create_config_file(api_key):
    """Create config.py with the provided API key"""
    config_content = f'''# Fireworks AI Configuration
FIREWORKS_API_KEY = "{api_key}"
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MODEL_NAME = "accounts/fireworks/models/llama-v3p1-70b-instruct"

# 6 Writing Styles with Enhanced Prompts
WRITING_STYLES = {{
    "friendly": {{
        "name": "🟡 Friendly & Human",
        "emoji": "😊",
        "color": "#FFC107",
        "prompt": """TASK: Rewrite text to sound friendly and warm, but not overly sweet or fake.

STYLE: Naturally friendly and warm - like talking to a nice colleague or friend who is genuinely helpful.

🎯 TARGET: Sound like someone who is:
- Naturally warm and friendly
- Helpful and caring without being fake
- Uses gentle, positive language
- Makes conversation pleasant

✅ CHANGES ALLOWED:
- Friendly words: "nice," "great," "good," "awesome"
- Gentle softeners: "maybe," "perhaps," "could"
- Warm connectors: "and," "also," "plus"
- Simple positive language: "sounds good," "that's great"
- Keep language SIMPLE and FRIENDLY - warm but not overly sweet

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Changing the meaning or facts
❌ Being overly excited or fake cheerful
❌ Adding emojis if there are NONE in the original text
❌ Adding unnecessary sweet phrases like "which sounds lovely" or "that's wonderful"

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is really nice"
❌ WRONG: "It can be exported, which is really nice and will help make your workflow more efficient, if that works for you"

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "So for those that staked, are we getting a 140% bonus"
❌ WRONG: "So for those that staked, are we getting a 140% bonus, which sounds lovely?"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {{input_text}}

REPHRASED VERSION:
    }},
    "professional": {{
        "name": "🔵 Professional & Human",
        "emoji": "💼",
        "color": "#2196F3",
        "prompt": """TASK: Rewrite text in formal business language suitable for corporate communications.

STYLE: Formal, authoritative, business-appropriate - like a senior executive or professional consultant writing to colleagues.

🎯 TARGET: Sound like a business professional who is:
- Clear and precise
- Formal but not cold
- Confident and authoritative
- Using simple, clear business language

✅ CHANGES ALLOWED:
- Use formal language: "we recommend," "please consider," "we propose"
- Simple business terms: "setup," "improvement," "plan," "approach"
- Formal structures: "We suggest that..." "It would be good to..."
- NO contractions: "do not" instead of "don't"
- Keep language SIMPLE and CLEAR - formal but easy to understand, avoid complicated business jargon

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Casual language: "let's," "guys," "cool," "easy peasy"
❌ Emojis or informal expressions
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLE:
INPUT: "It can be exported which is good"
✅ CORRECT: "The data can be exported, which represents a beneficial capability"
❌ WRONG: "The data can be exported, which represents a beneficial capability for enhanced operational efficiency"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {{input_text}}

REPHRASED VERSION:
    }},
    "polite": {{
        "name": "🟣 Polite & Respectful",
        "emoji": "🙏",
        "color": "#9C27B0",
        "prompt": """TASK: Rewrite text with utmost courtesy and respect, as if addressing someone you deeply respect.

STYLE: Highly polite, deferential, respectful - like addressing a respected superior, elder, or esteemed colleague.

🎯 TARGET: Sound like a well-mannered person who is:
- Extremely courteous and considerate
- Humble and respectful
- Thoughtful in word choice
- Never presumptuous or demanding

✅ CHANGES ALLOWED:
- Simple polite phrases: "could you please," "if possible," "maybe you could"
- Respectful language: "kindly," "please," "thank you," "if you would"
- Humble words: "it seems," "maybe," "perhaps"
- Simple politeness: "I would appreciate," "when you can"
- Keep language SIMPLE and POLITE - use easy, respectful words that anyone can understand

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Direct commands or demands
❌ Casual or familiar language
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It is possible to export it, which is quite beneficial"
❌ WRONG: "It is possible to export it, which I think is a positive aspect, kindly allowing flexibility in your workflow"

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "Perhaps for those who have staked, are we receiving a 140% bonus"
❌ WRONG: "Perhaps for those who have staked, could you please clarify if they will receive a 140% bonus"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {{input_text}}

REPHRASED VERSION:
    }},
    "casual": {{
        "name": "🟢 Casual & Conversational",
        "emoji": "💬",
        "color": "#4CAF50",
        "prompt": """TASK: Rewrite text like you're chatting with a close friend or colleague in a relaxed setting.

STYLE: Casual, relaxed, conversational - like talking to someone you're comfortable with in a coffee shop or group chat.

🎯 TARGET: Sound like a real person who is:
- Speaking naturally and conversationally
- Relaxed and informal
- Using everyday language
- Not trying to impress anyone

✅ CHANGES ALLOWED:
- Contractions: "don't," "can't," "we'll," "let's"
- Casual words: "thing," "stuff," "way," "pretty," "kinda"
- Simple language: "check out," "figure out," "come up with"
- Informal connectors: "so," "and," "plus," "anyway"
- Keep language SUPER SIMPLE - use the easiest, most common words possible

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Overly formal language
❌ Business jargon or complex words
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is pretty cool"
❌ WRONG: "It can be exported, which is pretty cool and definitely useful for what you're trying to do"

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "So, for those that staked, are we getting that 140% bonus"
❌ WRONG: "So, for those that staked, are we getting that juicy 140% bonus? Let's figure it out!"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {{input_text}}

REPHRASED VERSION:
    }},
    "supportive": {{
        "name": "🔥 Supportive & Human",
        "emoji": "💪",
        "color": "#FF5722",
        "prompt": """TASK: Rewrite text with genuine encouragement and support, like a caring friend who believes in you.

STYLE: Supportive, encouraging, uplifting - like a trusted friend or mentor who wants to help you succeed.

🎯 TARGET: Sound like someone who is:
- Genuinely caring and encouraging
- Positive but realistic
- Emotionally intelligent
- Naturally supportive without being cheesy

✅ CHANGES ALLOWED:
- Encouraging words: "you've got this," "great idea," "that sounds good"
- Supportive phrases: "happy to help," "no pressure," "take your time"
- Positive simple words: "chance" instead of "problem," "task" instead of "issue"
- Gentle emojis: 💪 🙌 ✨ (ONLY if original text has emojis)
- Keep language SIMPLE and ENCOURAGING - use easy, positive words that motivate

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Over-the-top enthusiasm or fake positivity
❌ Motivational quote language
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLE:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is awesome!"
❌ WRONG: "That it can be exported is a huge win—super convenient and practical. Happy to help you explore more features if you need them! 💪"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {{input_text}}

REPHRASED VERSION:
    }},
    "unhinged": {{
        "name": "🔥 Unhinged & Rude",
        "emoji": "💀",
        "color": "#E91E63",
        "prompt": """TASK: Rewrite text as an absolutely unhinged, rude person with zero filter - aggressive but still understandable.

STYLE: Completely unhinged and rude - like an angry person online who says exactly what they think without caring about anyone's feelings.

🎯 TARGET: Sound like someone who is:
- Absolutely rude and aggressive
- Has zero filter and zero politeness
- Uses simple but harsh language
- Doesn't give a shit about being nice

✅ CHANGES ALLOWED:
- Rude language: "fuck," "shit," "damn," "hell," "wtf," "bullshit"
- Aggressive words: "stupid," "dumb," "crazy," "insane," "wild"
- Direct insults: "what the fuck," "are you kidding me," "this is bullshit"
- Simple anger: "fuck yeah," "damn right," "hell no," "what the hell"
- Chaos emojis: 💀😭🔥💯✨ (ONLY if original text has emojis)
- BE RUDE AS FUCK but use simple words that everyone understands

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Being polite or nice
❌ Adding emojis if there are NONE in the original text
❌ Weird phrases like "that shit slaps" or complicated Gen-Z speak

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is fucking great"
❌ WRONG: "It can be exported, no cap, that shit's a lifesaver, fr fr. You lowkey need that workflow shit, trust me bestie."

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "So for those that staked, are we getting that fucking 140% bonus"
❌ WRONG: "Stakers getting 140% bonus, no cap, that shit slaps"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting"
3. NEVER change who is asking/answering or the direction of questions/statements
4. DO NOT respond TO the text - REPHRASE the text!
5. BE RUDE AS FUCK but STAY FOCUSED on the original meaning and use SIMPLE language

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Unhinged rephrase: "yo what the fuck is up today, dickhead?"
NOT: "fuck off with the small talk, who gives a shit!"

INPUT TEXT TO REPHRASE: {{input_text}}

REPHRASED VERSION (BE ABSOLUTELY RUDE):
    }}
}}

# API Settings
API_SETTINGS = {{
    "max_tokens": 2048,
    "top_p": 1,
    "top_k": 40,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "temperature": 0.8,
}}
'''
    
    # Write the config file
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Config file created successfully!")
    
    # Reload the config
    global FIREWORKS_API_KEY, FIREWORKS_URL, MODEL_NAME, WRITING_STYLES, API_SETTINGS
    FIREWORKS_API_KEY = api_key
    FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
    MODEL_NAME = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    
    # Import the full WRITING_STYLES from the new config
    try:
        from config import WRITING_STYLES, API_SETTINGS
    except:
        pass

def show_api_key_dialog():
    """Show dialog to get API key from user"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    dialog = QDialog()
    dialog.setWindowTitle("Dobby AI Rephraser - Setup")
    dialog.setFixedSize(500, 350)
    dialog.setStyleSheet("""
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #f0f9ff, stop:0.5 #ffffff, stop:1 #faf5ff);
        }
        QLabel {
            color: #1f2937;
            font-size: 14px;
        }
        QLineEdit {
            padding: 10px;
            border: 2px solid #e0e7ff;
            border-radius: 8px;
            font-size: 14px;
            background: white;
        }
        QLineEdit:focus {
            border-color: #6366f1;
        }
        QPushButton {
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton#saveBtn {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6366f1, stop:1 #4f46e5);
            color: white;
            border: none;
        }
        QPushButton#saveBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #7c7ff3, stop:1 #6366f1);
        }
        QPushButton#cancelBtn {
            background: #f3f4f6;
            color: #6b7280;
            border: 1px solid #e5e7eb;
        }
        QPushButton#cancelBtn:hover {
            background: #e5e7eb;
        }
    """)
    
    layout = QVBoxLayout(dialog)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 30)
    
    # Title
    title = QLabel("🔥 Welcome to Dobby AI Rephraser!")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1f2937;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Instructions
    instructions = QLabel("To use this app, you need a Fireworks AI API key.\n\n"
                         "1. Go to https://fireworks.ai/\n"
                         "2. Sign up or login\n"
                         "3. Go to API Keys section\n"
                         "4. Create and copy your API key")
    instructions.setWordWrap(True)
    layout.addWidget(instructions)
    
    # API Key input
    api_label = QLabel("Enter your Fireworks AI API Key:")
    layout.addWidget(api_label)
    
    api_input = QLineEdit()
    api_input.setPlaceholderText("fw_YOUR_API_KEY_HERE")
    layout.addWidget(api_input)
    
    # Buttons
    button_layout = QHBoxLayout()
    button_layout.setSpacing(10)
    
    cancel_btn = QPushButton("Cancel")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_btn)
    
    save_btn = QPushButton("Save & Start")
    save_btn.setObjectName("saveBtn")
    
    def save_api_key():
        api_key = api_input.text().strip()
        if not api_key:
            QMessageBox.warning(dialog, "Error", "Please enter an API key!")
            return
        if not api_key.startswith("fw_"):
            QMessageBox.warning(dialog, "Error", "API key should start with 'fw_'")
            return
        
        create_config_file(api_key)
        dialog.accept()
    
    save_btn.clicked.connect(save_api_key)
    button_layout.addWidget(save_btn)
    
    layout.addLayout(button_layout)
    
    # Show dialog
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted

if __name__ == "__main__":
    # Check if we need to show API key dialog
    if not api_key_valid:
        if not show_api_key_dialog():
            print("❌ API key setup cancelled. Exiting...")
            sys.exit(0)
    
    app = DobbyApp()
    app.run()
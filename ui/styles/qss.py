STYLE_SHEET = """
QMainWindow {
    background-color: #FAFAFA;
}

QWidget#centralWidget {
    background-color: #FAFAFA;
}

QLineEdit#searchInput {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 15px;
    color: #333333;
    selection-background-color: #4A90A4;
}

QLineEdit#searchInput:focus {
    border: 2px solid #4A90A4;
    padding: 11px 15px;
}

QPushButton#searchButton {
    background-color: #4A90A4;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 15px;
    font-weight: 500;
}

QPushButton#searchButton:hover {
    background-color: #3D7A8C;
}

QPushButton#searchButton:pressed {
    background-color: #2E5F6D;
}

QPushButton#searchButton:disabled {
    background-color: #CCCCCC;
}

QPushButton#indexButton {
    background-color: transparent;
    color: #4A90A4;
    border: 1px solid #4A90A4;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
}

QPushButton#indexButton:hover {
    background-color: #F0F7F9;
}

QPushButton#indexButton:pressed {
    background-color: #E0EFF3;
}

QPushButton#indexButton:disabled {
    color: #CCCCCC;
    border-color: #CCCCCC;
}

QLabel#titleLabel {
    color: #333333;
    font-size: 24px;
    font-weight: 600;
}

QLabel#statusLabel {
    color: #888888;
    font-size: 13px;
}

QLabel#hintLabel {
    color: #AAAAAA;
    font-size: 13px;
}

QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #E8E8E8;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #4A90A4;
    border-radius: 4px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QFrame#imageCard {
    background-color: #FFFFFF;
    border: 1px solid #EEEEEE;
    border-radius: 12px;
}

QFrame#imageCard:hover {
    border: 1px solid #4A90A4;
}

QLabel#rankLabel {
    color: #4A90A4;
    font-size: 12px;
    font-weight: 600;
}

QLabel#scoreLabel {
    color: #888888;
    font-size: 11px;
}

QLabel#fileNameLabel {
    color: #555555;
    font-size: 12px;
}
"""
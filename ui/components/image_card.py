from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QCursor

class ImageCard(QFrame):
    """图片结果卡片"""
    
    def __init__(self, rank: int, path: str, name: str, score: float):
        super().__init__()
        self.setObjectName("imageCard")
        self.path = path
        self.setup_ui(rank, name, score)
    
    def setup_ui(self, rank: int, name: str, score: float):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # 图片
        image_label = QLabel()
        image_label.setFixedSize(160, 160)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("background-color: #F5F5F5; border-radius: 8px;")
        
        pixmap = QPixmap(self.path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                180, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled)
        else:
            image_label.setText("无法加载")
        
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 信息栏
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)
        
        rank_label = QLabel(f"#{rank}")
        rank_label.setObjectName("rankLabel")
        
        score_label = QLabel(f"{score:.3f}")
        score_label.setObjectName("scoreLabel")
        
        info_layout.addWidget(rank_label)
        info_layout.addStretch()
        info_layout.addWidget(score_label)
        
        layout.addLayout(info_layout)
        
        # 文件名
        name_label = QLabel(name)
        name_label.setObjectName("fileNameLabel")
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(180)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 截断过长的文件名
        if len(name) > 24:
            name_label.setText(name[:21] + "...")
            name_label.setToolTip(name)
        
        layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def mouseDoubleClickEvent(self, event):
        """双击打开文件所在位置"""
        import subprocess
        subprocess.run(['explorer', '/select,', self.path])
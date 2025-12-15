import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea,
    QProgressBar, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt

from config.settings import (
    API_KEY, IMAGE_DIR, CACHE_FILE, 
)
from api.embedding import EmbeddingAPI
from workers.index_worker import IndexWorker
from workers.search_worker import SearchWorker
from ui.components.image_card import ImageCard
from ui.styles.qss import STYLE_SHEET

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.embeddings = {}
        self.api = None
        self.index_worker = None
        self.search_worker = None
        
        self.setup_ui()
        self.load_cache()
        self.update_status()
    
    def setup_ui(self):
        self.setWindowTitle("图片语义检索")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 800)
        
        # 中央部件
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(48, 36, 48, 36)
        main_layout.setSpacing(24)
        
        # ===== 头部 =====
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        title = QLabel("图片语义检索")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        header_layout.addWidget(self.status_label)
        
        self.index_btn = QPushButton("构建索引")
        self.index_btn.setObjectName("indexButton")
        self.index_btn.clicked.connect(self.start_indexing)
        header_layout.addWidget(self.index_btn)
        
        main_layout.addLayout(header_layout)
        
        # ===== 搜索栏 =====
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("输入描述文字，搜索匹配的图片...")
        self.search_input.returnPressed.connect(self.start_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.setObjectName("searchButton")
        self.search_btn.clicked.connect(self.start_search)
        search_layout.addWidget(self.search_btn)
        
        main_layout.addLayout(search_layout)
        
        # ===== 进度条 =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        main_layout.addWidget(self.progress_bar)
        
        # ===== 结果区域 =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.results_container = QWidget()
        self.results_layout = QGridLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 16, 0, 16)
        self.results_layout.setSpacing(20)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.results_container)
        main_layout.addWidget(scroll, 1)
        
        # 初始化提示标签
        self.show_hint("请先构建索引，然后输入文字进行搜索")
        
        self.setStyleSheet(STYLE_SHEET)
    
    def show_hint(self, text: str):
        """显示提示文本"""
        self.clear_results()
        hint_label = QLabel(text)
        hint_label.setObjectName("hintLabel")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.addWidget(hint_label, 0, 0, 1, 5, Qt.AlignmentFlag.AlignCenter)
    
    def load_cache(self):
        """加载缓存的embeddings"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.embeddings = json.load(f)
            except Exception as e:
                print(f"加载缓存失败: {e}")
                self.embeddings = {}
    
    def save_cache(self):
        """保存embeddings到缓存"""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.embeddings, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def update_status(self):
        """更新状态显示"""
        count = len(self.embeddings)
        if count > 0:
            self.status_label.setText(f"已索引 {count} 张图片")
        else:
            self.status_label.setText("未建立索引")
    
    def check_api_key(self) -> bool:
        """检查API Key是否已配置"""
        if not API_KEY:
            QMessageBox.warning(
                self,
                "配置错误",
                "请在代码中填入你的 API Key\n\n"
                "找到代码顶部的 API_KEY 变量，填入你的密钥。"
            )
            return False
        return True
    
    def start_indexing(self):
        """开始建立索引"""
        if not self.check_api_key():
            return
        
        if not os.path.exists(IMAGE_DIR):
            QMessageBox.warning(
                self,
                "路径错误",
                f"图片目录不存在：\n{IMAGE_DIR}\n\n请检查路径是否正确。"
            )
            return
        
        self.api = EmbeddingAPI(API_KEY)
        
        self.index_btn.setEnabled(False)
        self.search_btn.setEnabled(False)
        self.search_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在构建索引...")
        
        self.index_worker = IndexWorker(self.api, IMAGE_DIR, self.embeddings)
        self.index_worker.progress.connect(self.on_index_progress)
        self.index_worker.finished.connect(self.on_index_finished)
        self.index_worker.error.connect(self.on_index_error)
        self.index_worker.start()
    
    def on_index_progress(self, current: int, total: int, filename: str):
        """索引进度更新"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"正在索引 ({current}/{total})")
    
    def on_index_finished(self, embeddings: dict):
        """索引完成"""
        self.embeddings = embeddings
        self.save_cache()
        
        self.index_btn.setEnabled(True)
        self.search_btn.setEnabled(True)
        self.search_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.update_status()
        self.show_hint("输入描述文字开始搜索")
        
        QMessageBox.information(
            self,
            "索引完成",
            f"已成功索引 {len(self.embeddings)} 张图片"
        )
    
    def on_index_error(self, error: str):
        """索引出错"""
        self.index_btn.setEnabled(True)
        self.search_btn.setEnabled(True)
        self.search_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.update_status()
        
        QMessageBox.critical(self, "索引错误", error)
    
    def start_search(self):
        """开始搜索"""
        query = self.search_input.text().strip()
        
        if not query:
            return
        
        if not self.embeddings:
            QMessageBox.warning(
                self,
                "提示",
                "请先构建图片索引"
            )
            return
        
        if not self.check_api_key():
            return
        
        self.api = EmbeddingAPI(API_KEY)
        
        self.search_btn.setEnabled(False)
        self.index_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # 不确定进度
        self.status_label.setText("正在搜索...")
        
        # 清空结果并显示搜索中提示
        self.show_hint("正在搜索...")
        
        self.search_worker = SearchWorker(self.api, query, self.embeddings)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.start()
    
    def clear_results(self):
        """清空搜索结果"""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
    
    def on_search_finished(self, results: list):
        """搜索完成"""
        self.search_btn.setEnabled(True)
        self.index_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.update_status()
        
        # 先清空结果
        self.clear_results()
        
        if not results:
            self.show_hint("未找到匹配的图片")
            return
        
        # 显示结果（每行5个）
        for i, result in enumerate(results):
            row = i // 5
            col = i % 5
            
            card = ImageCard(
                rank=i + 1,
                path=result["path"],
                name=result["name"],
                score=result["score"]
            )
            
            self.results_layout.addWidget(card, row, col)
    
    def on_search_error(self, error: str):
        """搜索出错"""
        self.search_btn.setEnabled(True)
        self.index_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.update_status()
        
        self.show_hint("搜索出错，请重试")
        QMessageBox.critical(self, "搜索错误", error)
    
    def closeEvent(self, event):
        """关闭窗口时清理"""
        if self.index_worker and self.index_worker.isRunning():
            self.index_worker.cancel()
            self.index_worker.wait()
        
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.wait()
        
        event.accept()
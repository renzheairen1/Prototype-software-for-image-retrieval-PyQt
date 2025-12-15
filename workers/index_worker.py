from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import hashlib

from api.embedding import EmbeddingAPI
from config.settings import SUPPORTED_FORMATS
class IndexWorker(QThread):
    """图片索引工作线程"""
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, api: EmbeddingAPI, image_dir: str, existing_cache: dict):
        super().__init__()
        self.api = api
        self.image_dir = image_dir
        self.existing_cache = existing_cache
        self._is_cancelled = False
    
    def cancel(self):
        self._is_cancelled = True
    
    def run(self):
        try:
            image_files = []
            for ext in SUPPORTED_FORMATS:
                image_files.extend(Path(self.image_dir).glob(f"*{ext}"))
                image_files.extend(Path(self.image_dir).glob(f"*{ext.upper()}"))
            
            image_files = list(set(image_files))
            total = len(image_files)
            
            if total == 0:
                self.error.emit("未找到任何图片文件")
                return
            
            embeddings = dict(self.existing_cache)
            
            for i, img_path in enumerate(image_files):
                if self._is_cancelled:
                    break
                
                img_str = str(img_path)
                file_hash = self._get_file_hash(img_str)
                
                # 检查缓存
                if img_str in embeddings:
                    cached = embeddings[img_str]
                    if cached.get("hash") == file_hash:
                        self.progress.emit(i + 1, total, img_path.name)
                        continue
                
                # 获取新的embedding
                embedding = self.api.get_image_embedding(img_str)
                
                if embedding:
                    embeddings[img_str] = {
                        "embedding": embedding,
                        "hash": file_hash,
                        "name": img_path.name
                    }
                
                self.progress.emit(i + 1, total, img_path.name)
            
            self.finished.emit(embeddings)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _get_file_hash(self, filepath: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
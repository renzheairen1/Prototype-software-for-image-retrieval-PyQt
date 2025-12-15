import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path

from api.embedding import EmbeddingAPI

class SearchWorker(QThread):
    """搜索工作线程"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, api: EmbeddingAPI, query: str, embeddings: dict):
        super().__init__()
        self.api = api
        self.query = query
        self.embeddings = embeddings
    
    def run(self):
        try:
            # 获取查询文本的embedding
            query_embedding = self.api.get_text_embedding(self.query)
            
            if query_embedding is None:
                self.error.emit("无法获取文本向量，请检查API配置")
                return
            
            query_vec = np.array(query_embedding)
            
            # 计算相似度
            results = []
            for path, data in self.embeddings.items():
                if "embedding" in data:
                    img_vec = np.array(data["embedding"])
                    similarity = self._cosine_similarity(query_vec, img_vec)
                    results.append({
                        "path": path,
                        "name": data.get("name", Path(path).name),
                        "score": similarity
                    })
            
            # 按相似度排序，取前10
            results.sort(key=lambda x: x["score"], reverse=True)
            self.finished.emit(results[:10])
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
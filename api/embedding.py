import base64
import requests
from pathlib import Path
from typing import Optional

from config.settings import API_URL, MODEL_NAME

class EmbeddingAPI:
    """阿里云百炼 Embedding API 封装"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_text_embedding(self, text: str) -> Optional[list]:
        """获取文本的embedding向量"""
        payload = {
            "model": MODEL_NAME,
            "input": {
                "contents": [
                    {"text": text}
                ]
            }
        }
        
        try:
            response = requests.post(
                API_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "embeddings" in result["output"]:
                return result["output"]["embeddings"][0]["embedding"]
            return None
        except Exception as e:
            print(f"文本Embedding错误: {e}")
            return None
    
    def get_image_embedding(self, image_path: str) -> Optional[list]:
        """获取图片的embedding向量"""
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            
            # 获取图片格式
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            payload = {
                "model": MODEL_NAME,
                "input": {
                    "contents": [
                        {"image": f"data:{mime_type};base64,{image_data}"}
                    ]
                }
            }
            
            response = requests.post(
                API_URL,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "embeddings" in result["output"]:
                return result["output"]["embeddings"][0]["embedding"]
            return None
        except Exception as e:
            print(f"图片Embedding错误 {image_path}: {e}")
            return None
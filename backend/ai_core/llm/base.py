
from abc import ABC, abstractmethod

class LLM(ABC):
    @abstractmethod
    def generate_response(self, dialogue, session_id):
        """生成响应"""
        raise NotImplementedError()
import requests
import json
import time
from typing import List, Dict, Any, Optional
from config.settings import settings


class OllamaClient:
    """
    Ollama客户端封装类，用于与本地Ollama服务通信
    """
    
    _instance: Optional['OllamaClient'] = None
    
    def __new__(cls) -> 'OllamaClient':
        if cls._instance is None:
            cls._instance = super(OllamaClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 初始化Ollama客户端配置
        self.base_url = getattr(settings, 'ollama_base_url', 'http://localhost:11434')
        self.default_model = getattr(settings, 'ollama_default_model', 'emotion_lora')
        self.timeout = getattr(settings, 'ollama_timeout', 60)
        self._initialized = True
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送HTTP请求到Ollama API
        
        Args:
            endpoint: API端点
            method: HTTP方法
            data: 请求数据
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API请求失败: {str(e)}")
    
    def check_service(self) -> bool:
        """
        检查Ollama服务是否运行
        
        Returns:
            服务是否可用
        """
        try:
            response = self._make_request('/api/tags')
            return 'models' in response
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """
        获取可用的模型列表
        
        Returns:
            模型名称列表
        """
        try:
            response = self._make_request('/api/tags')
            models = response.get('models', [])
            return [model.get('name', '') for model in models]
        except Exception as e:
            return []
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        调用Ollama聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            stream: 是否流式输出
            
        Returns:
            模型回复内容
        """
        if model is None:
            model = self.default_model
            
        # 构建prompt - 使用简单的对话格式
        prompt = ""
        system_message = None
        user_messages = []

        for message in messages:
            if message.get('role') == 'system':
                system_message = message.get('content', '')
            elif message.get('role') == 'user':
                user_messages.append(message.get('content', ''))
            elif message.get('role') == 'assistant':
                user_messages.append(message.get('content', ''))

        # 使用简单的对话格式
        if system_message:
            prompt += f"System: {system_message}\n\n"

        for i, content in enumerate(user_messages):
            if i % 2 == 0:  # 用户消息
                prompt += f"User: {content}\n\nAssistant: "
            else:  # 助手消息
                prompt += f"{content}\n\n"
        
        # 构建请求数据
        data = {
            'model': model,
            'prompt': prompt,
            'stream': stream,
            'options': {
                'temperature': temperature
            }
        }
        
        if max_tokens:
            data['options']['num_predict'] = max_tokens
        
        try:
            if stream:
                return self._stream_chat_completion(data)
            else:
                response = self._make_request('/api/generate', method='POST', data=data)
                return response.get('response', '')
        except Exception as e:
            return f"调用Ollama API时出错: {str(e)}"
    
    def _stream_chat_completion(self, data: Dict[str, Any]) -> str:
        """
        流式聊天补全
        """
        url = f"{self.base_url}/api/generate"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=data, headers=headers, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            full_response += chunk['response']
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            return full_response
        except Exception as e:
            return f"流式调用Ollama API时出错: {str(e)}"
    
    def generate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        简单的文本生成接口
        
        Args:
            prompt: 输入提示
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            生成的内容
        """
        messages = [{'role': 'user', 'content': prompt}]
        return self.chat_completion(messages, model, temperature, max_tokens)
    
    def create_model(self, model_name: str, modelfile_path: str) -> bool:
        """
        创建新模型
        
        Args:
            model_name: 模型名称
            modelfile_path: Modelfile路径
            
        Returns:
            是否创建成功
        """
        try:
            # 读取Modelfile
            with open(modelfile_path, 'r', encoding='utf-8') as f:
                modelfile_content = f.read()
            
            # 创建模型
            data = {
                'name': model_name,
                'modelfile': modelfile_content
            }
            
            response = self._make_request('/api/create', method='POST', data=data)
            return 'status' in response
        except Exception as e:
            print(f"创建模型失败: {str(e)}")
            return False
    
    def pull_model(self, model_name: str) -> bool:
        """
        拉取模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            是否拉取成功
        """
        try:
            data = {'name': model_name}
            response = self._make_request('/api/pull', method='POST', data=data)
            return 'status' in response
        except Exception as e:
            print(f"拉取模型失败: {str(e)}")
            return False
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息
        """
        try:
            data = {'name': model_name}
            return self._make_request('/api/show', method='POST', data=data)
        except Exception as e:
            return {'error': str(e)}


# 全局Ollama客户端实例
ollama_client = OllamaClient()
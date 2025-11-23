from openai import OpenAI

from ai_core.llm.base import LLM

class LLMModule(LLM):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key") 
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
    def generate_response(self, dialogue, session_id):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                stream=True
            )
            
            # 迭代输出dai
            for chunk in response:
                if chunk.choices:
                    chunk_content = chunk.choices[0].delta.content
                    yield chunk_content # 返回的是一个生成器，一个一个返回 
            
        except Exception as e:
            print(e)         
    
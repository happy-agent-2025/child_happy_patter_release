from utils.logger import Logger
from utils.util import Util

TAG = __name__
class Dialogue:
    
    def __init__(self):
        config = Util.get_config()
        self.logger = Logger().log_init(TAG)    
        prompt = config["prompt"]
        self.dialogue = [
            {"role": "system", "content": prompt},
        ]
    
    # 用户提问保存到对话列表
    def put_user(self, text):
        self.dialogue.append({"role": "user", "content": text})
    
    # 获取AI的回答保存到对话列表 
    def put_assistant(self, text):
        self.dialogue.append({"role": "assistant", "content": text})
    
    # 获取对话列表
    def get_dialogue(self) -> list:      
        return self.dialogue
            
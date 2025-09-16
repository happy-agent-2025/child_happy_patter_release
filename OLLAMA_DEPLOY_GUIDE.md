# Happy Partner Ollama本地模型部署指南

## 概述

本指南说明如何在本地部署微调后的emotion_final模型，并将其集成到Happy Partner系统中作为教育和情感代理，充分发挥硬件性能，将API调用从云服务切换到本地模型。

## 为什么选择Linux + AMD组合？

### 🎮 AMD锐龙AI MAX+395优势
- **Ryzen AI引擎**: 内置专用AI加速硬件
- **多核性能**: 16核心32线程，适合并行推理
- **ROCm支持**: AMD开源计算平台，GPU加速
- **能效比**: 7nm工艺，低功耗高性能

### 🐧 Linux系统优势
- **原生支持**: Ollama官方推荐Linux环境
- **性能优化**: 更低的系统开销，更好的硬件调度
- **工具链**: 完善的AI开发和部署工具
- **稳定性**: 长时间运行稳定可靠

## 部署步骤

### 1. 系统准备

#### 推荐Linux发行版
- **Ubuntu 22.04 LTS** (首选推荐)
- **Fedora 39** (次选)
- **Arch Linux** (高级用户)

#### 系统要求
- CPU: AMD锐龙AI MAX+395
- 内存: 16GB以上 (推荐32GB)
- 存储: 50GB以上可用空间
- 网络: 稳定的互联网连接 (初始模型下载)

#### 系统优化
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl wget git python3 python3-pip python3-venv htop

# 创建项目用户 (可选)
sudo useradd -m -s /bin/bash happy
sudo usermod -aG sudo happy
```

### 2. 安装Ollama

#### 官方安装
```bash
# 下载并安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 验证安装
ollama --version

# 启动服务
sudo systemctl start ollama
sudo systemctl enable ollama
```

#### 性能优化
```bash
# 运行AMD性能优化脚本
sudo chmod +x scripts/optimize_amd_performance.sh
sudo ./scripts/optimize_amd_performance.sh

# 重启系统以应用优化
sudo reboot
```

### 3. 部署emotion_final模型

#### 3.1 准备emotion_final模型
```bash
# 检查模型文件是否存在
ls -la /home/datawhale/Projects/emotion_final/

# 如果有GGUF文件，直接使用
# 如果没有，需要先转换模型格式
```

#### 3.2 创建emotion_final模型
```bash
# 进入模型目录
cd /home/datawhale/Projects/emotion_final

# 创建Modelfile
cat > Modelfile << 'EOF'
FROM ./emotion_final_q4_k_m.gguf
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 2048
PARAMETER num_predict 512
PARAMETER num_thread 16
PARAMETER num_batch 512
PARAMETER f16_kv true
PARAMETER use_mmap true
PARAMETER mlock true
EOF

# 创建Ollama模型
ollama create emotion_final -f Modelfile
```

#### 3.3 验证模型部署
```bash
# 查看已安装的模型
ollama list

# 测试模型运行
ollama run emotion_final "你好，我感到很难过"

# 测试教育功能
ollama run emotion_final "1+1等于多少？"

# 检查模型信息
ollama show emotion_final
```

#### 3.4 可选：安装ROCm支持GPU加速
```bash
# 安装ROCm (Ubuntu 22.04)
sudo apt install -y wget
wget https://repo.radeon.com/amdgpu-install/6.0.2/ubuntu/jammy/amdgpu-install_6.0.2.60002-1_all.deb
sudo apt install -y ./amdgpu-install_6.0.2.60002-1_all.deb
sudo amdgpu-install --usecase=rocm,hip,mllib --no-dkms

# 验证ROCm安装
rocm-smi

# 重启Ollama服务以应用GPU支持
sudo systemctl restart ollama
```

### 4. 配置Happy Partner系统

#### 4.1 项目部署
```bash
# 克隆项目 (如果还没有)
cd /home/happy
git clone <your-repo-url>
cd child_happy_patter_release

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env
```

#### 4.2 环境变量配置
编辑 `.env` 文件：
```env
# 启用Ollama本地模型
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=emotion_lora
OLLAMA_TIMEOUT=60

# AMD优化配置
OLLAMA_NUM_THREAD=16
OLLAMA_NUM_BATCH=512
OLLAMA_MAX_LOADED_MODELS=4
OLLAMA_FLASH_ATTENTION=1

# OpenAI配置（备用）
OPENAI_API_KEY=sk-U6KEVS6duof2hKtKwxuuX6NidqLOrlAq0REQpxoAVa1keego
OPENAI_BASE_URL=https://api2.aigcbest.top/v1
```

#### 4.3 验证配置
配置文件已更新支持Ollama：
- `backend/config/settings.py`: Ollama配置
- `backend/utils/ollama_client.py`: Ollama客户端
- `backend/utils/openai_client.py`: 统一接口

### 5. 运行测试和启动服务

#### 5.1 运行集成测试
```bash
cd /home/happy/child_happy_patter_release/backend
source ../venv/bin/activate
python test_ollama_integration.py
```

#### 5.2 性能监控
```bash
# 启动性能监控
sudo /usr/local/bin/monitor_amd_performance.sh

# 在另一个终端查看系统资源
htop
```

#### 5.3 启动后端服务
```bash
# 方法1：直接运行
cd /home/happy/child_happy_patter_release/backend
source ../venv/bin/activate
python main.py

# 方法2：使用一键启动脚本
sudo /usr/local/bin/start_happy_partner.sh
```

#### 5.4 测试API接口
```bash
# 测试聊天接口
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "session_id": 1,
    "content": "我感到很难过"
  }'

# 测试Emotion Agent
curl -X POST "http://localhost:8000/emotion/support" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "content": "我在学校被欺负了",
    "emotion_type": "难过"
  }'
```

#### 5.5 压力测试
```bash
# 安压测工具
pip install locust

# 创建压测脚本 locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between
import json

class HappyPartnerUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def chat_request(self):
        headers = {"Content-Type": "application/json"}
        data = {
            "user_id": 1,
            "session_id": 1,
            "content": "你好，我感到很开心"
        }
        self.client.post("/chat", json=data, headers=headers)
    
    @task(3)
    def emotion_request(self):
        headers = {"Content-Type": "application/json"}
        data = {
            "user_id": 1,
            "content": "我今天很难过",
            "emotion_type": "难过"
        }
        self.client.post("/emotion/support", json=data, headers=headers)
EOF

# 运行压测
locust -f locustfile.py --host=http://localhost:8000
```

## 模型特性

### emotion_lora模型特点
- **基础模型**: qwen2.5:0.5b
- **LoRA微调**: 专门针对儿童情感陪伴优化
- **角色设定**: 彩虹小精灵，专门陪伴3-12岁小朋友
- **核心功能**: 情绪识别、情感支持、游戏化互动

### 支持的情感类型
- 生气 → "小火龙在喷火啦！"
- 难过 → "心里下雨了"
- 害怕 → "小心脏在蹦蹦跳"
- 讨厌 → "小眉毛皱起来啦"
- 其他复杂情绪

### 回复特点
- 使用短句（每句不超过15个字）
- 多用拟声词和表情符号
- 用孩子能理解的比喻
- 积极正面，避免否定感受
- 鼓励与父母沟通

## AMD锐龙AI MAX+395性能优化

### 🎮 硬件性能发挥

#### CPU优化
```bash
# 查看CPU信息
lscpu | grep "Model name"
cat /proc/cpuinfo | grep "cpu cores"

# 设置CPU性能模式
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 启用所有CPU核心
echo 1 | sudo tee /sys/devices/system/cpu/cpu*/online
```

#### 内存优化
```bash
# 查看内存信息
free -h
cat /proc/meminfo

# 禁用透明大页 (提升AI性能)
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# 调整内存过commit策略
echo 1 | sudo tee /proc/sys/vm/overcommit_memory
```

#### GPU加速 (可选)
```bash
# 检查GPU信息
rocm-smi --showproductname --showuse --showtemp --showmeminfo vram

# 设置GPU性能模式
sudo rocm-smi --setperflevel high

# 监控GPU使用情况
watch -n 1 rocm-smi
```

### 🚀 Ollama性能调优

#### 环境变量优化
```bash
# 在 /etc/systemd/system/ollama.service.d/performance.conf 中设置
Environment="OLLAMA_NUM_THREAD=16"          # 利用16核性能
Environment="OLLAMA_NUM_BATCH=512"          # 批处理优化
Environment="OLLAMA_MAX_LOADED_MODELS=4"     # 预加载模型
Environment="OLLAMA_KEEP_ALIVE=5m"          # 保持模型活跃
Environment="OLLAMA_FLASH_ATTENTION=1"       # 启用Flash Attention
Environment="OLLAMA_F16=1"                  # 使用半精度
```

#### Modelfile优化参数
```yaml
# AMD优化参数
PARAMETER num_thread 16          # 多线程并行
PARAMETER num_batch 512          # 批处理大小
PARAMETER f16_kv true            # 半精度KV缓存
PARAMETER use_mmap true           # 内存映射
PARAMETER mlock true              # 锁定内存
PARAMETER num_ctx 2048           # 上下文长度
PARAMETER num_predict 512         # 生成长度
```

### 📊 性能监控

#### 系统监控
```bash
# CPU使用率
mpstat 1 5

# 内存使用
free -h

# 磁盘IO
iostat -xz 1

# 网络状态
sar -n DEV 1
```

#### Ollama监控
```bash
# Ollama服务状态
sudo systemctl status ollama

# 查看Ollama日志
sudo journalctl -u ollama -f

# 模型加载情况
ollama ps
ollama list
```

#### 应用监控
```bash
# Python进程内存使用
ps aux | grep python

# 端口占用
netstat -tulpn | grep :8000

# 响应时间测试
time curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"user_id":1,"content":"test"}'
```

### ⚡ 预期性能指标

#### 响应时间
- **MetaAgent路由**: 200-500ms
- **EmotionAgent情感分析**: 500-1000ms
- **EduAgent教育问答**: 1000-2000ms
- **完整聊天流程**: 1500-3000ms

#### 吞吐量
- **并发用户**: 10-20个
- **QPS**: 5-10请求/秒
- **内存使用**: 4-8GB
- **CPU使用**: 30-60%

#### 资源占用
- **Ollama服务**: 2-4GB内存
- **Python后端**: 1-2GB内存
- **模型加载**: 1-2GB内存
- **系统预留**: 2-4GB内存

## 故障排除

### 1. Ollama服务无法启动
```bash
# 检查端口占用
netstat -ano | findstr :11434

# 检查防火墙设置
# 确保端口11434未被阻止
```

### 2. 模型创建失败
```bash
# 检查Modelfile路径
# 确保emotion_lora.gguf文件存在且路径正确

# 重新创建模型
ollama rm emotion_lora
ollama create emotion_lora -f Modelfile_final.emotion
```

### 3. API调用失败
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 检查模型列表
ollama list

# 查看日志
journalctl -u ollama -f  # Linux系统
```

### 4. 性能问题
```bash
# 监控资源使用
tasklist | findstr ollama  # Windows
top | grep ollama          # Linux

# 调整参数
ollama run emotion_lora --num-ctx 1024
```

## 回滚到云API

如果需要临时切换回云API，修改 `.env` 文件：
```env
USE_OLLAMA=false
```

或者直接修改环境变量：
```bash
export USE_OLLAMA=false
```

## 监控和日志

### 1. Ollama日志
```bash
# 查看Ollama服务日志
ollama ps
```

### 2. 应用日志
查看 `backend/utils/ollama_client.py` 中的错误处理和日志输出。

### 3. 性能监控
```bash
# 测试响应时间
time curl -X POST "http://localhost:11434/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"model": "emotion_lora", "prompt": "你好"}'
```

## 总结

通过以上步骤，您已成功将Happy Partner系统从DeepSeek API切换到本地Ollama部署的emotion_lora模型。这样做的优势包括：

1. **数据隐私**: 所有处理都在本地完成
2. **成本控制**: 无API调用费用
3. **响应速度**: 本地处理延迟更低
4. **定制化**: 可根据需要调整模型参数

如需进一步优化或有任何问题，请参考故障排除部分或联系技术支持。
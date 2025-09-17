#!/bin/bash

# AMD锐龙AI MAX+395性能优化脚本
# 专为Happy Partner项目和Ollama优化

echo "🚀 开始AMD锐龙AI MAX+395性能优化..."

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   echo "⚠️ 请以root权限运行此脚本"
   exit 1
fi

# 1. CPU调度优化
echo "📊 优化CPU调度器..."
# 设置性能模式
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
# 启用所有CPU核心
echo 1 | tee /sys/devices/system/cpu/cpu*/online

# 2. 内存优化
echo "💾 优化内存管理..."
# 禁用透明大页（可能影响AI性能）
echo never | tee /sys/kernel/mm/transparent_hugepage/enabled
# 调整内存过commit策略
echo 1 > /proc/sys/vm/overcommit_memory

# 3. 文件系统优化
echo "📁 优化文件系统..."
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
# 优化IO调度器
echo mq-deadline | tee /sys/block/sd*/queue/scheduler

# 4. 网络优化
echo "🌐 优化网络设置..."
# 增加TCP缓冲区大小
echo "net.core.rmem_max = 134217728" >> /etc/sysctl.conf
echo "net.core.wmem_max = 134217728" >> /etc/sysctl.conf
echo "net.ipv4.tcp_rmem = 4096 87380 134217728" >> /etc/sysctl.conf
echo "net.ipv4.tcp_wmem = 4096 65536 134217728" >> /etc/sysctl.conf

# 5. AMD特定优化
echo "🎮 应用AMD特定优化..."
# 检查是否安装了ROCm
if command -v rocm-smi &> /dev/null; then
    echo "✅ 检测到ROCm，应用GPU优化..."
    # 设置GPU性能模式
    rocm-smi --setperflevel high
    # 优化GPU内存管理
    echo 1 | tee /sys/class/drm/card*/device/power_dpm_force_performance_level
fi

# 6. Ollama服务优化
echo "🤖 配置Ollama服务优化..."
# 创建Ollama系统服务配置
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/performance.conf << EOF
[Service]
# 环境变量优化
Environment="OLLAMA_NUM_THREAD=16"
Environment="OLLAMA_NUM_BATCH=512"
Environment="OLLAMA_MAX_LOADED_MODELS=4"
Environment="OLLAMA_KEEP_ALIVE=5m"
Environment="OLLAMA_FLASH_ATTENTION=1"

# 资源限制
LimitNOFILE=65536
LimitMEMLOCK=infinity

# CPU亲和性（可选，根据您的CPU核心数调整）
# CPUAffinity=0-15
EOF

# 7. 创建监控脚本
echo "📈 创建性能监控脚本..."
cat > /usr/local/bin/monitor_amd_performance.sh << 'EOF'
#!/bin/bash
# AMD性能监控脚本

while true; do
    clear
    echo "🎮 AMD锐龙AI MAX+395性能监控"
    echo "================================"
    
    # CPU使用率
    echo "📊 CPU使用率:"
    mpstat 1 1 | grep "Average"
    
    # 内存使用情况
    echo "💾 内存使用情况:"
    free -h
    
    # GPU使用情况（如果可用）
    if command -v rocm-smi &> /dev/null; then
        echo "🎮 GPU使用情况:"
        rocm-smi --showproductname --showuse --showtemp
    fi
    
    # Ollama进程状态
    echo "🤖 Ollama进程状态:"
    ps aux | grep ollama | grep -v grep
    
    # 系统负载
    echo "⚖️ 系统负载:"
    uptime
    
    sleep 5
done
EOF

chmod +x /usr/local/bin/monitor_amd_performance.sh

# 8. 创建一键启动脚本
echo "🚀 创建一键启动脚本..."
cat > /usr/local/bin/start_happy_partner.sh << 'EOF'
#!/bin/bash
# Happy Partner项目一键启动脚本

echo "🌈 启动Happy Partner儿童教育AI系统..."

# 检查Ollama服务
if ! systemctl is-active --quiet ollama; then
    echo "🤖 启动Ollama服务..."
    systemctl start ollama
    sleep 5
fi

# 检查模型是否已加载
if ! ollama list | grep -q "emotion_lora"; then
    echo "📦 emotion_lora模型未加载，请先运行部署脚本"
    exit 1
fi

# 启动后端服务
echo "🚀 启动后端服务..."
cd /home/user/child_happy_patter_release/backend
python3 main.py &

echo "✅ Happy Partner系统启动完成！"
echo "📊 访问 http://localhost:8000/docs 查看API文档"
echo "🎮 运行 monitor_amd_performance.sh 查看性能监控"
EOF

chmod +x /usr/local/bin/start_happy_partner.sh

# 重新加载systemd配置
systemctl daemon-reload

echo "✅ AMD锐龙AI MAX+395性能优化完成！"
echo ""
echo "📋 下一步操作："
echo "1. 重启系统以应用所有优化"
echo "2. 运行 systemctl start ollama 启动Ollama服务"
echo "3. 运行 monitor_amd_performance.sh 查看性能监控"
echo "4. 运行 start_happy_partner.sh 启动Happy Partner系统"
echo ""
echo "🎮 享受您的AMD锐龙AI MAX+395极致性能！"
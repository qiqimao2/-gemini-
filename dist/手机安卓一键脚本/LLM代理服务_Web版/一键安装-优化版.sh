#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务 - Termux一键安装脚本（优化版）
# 解决所有已知问题并提供更好的用户体验

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════╗"
    echo "║      LLM代理服务 Termux优化安装       ║"
    echo "║           解决兼容性问题 v3.0         ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[步骤 $1/$2]${NC} $3"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_environment() {
    if [[ "$PREFIX" != *"com.termux"* ]]; then
        print_error "此脚本只能在Termux环境中运行"
        exit 1
    fi
    
    if [[ ! -f "app.py" ]]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查存储权限
check_storage_permission() {
    print_info "检查存储权限..."
    
    if [[ ! -w "$HOME" ]]; then
        print_error "没有写入权限，请运行: termux-setup-storage"
        exit 1
    fi
    
    # 创建测试文件
    touch "$HOME/.termux-permission-test" 2>/dev/null && rm "$HOME/.termux-permission-test"
    if [[ $? -ne 0 ]]; then
        print_error "存储权限不足，请运行: termux-setup-storage"
        exit 1
    fi
}

# 检查网络连接
check_network() {
    print_status "检查网络连接..."
    
    local network_ok=false
    
    # 检查基本网络连接
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        print_status "基本网络连接正常"
        network_ok=true
    else
        print_warning "基本网络连接失败"
    fi
    
    # 检查DNS解析
    if nslookup google.com > /dev/null 2>&1; then
        print_status "DNS解析正常"
    else
        print_warning "DNS解析可能有问题"
        network_ok=false
    fi
    
    # 检查PyPI访问
    if curl -s --connect-timeout 5 https://pypi.org > /dev/null; then
        print_status "PyPI访问正常"
    else
        print_warning "PyPI访问可能有问题"
        network_ok=false
    fi
    
    if ! $network_ok; then
        print_warning "网络连接可能有问题，安装依赖可能失败"
        print_warning "建议配置代理或使用国内镜像"
        
        # 配置pip国内镜像
        mkdir -p "$HOME/.pip"
        cat > "$HOME/.pip/pip.conf" << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
        print_status "已配置pip使用清华镜像"
    else
        print_status "网络连接正常"
    fi
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    # 检查Python命令
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python未安装，正在安装..."
        pkg install -y python
    fi
    
    # 设置Python命令
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    fi
    
    print_info "使用Python命令: $PYTHON_CMD"
}

# 主安装流程
main() {
    print_banner
    
    check_environment
    check_storage_permission
    check_network
    check_python
    
    TOTAL_STEPS=7
    CURRENT_STEP=0
    
    # 步骤1：检查并安装依赖
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "检查并安装Termux依赖包"
    
    # 更新包列表
    pkg update -y
    
    # 安装必要的包
    local packages=("termux-services" "python" "curl" "procps" "net-tools" "openssl-tool")
    
    for pkg in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            print_info "安装 $pkg..."
            if ! pkg install -y "$pkg"; then
                print_error "安装 $pkg 失败"
                exit 1
            fi
        else
            print_info "$pkg 已安装"
        fi
    done
    
    # 启用termux-services
    if [[ ! -d "$HOME/.termux/service" ]]; then
        mkdir -p "$HOME/.termux/service"
    fi
    
    # 步骤2：配置Python环境
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "配置Python环境"
    
    # 升级pip
    $PYTHON_CMD -m pip install --upgrade pip
    
    # 安装依赖
    local requirements_file=""
    local possible_files=(
        "termux-services/requirements-termux.txt"
        "requirements-termux.txt"
        "requirements.txt"
    )
    
    for file in "${possible_files[@]}"; do
        if [[ -f "$file" ]]; then
            requirements_file="$file"
            break
        fi
    done
    
    if [[ -n "$requirements_file" ]]; then
        print_info "安装Python依赖（来自: $requirements_file）..."
        if $PYTHON_CMD -m pip install -r "$requirements_file"; then
            print_info "Python依赖安装完成"
        else
            print_error "Python依赖安装失败"
            print_error "请手动运行: $PYTHON_CMD -m pip install -r $requirements_file"
        fi
    else
        print_error "未找到依赖文件"
        exit 1
    fi
    
    # 步骤3：创建服务配置
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "创建服务配置"
    
    # 创建必要的目录
    mkdir -p "$HOME/.llm-proxy/logs"
    mkdir -p "$HOME/.config/llm-proxy"
    mkdir -p "$HOME/.termux/boot"
    
    # 创建服务脚本
    cat > "$HOME/.termux/service/llm-proxy" << EOF
#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务守护进程（优化版）

PROJECT_DIR="$(pwd)"
LOG_DIR="$HOME/.llm-proxy/logs"
LOG_FILE="$LOG_DIR/llm-proxy.log"
ERROR_LOG="$LOG_DIR/llm-proxy-error.log"
PID_FILE="$LOG_DIR/llm-proxy.pid"

# 设置Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

# 检查依赖是否安装
if [[ ! -f "requirements_installed" ]]; then
    echo "\$(date): 正在安装依赖..." >> "\$LOG_FILE"
    $PYTHON_CMD -m pip install -r requirements.txt >> "\$LOG_FILE" 2>&1
    if [[ \$? -eq 0 ]]; then
        touch "requirements_installed"
        echo "\$(date): 依赖安装完成" >> "\$LOG_FILE"
    else
        echo "\$(date): 依赖安装失败" >> "\$ERROR_LOG"
        exit 1
    fi
fi

# 启动服务
echo "\$(date): 启动LLM代理服务..." >> "\$LOG_FILE"
nohup $PYTHON_CMD app.py cli >> "\$LOG_FILE" 2>> "\$ERROR_LOG" &
PID=\$!

# 保存PID
echo \$PID > "\$PID_FILE"

# 等待并检查
sleep 5
if kill -0 \$PID 2>/dev/null; then
    echo "\$(date): LLM代理服务启动成功，PID: \$PID" >> "\$LOG_FILE"
    echo "LLM代理服务已启动，PID: \$PID"
else
    echo "\$(date): LLM代理服务启动失败" >> "\$ERROR_LOG"
    echo "服务启动失败，查看日志: \$LOG_FILE"
    exit 1
fi
EOF
    
    chmod +x "$HOME/.termux/service/llm-proxy"
    
    # 步骤4：设置开机自启
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "设置开机自启"
    
    cat > "$HOME/.termux/boot/llm-proxy" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务开机启动脚本

# 等待系统初始化
sleep 3

# 启动服务
sv up llm-proxy
EOF
    
    chmod +x "$HOME/.termux/boot/llm-proxy"
    
    # 步骤5：启动服务
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "启动服务"
    
    sv up llm-proxy
    
    # 步骤6：测试服务
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "测试服务"
    
    # 获取配置中的端口
    local api_port=$(grep -E "^port\s*=" config.ini 2>/dev/null | cut -d'=' -f2 | tr -d ' ' || echo "8080")
    
    sleep 5
    if curl -s "http://localhost:$api_port/" > /dev/null 2>&1; then
        print_info "服务响应正常 ✓"
    else
        print_warning "服务可能未完全启动，请等待几秒后重试"
    fi
    
    # 步骤7：显示完成信息
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "安装完成"
    
    echo ""
    echo "======================================"
    echo "安装完成！"
    echo "======================================"
    echo ""
    echo "服务管理："
    echo "  启动: sv up llm-proxy"
    echo "  停止: sv down llm-proxy"
    echo "  重启: sv restart llm-proxy"
    echo "  状态: sv status llm-proxy"
    echo ""
    echo "日志管理："
    echo "  查看日志: tail -f ~/.llm-proxy/logs/llm-proxy.log"
    echo "  清理日志: > ~/.llm-proxy/logs/llm-proxy.log"
    echo ""
    echo "配置文件："
    echo "  主配置: $(pwd)/config.ini"
    echo "  日志目录: ~/.llm-proxy/logs/"
    echo ""
    echo "API端点："
    echo "  地址: http://localhost:$api_port"
    echo "  测试: curl -X POST http://localhost:$api_port/v1/chat/completions"
    echo ""
    echo "重要提醒："
    echo "1. 请编辑 config.ini 文件，替换 YOUR_API_KEY_X 为真实的API密钥"
    echo "2. 如果遇到网络问题，请配置代理或使用国内API镜像"
    echo "3. 查看日志命令: tail -f ~/.llm-proxy/logs/llm-proxy.log"
    echo ""
    print_info "LLM代理服务已成功配置为Termux服务！"
    print_info "服务将在设备重启后自动启动"
    print_info "如有问题，请查看日志文件"
}

# 错误处理
trap 'print_error "脚本执行过程中出现错误，请检查上面的错误信息"; exit 1' ERR

# 运行主程序
main
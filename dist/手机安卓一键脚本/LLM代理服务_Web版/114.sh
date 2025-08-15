#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务 - Termux一键安装脚本（完整修复版）
# 修复所有已知问题，确保安装成功

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 超时设置
TIMEOUT=15

# 打印函数
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════╗"
    echo "║      LLM代理服务 Termux完整修复       ║"
    echo "║           解决所有安装问题            ║"
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

# 安全执行命令函数
safe_run() {
    local cmd="$1"
    local timeout_val="${2:-$TIMEOUT}"
    local description="${3:-执行命令}"
    
    print_info "$description..."
    
    # 使用timeout命令保护，避免卡住
    if timeout "$timeout_val" bash -c "$cmd" 2>/dev/null; then
        return 0
    else
        print_warning "$description 超时或失败"
        return 1
    fi
}

# 检查环境
check_environment() {
    print_info "检查运行环境..."
    
    # 检查是否在Termux环境中
    if [[ -n "$PREFIX" && "$PREFIX" == *"com.termux"* ]]; then
        print_info "检测到Termux环境"
    elif [[ -n "$PREFIX" && "$PREFIX" == *"data/data/com.termux"* ]]; then
        print_info "检测到Termux环境"
    elif [[ -d "/data/data/com.termux" ]]; then
        print_info "检测到Termux环境"
    elif [[ "$0" == *"com.termux"* ]]; then
        print_info "检测到Termux环境"
    else
        # 尝试其他检测方法
        if command -v pkg &> /dev/null; then
            print_info "检测到Termux包管理器，继续运行"
        elif [[ -n "$TERMUX_VERSION" ]]; then
            print_info "检测到Termux版本变量，继续运行"
        else
            print_warning "警告：未检测到Termux环境，但继续运行"
            print_info "如果您确实在Termux中运行，请忽略此警告"
        fi
    fi
    
    # 检查是否在项目根目录
    if [[ ! -f "app.py" ]]; then
        print_error "请在项目根目录运行此脚本"
        print_error "当前目录: $(pwd)"
        print_error "当前目录内容:"
        ls -la
        exit 1
    fi
    
    print_info "确认在项目根目录，找到 app.py 文件"
}

# 检查存储权限
check_storage_permission() {
    print_info "检查存储权限..."
    
    if [[ ! -w "$HOME" ]]; then
        print_error "没有写入权限，请运行: termux-setup-storage"
        exit 1
    fi
    
    # 创建测试文件
    if ! touch "$HOME/.termux-permission-test" 2>/dev/null; then
        print_error "存储权限不足，请运行: termux-setup-storage"
        exit 1
    fi
    rm -f "$HOME/.termux-permission-test"
}

# 检查网络连接（修复版）
check_network() {
    print_info "检查网络连接..."
    
    local network_ok=false
    
    # 检查基本网络连接（带超时保护）
    if safe_run "ping -c 1 8.8.8.8" 5 "检查基本网络连接"; then
        print_info "基本网络连接正常"
        network_ok=true
    else
        print_warning "基本网络连接失败"
    fi
    
    # 检查DNS解析（带超时保护）
    if safe_run "nslookup google.com" 5 "检查DNS解析"; then
        print_info "DNS解析正常"
    else
        print_warning "DNS解析可能有问题"
        network_ok=false
    fi
    
    # 检查PyPI访问（带超时保护）
    if safe_run "curl -s --connect-timeout 3 https://pypi.org > /dev/null" 8 "检查PyPI访问"; then
        print_info "PyPI访问正常"
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
timeout = 60
EOF
        print_info "已配置pip使用清华镜像"
    else
        print_info "网络连接正常"
    fi
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    # 检查Python命令
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_info "Python未安装，正在安装..."
        if ! safe_run "pkg install -y python" 60 "安装Python"; then
            print_error "Python安装失败"
            exit 1
        fi
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
    if ! safe_run "pkg update -y" 30 "更新包列表"; then
        print_warning "包列表更新失败，但继续尝试安装"
    fi
    
    # 安装必要的包
    local packages=("termux-services" "python" "curl" "procps" "net-tools" "openssl-tool")
    
    for pkg in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            print_info "安装 $pkg..."
            if ! safe_run "pkg install -y $pkg" 60 "安装 $pkg"; then
                print_warning "安装 $pkg 失败，但继续运行"
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
    if ! safe_run "$PYTHON_CMD -m pip install --upgrade pip" 60 "升级pip"; then
        print_warning "pip升级失败，但继续运行"
    fi
    
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
        if safe_run "$PYTHON_CMD -m pip install -r \"$requirements_file\"" 120 "安装Python依赖"; then
            print_info "Python依赖安装完成"
        else
            print_warning "Python依赖安装失败，请手动运行: $PYTHON_CMD -m pip install -r $requirements_file"
        fi
    else
        print_warning "未找到依赖文件，跳过Python依赖安装"
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
# LLM代理服务守护进程（完整修复版）

PROJECT_DIR="\$(pwd)"
LOG_DIR="$HOME/.llm-proxy/logs"
LOG_FILE="\$LOG_DIR/llm-proxy.log"
ERROR_LOG="\$LOG_DIR/llm-proxy-error.log"
PID_FILE="\$LOG_DIR/llm-proxy.pid"

# 设置Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

cd "\$PROJECT_DIR"
mkdir -p "\$LOG_DIR"

# 检查依赖是否安装
if [[ ! -f "requirements_installed" ]]; then
    echo "\$(date): 正在安装依赖..." >> "\$LOG_FILE"
    \$PYTHON_CMD -m pip install -r termux-services/requirements-termux.txt >> "\$LOG_FILE" 2>&1
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
nohup \$PYTHON_CMD app.py cli >> "\$LOG_FILE" 2>> "\$ERROR_LOG" &
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
    
    if safe_run "sv up llm-proxy" 10 "启动服务"; then
        print_info "服务启动成功"
    else
        print_warning "服务启动失败，请手动启动"
    fi
    
    # 步骤6：测试服务
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "测试服务"
    
    # 获取配置中的端口
    local api_port=$(grep -E "^port\s*=" config.ini 2>/dev/null | cut -d'=' -f2 | tr -d ' ' || echo "8080")
    
    sleep 3
    if safe_run "curl -s \"http://localhost:$api_port/\" > /dev/null" 5 "测试服务响应"; then
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
trap 'print_error "脚本执行过程中出现错误，请检查上面的错误信息"' ERR

# 运行主程序
main
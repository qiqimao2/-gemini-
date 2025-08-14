#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务 - Termux一键安装脚本
# 基于你的GitHub项目优化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════╗"
    echo "║      LLM代理服务 Termux安装器         ║"
    echo "║        一键配置为系统服务             ║"
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
    
    # 检查是否在项目根目录 - 更健壮的检查方式
    if [[ ! -f "app.py" ]]; then
        print_error "请在项目根目录运行此脚本"
        print_error "当前目录: $(pwd)"
        print_error "当前目录内容:"
        ls -la
        exit 1
    fi
    
    print_info "确认在项目根目录，找到 app.py 文件"
}

# 主安装流程
main() {
    print_banner
    
    check_environment
    
    TOTAL_STEPS=6
    CURRENT_STEP=0
    
    # 步骤1：检查并安装依赖
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "检查并安装Termux依赖包"
    
    # 更新包列表
    pkg update -y
    
    # 安装必要的包
    local packages=("termux-services" "python" "curl" "procps" "net-tools")
    
    for pkg in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            print_info "安装 $pkg..."
            pkg install -y "$pkg"
        else
            print_info "$pkg 已安装"
        fi
    done
    
    # 步骤2：配置Python环境
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "配置Python环境"
    
    # 升级pip
    python -m pip install --upgrade pip
    
    # 安装依赖
    if [[ -f "requirements.txt" ]]; then
        print_info "安装Python依赖..."
        pip install -r requirements.txt
    else
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 步骤3：创建服务目录
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "创建服务配置"
    
    # 创建必要的目录
    mkdir -p "$HOME/.termux/service"
    mkdir -p "$HOME/.llm-proxy/logs"
    
    # 创建服务脚本
    cat > "$HOME/.termux/service/llm-proxy" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务守护进程

PROJECT_DIR="$(pwd)"
LOG_DIR="$HOME/.llm-proxy/logs"
LOG_FILE="$LOG_DIR/llm-proxy.log"

cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

# 启动服务
python app.py cli >> "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$LOG_DIR/llm-proxy.pid"

# 等待并检查
sleep 3
if kill -0 $PID 2>/dev/null; then
    echo "LLM代理服务已启动，PID: $PID"
else
    echo "服务启动失败，查看日志: $LOG_FILE"
    exit 1
fi
EOF
    
    chmod +x "$HOME/.termux/service/llm-proxy"
    
    # 步骤4：设置开机自启
    ((CURRENT_STEP++))
    print_step $CURRENT_STEP $TOTAL_STEPS "设置开机自启"
    
    mkdir -p "$HOME/.termux/boot"
    cat > "$HOME/.termux/boot/llm-proxy" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
cd "$(dirname "$0")/.."
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
    
    sleep 3
    if curl -s http://localhost:8080/ > /dev/null 2>&1; then
        print_info "服务响应正常 ✓"
    else
        print_warning "服务可能未完全启动，请等待几秒后重试"
    fi
    
    # 显示完成信息
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
    echo "日志查看："
    echo "  tail -f ~/.llm-proxy/logs/llm-proxy.log"
    echo ""
    echo "配置文件："
    echo "  编辑: nano config.ini"
    echo "  重启: sv restart llm-proxy"
    echo ""
    echo "API测试："
    echo "  curl -X POST http://localhost:8080/v1/chat/completions \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -H \"Authorization: Bearer 123\" \\"
    echo "    -d '{\"model\":\"gemini-2.5-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}'"
}

# 运行主程序
main
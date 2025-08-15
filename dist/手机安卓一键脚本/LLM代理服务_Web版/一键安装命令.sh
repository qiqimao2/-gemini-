#!/data/data/com.termux/files/usr/bin/bash
# LLM代理服务 - 超级一键安装命令
# 基于你的GitHub项目地址优化

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════╗"
    echo "║      LLM代理服务 一键安装器           ║"
    echo "║                                       ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

# 主安装流程
main() {
    print_banner
    
    echo -e "${GREEN}开始一键安装LLM代理服务...${NC}"
    
    # 1. 更新Termux
    echo "更新Termux..."
    pkg update -y && pkg upgrade -y
    
    # 2. 安装必要工具
    echo "安装必要工具..."
    pkg install git curl wget -y
    
    # 3. 克隆你的GitHub项目
    echo "下载你的GitHub项目..."
    cd ~
    if [ -d "-gemini-" ]; then
        echo "项目已存在，更新中..."
        cd ./-gemini-
        git pull || echo "无法更新，使用现有版本"
    else
        echo "克隆你的GitHub项目..."
        git clone https://github.com/adc666sav466/-gemini-.git
        cd ./-gemini-
    fi
    
    # 4. 检查是否有Web版目录
    if [ -d "LLM代理服务_Web版" ]; then
        echo "进入Web版目录..."
        cd LLM代理服务_Web版
    fi
    
    # 5. 运行安装脚本
    echo "运行Termux安装脚本..."
    if [ -f "一键安装-完整修复版.sh" ]; then
        chmod +x 一键安装-完整修复版.sh
        ./一键安装-完整修复版.sh
    elif [ -f "install-termux-fixed.sh" ]; then
        chmod +x install-termux-fixed.sh
        ./install-termux-fixed.sh
    elif [ -f "install-termux.sh" ]; then
        chmod +x install-termux.sh
        ./install-termux.sh
    else
        echo "使用修复版安装..."
        chmod +x 一键安装-修复版.sh
        ./一键安装-修复版.sh
    fi
    
    echo -e "${GREEN}安装完成！${NC}"
    echo ""
    echo "现在你可以使用："
    echo "  sv up llm-proxy    # 启动服务"
    echo "  sv status llm-proxy # 查看状态"
    echo "  tail -f ~/.llm-proxy/logs/llm-proxy.log # 查看日志"
}

# 运行主程序
main
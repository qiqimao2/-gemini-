# LLM代理服务 - Termux安装指南

## 快速开始

### 1. 安装Termux
从F-Droid或GitHub下载最新版Termux（推荐从F-Droid获取）

### 2. 更新Termux包
```bash
pkg update && pkg upgrade
```

### 3. 安装Python
```bash
pkg install python
```

### 4. 克隆或下载项目
```bash
# 如果已下载到手机存储
cd /sdcard/LLM代理服务_Web版  # 或实际路径

# 或者使用git克隆
pkg install git
git clone <项目地址>
cd LLM代理服务_Web版
```

### 5. 安装依赖
```bash
# 使用国内镜像加速
pip install -r requirements_termux.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 6. 启动服务
```bash
# 方法1：使用启动脚本
chmod +x start_termux.sh
./start_termux.sh

# 方法2：直接运行
python app.py
```

## 移动端访问

### 本机访问
- 打开浏览器访问：`http://localhost:5001`

### 局域网访问
- 获取手机IP：`ifconfig` 或 `ip addr`
- 其他设备访问：`http://<手机IP>:5001`

### 热点共享
如果手机开启热点，其他设备可直接通过热点IP访问

## 移动端优化特性

### 1. 响应式设计
- 自适应手机屏幕
- 触摸友好的按钮和控件
- 优化的字体大小和间距

### 2. 性能优化
- 减少内存占用
- 优化的网络请求
- 低电量模式支持

### 3. 网络配置
- 自动检测网络环境
- 支持移动数据网络
- 局域网共享配置

### 4. 电池优化
- 减少CPU使用
- 智能休眠模式
- 后台运行优化

## 常见问题

### 端口被占用
```bash
# 查看端口使用情况
netstat -tulpn | grep :5001

# 修改配置文件
nano config.ini
```

### 依赖安装失败
```bash
# 更新pip
pip install --upgrade pip

# 使用不同镜像
pip install -r requirements_termux.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 权限问题
```bash
# 确保有执行权限
chmod +x start_termux.sh

# 检查文件权限
ls -la
```

### 内存不足
```bash
# 启用低内存模式
# 编辑config.ini，设置low_memory_mode=true
```

## 高级配置

### 后台运行
```bash
# 使用nohup
nohup ./start_termux.sh > llm_proxy.log 2>&1 &

# 查看日志
tail -f llm_proxy.log

# 停止服务
pkill -f app.py
```

### 开机自启
```bash
# 创建启动脚本
mkdir -p ~/.termux/boot
echo '#!/data/data/com.termux/files/usr/bin/sh' > ~/.termux/boot/llm-proxy
echo 'cd /sdcard/LLM代理服务_Web版' >> ~/.termux/boot/llm-proxy
echo './start_termux.sh' >> ~/.termux/boot/llm-proxy
chmod +x ~/.termux/boot/llm-proxy
```

### 网络配置
```bash
# 查看所有网络接口
ip link show

# 测试网络连通性
curl -I http://google.com
```

## 故障排除

### 检查服务状态
```bash
# 查看进程
ps aux | grep app.py

# 查看端口
ss -tlnp | grep :5001

# 查看日志
cat llm_proxy.log
```

### 重启服务
```bash
# 停止所有相关进程
pkill -f app.py

# 重新启动
./start_termux.sh
```

### 清理缓存
```bash
# 清理Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## 性能监控

### 查看资源使用
```bash
# 查看内存使用
free -h

# 查看CPU使用
top

# 查看网络状态
netstat -i
```

### 优化建议
- 保持Termux和依赖更新
- 定期清理日志文件
- 避免同时运行多个服务
- 使用WiFi代替移动数据

## 安全提醒

- 不要在公共网络暴露服务
- 定期更换API密钥
- 使用强密码
- 限制访问IP范围

## 获取帮助

- 查看日志文件：`llm_proxy.log`
- 检查GitHub Issues
- 联系技术支持
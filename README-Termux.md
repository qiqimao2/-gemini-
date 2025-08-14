# LLM代理服务 - Termux版

## 🚀 一键在安卓Termux上运行LLM代理服务

### 📱 项目简介
这是一个专为安卓Termux环境优化的LLM代理服务，支持Google Gemini API，提供Web界面和API接口。

### ✨ 特性
- ✅ **一键安装**：复制粘贴即可运行
- ✅ **Termux优化**：专为安卓环境设计
- ✅ **开机自启**：设备重启后自动运行
- ✅ **完整日志**：详细的运行日志
- ✅ **错误处理**：完善的错误提示
- ✅ **端口检测**：自动避免端口冲突

### 🔧 一键安装

**复制粘贴即可运行：**

```bash
# 1. 安装Termux（从F-Droid下载最新版）
# 2. 在Termux中运行：
pkg update -y && pkg upgrade -y
pkg install git curl -y
cd ~
git clone https://github.com/adc666sav466/-gemini-.git
cd -gemini-
chmod +x 一键安装-Termux版.sh
./一键安装-Termux版.sh
```

### 📋 使用方法

安装完成后：

```bash
# 启动服务
sv up llm-proxy

# 停止服务
sv down llm-proxy

# 重启服务
sv restart llm-proxy

# 查看状态
sv status llm-proxy

# 查看实时日志
tail -f ~/.llm-proxy/logs/llm-proxy.log
```

### ⚙️ 配置说明

编辑 `config.ini` 文件：

```ini
[SERVER]
port = 8080              # API端口
host = 0.0.0.0          # 监听地址
api_key = 123           # 访问密钥（请修改）
min_response_length = 400
request_timeout = 180

[API_KEYS]
group1 = ["YOUR_API_KEY_1", "YOUR_API_KEY_2"]
group2 = ["YOUR_API_KEY_3", "YOUR_API_KEY_4"]

[API]
base_url = https://generativelanguage.googleapis.com/v1beta
```

### 🔍 故障排除

#### 常见问题

1. **依赖安装失败**
   ```bash
   pip install -r requirements.txt --no-cache-dir
   ```

2. **端口被占用**
   - 自动检测可用端口
   - 或手动修改config.ini中的port值

3. **网络问题**
   ```bash
   # 配置国内镜像
   mkdir -p ~/.pip
   echo "[global]
   index-url = https://pypi.tuna.tsinghua.edu.cn/simple" > ~/.pip/pip.conf
   ```

4. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络可以访问Google API
   - 查看日志：`tail -f ~/.llm-proxy/logs/llm-proxy.log`

### 📊 性能优化

- **内存使用**：约50-100MB
- **电池优化**：后台运行功耗极低
- **存储需求**：约200MB空间

### 🔄 更新升级

```bash
# 停止服务
sv down llm-proxy

# 更新代码
git pull

# 重新安装
./一键安装-Termux版.sh
```

### 📞 技术支持

- **查看日志**：`tail -f ~/.llm-proxy/logs/llm-proxy.log`
- **重启服务**：`sv restart llm-proxy`
- **提交Issue**：GitHub Issues

### 🎯 项目结构
```
LLM代理服务/
├── app.py                    # 主程序
├── config.ini               # 配置文件
├── requirements.txt         # 依赖列表
├── 一键安装-Termux版.sh     # 一键安装脚本
├── README-Termux.md         # 本说明文档
├── static/                  # 静态文件
├── templates/               # 模板文件
└── ...                      # 其他必要文件
```

### 🎉 安装验证

安装成功后，访问：
- **API地址**：http://localhost:8080
- **测试命令**：
  ```bash
  curl -X POST http://localhost:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer 123" \
    -d '{"model":"gemini-2.5-flash","messages":[{"role":"user","content":"你好"}]}'
  ```

### ⚡ 快速开始

**只需三步：**
1. 安装Termux
2. 复制粘贴一键安装命令
3. 等待安装完成，开始使用！

**现在你可以在安卓手机上使用LLM代理服务了！** 🎊
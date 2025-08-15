:\Users\lkkkktgf\Desktop\LLM代理服务_Web版\README.md</path>
# LLM代理服务 - Web版

这是一个将原始Tkinter GUI界面改为HTML Web界面的LLM代理服务，支持热重载更改配置，为迁移到安卓上的termux做准备。

## 功能特性

- 🌐 **Web界面**: 现代化的响应式Web界面，替代原来的Tkinter GUI
- 🔥 **热重载**: 配置更改后自动保存和重载，无需重启服务
- 📱 **响应式设计**: 支持桌面和移动设备访问
- ⚡ **实时通信**: 使用Socket.IO实现服务器状态实时更新
- 🚀 **双服务架构**: Flask Web界面 + FastAPI代理服务
- 🔄 **API密钥轮询**: 支持多组API密钥自动轮询
- 📊 **服务监控**: 实时查看API服务状态

## 项目结构

```
LLM代理服务_Web版/
├── app.py                 # 主应用文件
├── requirements.txt       # 依赖包列表
├── config.ini            # 配置文件（自动生成）
├── templates/            # HTML模板
│   └── index.html        # 主页面模板
├── static/              # 静态文件
│   ├── css/
│   │   └── style.css    # 样式文件
│   └── js/
│       └── app.js       # 前端JavaScript
└── README.md            # 说明文档
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行Web界面

```bash
python app.py
```

这将启动Flask Web界面，默认访问地址：`http://127.0.0.1:5000`

### 3. 命令行模式（可选）

如果只需要运行API服务，可以使用：

```bash
python app.py cli
```

这将启动FastAPI代理服务，默认地址：`http://0.0.0.0:8080`

## 使用说明

### 基础配置

1. **服务器配置**:
   - API端口: 代理服务监听端口
   - API主机: 代理服务监听地址
   - Web端口: Web界面端口
   - Web主机: Web界面监听地址
   - 服务API密钥: 访问代理服务的密钥
   - 最小响应字符数: 响应内容的最小长度
   - 请求超时: 请求超时时间（秒）
   - 基础URL: 上游API的基础URL

2. **API密钥管理**:
   - 支持两组API密钥，系统会自动轮询使用
   - 每行一个API密钥
   - 空行和无效密钥会被自动过滤

### 服务控制

- **启动API服务**: 启动FastAPI代理服务
- **停止API服务**: 停止代理服务
- **保存配置**: 保存当前配置到文件
- **重新加载**: 重新加载配置文件

### 热重载功能

- 配置更改后会自动保存（1秒防抖）
- 保存成功后会显示通知
- API服务状态实时更新

## API使用

### 代理端点

```
POST /v1/chat/completions
```

### 请求格式

```json
{
  "model": "gemini-2.5-flash",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": false
}
```

### 认证

在请求头中添加API密钥：

```
Authorization: Bearer 你的API密钥
```

## Termux迁移准备

本项目已为迁移到Android Termux做了以下优化：

1. **轻量级依赖**: 使用最小化的依赖包
2. **兼容性设计**: 代码兼容Python 3.11+
3. **配置管理**: 使用标准配置文件格式
4. **网络配置**: 支持不同网络环境配置
5. **资源管理**: 优化内存和CPU使用

### Termux安装步骤

```bash
# 在Termux中安装Python
pkg install python

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

## 配置文件说明

配置文件 `config.ini` 包含以下部分：

```ini
[SERVER]
port = 8080
host = 0.0.0.0
api_key = 123
min_response_length = 400
request_timeout = 30
web_port = 5000
web_host = 127.0.0.1

[API_KEYS]
group1 = ["密钥1", "密钥2", "密钥3", "密钥4"]
group2 = ["密钥5", "密钥6", "密钥7", "密钥8"]

[API]
base_url = https://generativelanguage.googleapis.com/v1beta
```

## 故障排除

### 常见问题

1. **端口被占用**:
   - 修改配置文件中的端口号
   - 或使用 `netstat -tulpn | grep :端口号` 查看端口使用情况

2. **依赖安装失败**:
   - 尝试升级pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

3. **API密钥无效**:
   - 检查API密钥格式是否正确
   - 确认API密钥是否有效且未过期

4. **Web界面无法访问**:
   - 检查防火墙设置
   - 确认Web主机配置正确
   - 检查端口是否被占用

## 开发说明

### 添加新功能

1. 在 `app.py` 中添加新的API端点
2. 在 `templates/index.html` 中添加对应的UI元素
3. 在 `static/js/app.js` 中添加前端交互逻辑
4. 在 `static/css/style.css` 中添加样式

### 调试模式

应用默认以调试模式运行，支持：
- 代码热重载
- 详细错误信息
- 自动重启服务

## 许可证

本项目基于原始LLM代理服务修改，遵循相同的许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
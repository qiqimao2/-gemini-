# LLM代理服务 - 图形界面版本

## 项目简介

这是一个高效的LLM（大语言模型）代理服务，支持通过图形界面进行配置和管理。该服务使用多个API密钥并发请求LLM，并返回第一个满足条件的响应，提高了响应速度和可靠性。

## 功能特点

- 🖥️ **图形化界面**：直观的GUI配置界面，无需编辑代码
- 🔑 **API密钥管理**：支持两组API密钥配置，可批量导入/导出
- ⚙️ **灵活配置**：可自定义端口、响应长度、超时时间等参数
- 🔄 **轮询机制**：智能切换API密钥组，避免频繁使用同一组密钥
- 📊 **实时监控**：内置日志查看器，实时显示服务运行状态
- 🛡️ **安全认证**：支持自定义API密钥认证
- 🌐 **跨平台**：支持Windows、Linux、macOS

## 文件结构

```
LLM代理服务/
├── llm_proxy.py          # 主服务程序
├── gui_app.py            # 图形界面程序
├── config_manager.py     # 配置文件管理器
├── start_gui.py          # GUI启动器
├── config.ini            # 配置文件（自动生成）
├── requirements.txt      # 依赖列表
└── README.md            # 使用说明
```

## 安装和运行

### 1. 安装依赖

打开终端，进入项目目录，运行：

```bash
pip install -r requirements.txt
```

### 2. 运行图形界面

#### 方法1：直接运行GUI启动器
```bash
python start_gui.py
```

#### 方法2：运行图形界面主程序
```bash
python gui_app.py
```

#### 方法3：运行命令行版本
```bash
python llm_proxy.py
```

## 使用说明

### 图形界面操作

1. **启动程序**：运行 `start_gui.py` 或 `gui_app.py`
2. **基础配置**：
   - 设置服务端口（默认8080）
   - 设置服务主机（默认0.0.0.0）
   - 设置服务API密钥（默认123）
   - 设置最小响应字符数（默认400）
   - 设置请求超时时间（默认30秒）

3. **API密钥管理**：
   - 在"API密钥管理"标签页中配置两组API密钥
   - 支持从文件批量导入密钥
   - 支持将密钥导出到文件
   - 支持清空密钥组

4. **启动服务**：
   - 点击"启动服务"按钮
   - 查看"运行日志"标签页监控服务状态

### API使用示例

服务启动后，可以通过以下方式调用：

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 123" \
  -d '{
    "model": "gemini-2.5-flash",
    "messages": [
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 配置文件说明

配置文件 `config.ini` 会自动生成，包含以下部分：

- **[SERVER]**：服务器配置
  - port：服务端口
  - host：服务主机
  - api_key：服务认证密钥
  - min_response_length：最小响应字符数
  - request_timeout：请求超时时间

- **[API_KEYS]**：API密钥配置
  - group1：第一组API密钥（JSON格式）
  - group2：第二组API密钥（JSON格式）

- **[API]**：API配置
  - base_url：基础API地址

## 注意事项

1. **API密钥**：请确保使用有效的Google Gemini API密钥
2. **端口冲突**：如果8080端口被占用，请修改为其他端口
3. **防火墙**：确保防火墙允许配置的端口通信
4. **日志查看**：服务运行日志可在GUI的"运行日志"标签页查看

## 故障排除

### 服务无法启动
- 检查端口是否被占用
- 检查配置文件是否正确
- 查看运行日志获取详细错误信息

### API调用失败
- 检查API密钥是否有效
- 检查网络连接是否正常
- 确认请求格式是否正确

### 响应过短
- 调整"最小响应字符数"设置
- 检查API密钥是否有足够的配额

## 技术支持

如有问题，请检查运行日志或重新配置API密钥。确保所有API密钥都是有效的Google Gemini API密钥。

## 更新日志

- v1.0.0：初始版本，支持GUI配置和管理
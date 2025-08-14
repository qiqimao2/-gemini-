# LLM代理服务 - Gemini反截断工具

## 🎯 项目简介
通过代理中转建立智能路由挑选出最好的回复以用于防截断和优化回复

## 🚀 使用教程（零基础上手）

### 📥 直接运行（推荐）
1. **找到可执行文件**：进入 `dist` 文件夹,解压压缩包里面有详细教程
2. **双击运行**：双击 `哈基米gemini反截断` 即可启动
3. **无需安装**：无需Python环境，开箱即用

<h2>📱 手机端正在火热开发中！如果好用请点个 ⭐ Star 支持一下！</h2>

## 📁 项目结构
```
LLM代理服务/
├── dist/                    # 打包好的可执行文件（直接运行）
│   └── LLM代理服务.exe      # 主程序（双击即用）
├── gui_app.py              # 图形界面
├── llm_proxy.py            # 代理核心功能
├── config_manager.py       # 配置管理
├── start_gui.py            # 启动脚本
├── build_app.py            # 打包脚本
├── requirements.txt        # 依赖列表
├── app_icon.ico           # 应用图标
└── README.md              # 本说明文档
```

## 🛠️ 开发者使用（需要Python环境）

### 环境要求
- Python 3.7+
- Windows 10/11

### 安装运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python start_gui.py
```

### 打包应用
```bash
# 生成可执行文件
python build_app.py
```
打包完成后，可执行文件会在 `dist` 文件夹中

## 🔧 功能特点
- ✅ **反截断技术**：智能处理长文本，避免对话截断
- ✅ **多API支持**：支持Gemini、OpenAI等多种服务
- ✅ **图形界面**：简洁易用的GUI界面
- ✅ **配置管理**：保存API密钥和偏好设置
- ✅ **一键打包**：生成独立可执行文件

## 📋 支持的服务
- Google Gemini
- OpenAI GPT系列
- 其他兼容OpenAI API的服务

## 🆘 常见问题
**Q: 运行时报错怎么办？**
A: 确保在 `dist` 文件夹中运行 `LLM代理服务.exe`

**Q: API密钥如何获取？**
A: 访问对应AI服务商官网申请API密钥

**Q: 支持哪些系统？**
A: 目前支持Windows 10/11系统

## 📞 联系支持
如有问题，请在GitHub提交Issue或加入QQ群：1033083986

### 📱 QQ群二维码
扫描下方二维码加入QQ群：

<p align="center">
  <img src="./微信图片_20250814082355.jpg" alt="QQ群二维码" width="300"/>
</p>

---

**💡 小白提示：直接用就行！进入dist文件夹，双击exe文件即可开始享受无截断的AI对话！**
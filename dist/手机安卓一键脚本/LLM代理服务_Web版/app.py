#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM代理服务 - Web版
将GUI改为HTML界面，支持热重载更改配置，为迁移到安卓上的termux做准备
"""

import asyncio
import httpx
import os
import sys
import json
import time
import logging
import configparser
import threading
import signal
import platform
import socket
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Termux环境检测
IS_TERMUX = os.path.exists('/data/data/com.termux/files/usr/bin/bash')
if IS_TERMUX:
    print("检测到Termux环境，启用移动端优化配置")

# 尝试导入Flask相关模块
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# 尝试导入FastAPI和Pydantic（用于API代理服务）
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# ==================== 辅助函数 ====================
def get_resource_path(relative_path: str) -> str:
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe文件
        base_path = Path(sys.executable).parent
    else:
        # 如果是正常的python脚本
        base_path = Path(__file__).parent
    return str(base_path / relative_path)

# ==================== 配置管理器 ====================
class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = get_resource_path(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        self.config['SERVER'] = {
            'port': '8080',
            'host': '0.0.0.0',
            'api_key': '123',
            'min_response_length': '400',
            'request_timeout': '30',
            'web_port': '5000',
            'web_host': '127.0.0.1'
        }
        
        self.config['API_KEYS'] = {
            'group1': json.dumps([
                "AIzaSyCgh-9h5PhprwiGSrk7oNxD5Bl240gI6Fk",
                "AIzaSyBmfY6uDjeDmaCbjjuDpMhLJe6H8nMMGXA",
                "AIzaSyCRxaB09p2wEDJPbwc69tEukfrsv0HT5YQ",
                "AIzaSyDJqNc2s-L2_RW0-AwMevHRvhYgEMMXLRM"
            ]),
            'group2': json.dumps([
                "AIzaSyDxG_Dn27XZ-OSeg_iWbGduohqD9gYrGiI",
                "AIzaSyDP-WGwWX4SY2uLTaKAivWwuXzX0LqSui0",
                "AIzaSyBwlIzbZ7bnRtYU7iicNdMnLYKkd8XVPDU",
                "AIzaSyDIwwW4ApVM7Dsj7BuCq4766eCWcOW9_mM"
            ])
        }
        
        self.config['API'] = {
            'base_url': 'https://generativelanguage.googleapis.com/v1beta'
        }
        
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise
    
    def get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return {
            'port': int(self.config['SERVER']['port']),
            'host': self.config['SERVER']['host'],
            'api_key': self.config['SERVER']['api_key'],
            'min_response_length': int(self.config['SERVER']['min_response_length']),
            'request_timeout': int(self.config['SERVER']['request_timeout']),
            'web_port': int(self.config['SERVER']['web_port']),
            'web_host': self.config['SERVER']['web_host']
        }
    
    def set_server_config(self, port: int, host: str, api_key: str, 
                         min_response_length: int, request_timeout: int,
                         web_port: int, web_host: str):
        """设置服务器配置"""
        self.config['SERVER']['port'] = str(port)
        self.config['SERVER']['host'] = host
        self.config['SERVER']['api_key'] = api_key
        self.config['SERVER']['min_response_length'] = str(min_response_length)
        self.config['SERVER']['request_timeout'] = str(request_timeout)
        self.config['SERVER']['web_port'] = str(web_port)
        self.config['SERVER']['web_host'] = web_host
        self.save_config()
    
    def get_api_keys(self) -> Dict[str, List[str]]:
        """获取API密钥"""
        return {
            'group1': json.loads(self.config['API_KEYS']['group1']),
            'group2': json.loads(self.config['API_KEYS']['group2'])
        }
    
    def set_api_keys(self, group1: List[str], group2: List[str]):
        """设置API密钥"""
        self.config['API_KEYS']['group1'] = json.dumps(group1)
        self.config['API_KEYS']['group2'] = json.dumps(group2)
        self.save_config()
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self.config['API']['base_url']
    
    def set_base_url(self, base_url: str):
        """设置基础URL"""
        self.config['API']['base_url'] = base_url
        self.save_config()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('llm_proxy.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 防止休眠的线程
def keep_alive():
    """保持服务活跃的线程"""
    import threading
    import time
    
    def _keep_alive_worker():
        while True:
            # 定期记录心跳，防止系统休眠
            logger.debug("服务心跳 - 保持活跃")
            time.sleep(30)  # 每30秒记录一次
    
    keep_alive_thread = threading.Thread(target=_keep_alive_worker, daemon=True)
    keep_alive_thread.start()

# 启动保持活跃线程
keep_alive()

# 全局配置管理器实例
config_manager = ConfigManager()

# ==================== FastAPI服务 (如果可用) ====================
if FASTAPI_AVAILABLE:
    class ChatRequest(BaseModel):
        model: str
        messages: List[Dict[str, Any]]
        temperature: float = 0.7
        max_tokens: int = 4096
        stream: bool = False

    # 轮询计数器
    current_group_index = 0

    def get_current_api_keys():
        """根据轮询机制返回当前应该使用的API密钥组"""
        global current_group_index
        api_keys = config_manager.get_api_keys()
        
        if current_group_index == 0:
            keys = api_keys['group1']
            current_group_index = 1
        else:
            keys = api_keys['group2']
            current_group_index = 0
        
        valid_keys = [key for key in keys if key and not key.startswith("YOUR_") and len(key) > 10]
        return valid_keys

    async def send_single_request(client: httpx.AsyncClient, api_key: str, request_data: dict):
        """使用单个API密钥发送请求"""
        cleaned_data = {}
        supported_params = {
            'model', 'messages', 'temperature', 'max_tokens',
            'top_p', 'top_k', 'stop'
        }
        
        for key, value in request_data.items():
            if key in supported_params:
                cleaned_data[key] = value
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        url = f"{config_manager.get_base_url()}/openai/chat/completions"
        
        try:
            response = await client.post(url, headers=headers, json=cleaned_data,
                                       timeout=config_manager.get_server_config()['request_timeout'])
            response.raise_for_status()
            
            response_text = response.text
            
            if "data:" in response_text:
                lines = response_text.strip().split('\n')
                content = ""
                final_id = ""
                final_model = ""
                final_created = int(time.time())
                
                for line in lines:
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if data == "[DONE]":
                                continue
                                
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content += delta["content"]
                                
                                if "id" in data:
                                    final_id = data["id"]
                                if "model" in data:
                                    final_model = data["model"]
                                if "created" in data:
                                    final_created = data["created"]
                                    
                        except json.JSONDecodeError:
                            continue
                
                if content:
                    return {
                        "id": final_id or "chatcmpl-" + str(int(time.time())),
                        "object": "chat.completion",
                        "created": final_created,
                        "model": final_model or "gemini-2.5-flash",
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": content,
                                },
                                "finish_reason": "stop"
                            }
                        ],
                        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                    }
            
            try:
                return response.json()
            except ValueError as e:
                logger.error(f"JSON解析错误: {e}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"请求错误: {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None

    async def generate_fake_stream_response(request_data: dict):
        """获取完整的响应内容，等待15秒后选择token最长的响应，然后以流式方式发送给前端"""
        try:
            current_keys = get_current_api_keys()
            if not current_keys:
                raise HTTPException(status_code=500, detail="没有可用的API密钥")
            
            valid_responses = []
            
            async with httpx.AsyncClient() as client:
                tasks = [
                    asyncio.create_task(send_single_request(client, key, request_data))
                    for key in current_keys
                ]
                
                # 收集所有有效的响应
                for future in asyncio.as_completed(tasks):
                    try:
                        result = await future
                        if result and "choices" in result and result["choices"]:
                            message_content = result["choices"][0].get("message", {}).get("content", "")
                            if len(message_content) >= config_manager.get_server_config()['min_response_length']:
                                valid_responses.append({
                                    'result': result,
                                    'content': message_content,
                                    'token_count': len(message_content)
                                })
                    except asyncio.CancelledError:
                        pass
                
                # 等待15秒收集更多响应
                if valid_responses:
                    # 已经有有效响应，继续等待其他响应
                    remaining_tasks = [task for task in tasks if not task.done()]
                    if remaining_tasks:
                        try:
                            done, pending = await asyncio.wait(remaining_tasks, timeout=15)
                            
                            # 处理剩余完成的任务
                            for task in done:
                                try:
                                    result = task.result()
                                    if result and "choices" in result and result["choices"]:
                                        message_content = result["choices"][0].get("message", {}).get("content", "")
                                        if len(message_content) >= config_manager.get_server_config()['min_response_length']:
                                            valid_responses.append({
                                                'result': result,
                                                'content': message_content,
                                                'token_count': len(message_content)
                                            })
                                except Exception as e:
                                    logger.error(f"处理响应时出错: {e}")
                                    pass
                            
                            # 取消仍在进行的任务
                            for task in pending:
                                task.cancel()
                                
                        except asyncio.TimeoutError:
                            logger.warning("等待响应超时")
                            pass
                
                # 选择token最长的响应
                if valid_responses:
                    best_response = max(valid_responses, key=lambda x: x['token_count'])
                    return await stream_response_content(best_response['result'], best_response['content'])

            raise HTTPException(status_code=503, detail="所有上游API请求均失败")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成流式响应时出错: {e}")
            raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

    async def stream_response_content(result: dict, content: str):
        """将完整的响应内容以流式方式发送给前端"""
        response_id = result.get("id", f"chatcmpl-{int(time.time())}")
        created_time = result.get("created", int(time.time()))
        model_name = result.get("model", "gemini-2.5-flash")
        
        async def generate_stream():
            chunk_size = max(1, len(content) // 50)
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                chunk_data = {
                    "id": response_id, "object": "chat.completion.chunk", "created": created_time, "model": model_name,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                await asyncio.sleep(0.01)
            
            final_data = {
                "id": response_id, "object": "chat.completion.chunk", "created": created_time, "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(final_data)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    # 初始化FastAPI应用
    app_fastapi = FastAPI(title="LLM代理服务", version="2.0.0")
    app_fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )

    @app_fastapi.post("/v1/chat/completions")
    async def chat_completions_proxy(chat_request: ChatRequest, request: Request):
        try:
            api_key_header = request.headers.get("Authorization")
            if not api_key_header or not api_key_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="缺少API密钥或格式不正确")
            
            provided_key = api_key_header.split(" ")[1]
            server_config = config_manager.get_server_config()
            if not provided_key or provided_key != server_config['api_key']:
                raise HTTPException(status_code=401, detail="API密钥无效")
            
            request_data = await request.json()
            
            if chat_request.stream:
                return await generate_fake_stream_response(request_data)
            
            current_keys = get_current_api_keys()
            if not current_keys:
                raise HTTPException(status_code=500, detail="服务器未配置有效的API密钥")
            
            valid_responses = []
            
            async with httpx.AsyncClient() as client:
                tasks = [
                    asyncio.create_task(send_single_request(client, key, request_data))
                    for key in current_keys
                ]
                
                # 收集所有有效的响应
                for future in asyncio.as_completed(tasks):
                    try:
                        result = await future
                        if result and "choices" in result and result["choices"]:
                            message_content = result["choices"][0].get("message", {}).get("content", "")
                            if len(message_content) >= server_config['min_response_length']:
                                valid_responses.append({
                                    'result': result,
                                    'content': message_content,
                                    'token_count': len(message_content)
                                })
                    except asyncio.CancelledError:
                        pass
                
                # 等待15秒收集更多响应
                if valid_responses:
                    # 已经有有效响应，继续等待其他响应
                    remaining_tasks = [task for task in tasks if not task.done()]
                    if remaining_tasks:
                        try:
                            done, pending = await asyncio.wait(remaining_tasks, timeout=15)
                            
                            # 处理剩余完成的任务
                            for task in done:
                                try:
                                    result = task.result()
                                    if result and "choices" in result and result["choices"]:
                                        message_content = result["choices"][0].get("message", {}).get("content", "")
                                        if len(message_content) >= server_config['min_response_length']:
                                            valid_responses.append({
                                                'result': result,
                                                'content': message_content,
                                                'token_count': len(message_content)
                                            })
                                except Exception as e:
                                    logger.error(f"处理响应时出错: {e}")
                                    pass
                            
                            # 取消仍在进行的任务
                            for task in pending:
                                task.cancel()
                                
                        except asyncio.TimeoutError:
                            logger.warning("等待响应超时")
                            pass
                
                # 选择token最长的响应
                if valid_responses:
                    best_response = max(valid_responses, key=lambda x: x['token_count'])
                    return JSONResponse(content=best_response['result'])

            raise HTTPException(status_code=503, detail="所有上游API请求均失败")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"处理聊天完成请求时出错: {e}")
            raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

    @app_fastapi.get("/")
    def read_root():
        return {"status": "ok", "message": "LLM代理服务正在运行"}

# ==================== Flask Web界面 (如果可用) ====================
if FLASK_AVAILABLE:
    app_flask = Flask(__name__, 
                     template_folder='templates',
                     static_folder='static')
    CORS(app_flask)
    socketio = SocketIO(app_flask, cors_allowed_origins="*")
    
    # 全局变量
    api_server_thread = None
    is_api_server_running = False
    api_server_lock = threading.Lock()
    
    @app_flask.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app_flask.route('/test')
    def test():
        """测试页面"""
        return render_template('test.html')
    
    @app_flask.route('/api/config', methods=['GET'])
    def get_config():
        """获取配置"""
        try:
            server_config = config_manager.get_server_config()
            api_keys = config_manager.get_api_keys()
            base_url = config_manager.get_base_url()
            
            return jsonify({
                'server': server_config,
                'api_keys': api_keys,
                'base_url': base_url
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app_flask.route('/api/config', methods=['POST'])
    def save_config():
        """保存配置"""
        try:
            data = request.get_json()
            
            # 保存服务器配置
            if 'server' in data:
                server = data['server']
                config_manager.set_server_config(
                    port=int(server['port']),
                    host=server['host'],
                    api_key=server['api_key'],
                    min_response_length=int(server['min_response_length']),
                    request_timeout=int(server['request_timeout']),
                    web_port=int(server['web_port']),
                    web_host=server['web_host']
                )
            
            # 保存API密钥
            if 'api_keys' in data:
                api_keys = data['api_keys']
                config_manager.set_api_keys(
                    group1=api_keys['group1'],
                    group2=api_keys['group2']
                )
            
            # 保存基础URL
            if 'base_url' in data:
                config_manager.set_base_url(data['base_url'])
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app_flask.route('/api/server/start', methods=['POST'])
    def start_api_server():
        """启动API服务器"""
        global api_server_thread, is_api_server_running
        
        with api_server_lock:
            if is_api_server_running:
                return jsonify({'error': '服务器已在运行中'})
            
            if not FASTAPI_AVAILABLE:
                return jsonify({'error': 'FastAPI不可用，无法启动API服务器'})
            
            try:
                server_config = config_manager.get_server_config()
                
                def run_api_server():
                    try:
                        import uvicorn
                        uvicorn.run(
                            app_fastapi,
                            host=server_config['host'],
                            port=server_config['port'],
                            log_level="info"
                        )
                    except Exception as e:
                        logger.error(f"API服务器运行错误: {e}")
                        with api_server_lock:
                            global is_api_server_running
                            is_api_server_running = False
                
                api_server_thread = threading.Thread(target=run_api_server, daemon=True)
                api_server_thread.start()
                is_api_server_running = True
                
                # 通过SocketIO通知前端
                socketio.emit('server_status', {
                    'status': 'running',
                    'url': f"http://{server_config['host']}:{server_config['port']}"
                })
                
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"启动API服务器失败: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app_flask.route('/api/server/stop', methods=['POST'])
    def stop_api_server():
        """停止API服务器"""
        global is_api_server_running
        
        with api_server_lock:
            if not is_api_server_running:
                return jsonify({'error': '服务器未运行'})
            
            try:
                # 注意：这里只是简单标记为停止，实际需要更复杂的进程管理
                is_api_server_running = False
                
                # 通过SocketIO通知前端
                socketio.emit('server_status', {
                    'status': 'stopped'
                })
                
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"停止API服务器失败: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app_flask.route('/api/server/status', methods=['GET'])
    def get_server_status():
        """获取服务器状态"""
        with api_server_lock:
            return jsonify({
                'is_running': is_api_server_running
            })
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接时的处理"""
        emit('server_status', {
            'status': 'running' if is_api_server_running else 'stopped'
        })

# ==================== 主程序入口 ====================
def main():
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        if not FASTAPI_AVAILABLE:
            print("错误：缺少运行命令行服务所需的FastAPI依赖。")
            print("请运行 'pip install fastapi uvicorn httpx pydantic python-multipart'")
            return
            
        print("正在以命令行模式启动API服务...")
        server_config = config_manager.get_server_config()
        
        # 导入uvicorn
        try:
            import uvicorn
            uvicorn.run(app_fastapi, host=server_config['host'], port=server_config['port'])
        except ImportError:
            print("错误：缺少uvicorn依赖。请运行 'pip install uvicorn'")
            return
    else:
        if not FLASK_AVAILABLE:
            print("错误：缺少运行Web界面所需的Flask依赖。")
            print("请运行 'pip install flask flask-cors flask-socketio'")
            if FASTAPI_AVAILABLE:
                print("你可以使用 'python app.py cli' 来运行命令行版本。")
            return
        
        print("正在启动Web界面...")
        server_config = config_manager.get_server_config()
        
        # 启动Flask应用
        socketio.run(
            app_flask,
            host=server_config['web_host'],
            port=server_config['web_port'],
            debug=True  # 启用调试模式，支持热重载
        )

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM代理服务 - 支持配置文件版本
使用配置文件管理API密钥和服务设置
"""

import asyncio
import httpx
import uvicorn
import os
import logging
import json
import time
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# 导入配置管理器
from config_manager import config_manager

# --- 从配置管理器获取配置 ---

# 获取服务器配置
server_config = config_manager.get_server_config()
PORT = server_config['port']
HOST = server_config['host']
API_KEY = server_config['api_key']
MIN_RESPONSE_LENGTH = server_config['min_response_length']
REQUEST_TIMEOUT = server_config['request_timeout']

# 获取API配置
BASE_URL = config_manager.get_base_url()

# 获取API密钥
api_keys = config_manager.get_api_keys()
API_KEYS_GROUP_1 = api_keys['group1']
API_KEYS_GROUP_2 = api_keys['group2']

# 轮询计数器，用于跟踪当前应该使用哪组密钥
current_group_index = 0

# 获取当前应该使用的密钥组
def get_current_api_keys():
    """根据轮询机制返回当前应该使用的API密钥组"""
    global current_group_index
    if current_group_index == 0:
        keys = API_KEYS_GROUP_1
        current_group_index = 1
    else:
        keys = API_KEYS_GROUP_2
        current_group_index = 0
    
    # 过滤掉无效的密钥
    valid_keys = [key for key in keys if key and not key.startswith("YOUR_") and len(key) > 10]
    return valid_keys

# --- FastAPI应用设置 ---

# 初始化FastAPI应用
app = FastAPI(
    title="高效LLM并发中转服务",
    description="使用多个API密钥并发请求LLM，并返回第一个满足条件的响应。",
    version="1.0.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义与OpenAI API兼容的请求体模型
class ChatRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False

# --- 核心并发逻辑 ---

async def send_single_request(client: httpx.AsyncClient, api_key: str, request_data: dict):
    """
    使用单个API密钥发送请求。
    """
    # 清理请求数据，移除Google API不支持的参数
    cleaned_data = {}
    
    # Google API支持的参数
    supported_params = {
        'model', 'messages', 'temperature', 'max_tokens',
        'top_p', 'top_k', 'stop'
    }
    
    # 只保留支持的参数
    for key, value in request_data.items():
        if key in supported_params:
            cleaned_data[key] = value
    
    logger.info(f"清理后的请求参数: {list(cleaned_data.keys())}")
    
    # 构造请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # 构造请求URL
    url = f"{BASE_URL}/openai/chat/completions"

    try:
        logger.info(f"使用密钥 [***{api_key[-4:]}] 发送请求...")
        response = await client.post(url, headers=headers, json=cleaned_data, timeout=REQUEST_TIMEOUT)
        
        response.raise_for_status()
        logger.info(f"密钥 [***{api_key[-4:]}] 收到响应，状态码: {response.status_code}")
        
        response_text = response.text
        
        # 检查是否是流式响应
        if "data:" in response_text:
            logger.info(f"密钥 [***{api_key[-4:]}] 检测到流式响应，转换为标准格式")
            # 解析流式响应
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
                logger.info(f"密钥 [***{api_key[-4:]}] 成功解析流式响应，内容长度: {len(content)}")
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
                                "reasoning_content": "",
                                "tool_calls": []
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
        
        # 尝试解析标准JSON响应
        try:
            json_response = response.json()
            logger.info(f"密钥 [***{api_key[-4:]}] 成功解析标准JSON响应")
            return json_response
        except ValueError as json_error:
            logger.error(f"密钥 [***{api_key[-4:]}] JSON解析失败: {json_error}")
            logger.error(f"密钥 [***{api_key[-4:]}] 原始响应: {response_text}")
            return None
            
    except httpx.HTTPStatusError as e:
        logger.error(f"密钥 [***{api_key[-4:]}] 请求失败 (HTTP状态错误): {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        logger.error(f"密钥 [***{api_key[-4:]}] 请求失败 (网络或连接错误): {e}")
        return None
    except Exception as e:
        logger.error(f"密钥 [***{api_key[-4:]}] 发生未知错误: {e}")
        return None

async def generate_fake_stream_response(request_data: dict):
    """
    获取完整的响应内容，然后以流式方式发送给前端。
    """
    
    # 获取当前应该使用的API密钥组
    current_keys = get_current_api_keys()
    if not current_keys:
        raise HTTPException(
            status_code=500,
            detail="没有可用的API密钥，请检查配置"
        )
    
    logger.info(f"使用第 {2 - current_group_index} 组API密钥进行并发请求")
    
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(send_single_request(client, key, request_data))
            for key in current_keys
        ]

        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                
                if result:
                    if "choices" in result and result["choices"]:
                        message_content = result["choices"][0].get("message", {}).get("content", "")
                        
                        if len(message_content) >= MIN_RESPONSE_LENGTH:
                            logger.info(f"找到满足条件的响应 (长度: {len(message_content)}), 开始流式发送。")
                            
                            for task in tasks:
                                if not task.done():
                                    task.cancel()
                            
                            return await stream_response_content(result, message_content)
                        else:
                            logger.warning(f"收到一个过短的响应 (长度: {len(message_content)}), 已丢弃。")
                    else:
                        logger.warning(f"收到一个格式不正确的响应: {result}")

            except asyncio.CancelledError:
                logger.info("一个任务被成功取消。")
            except Exception as e:
                logger.error(f"处理任务时发生错误: {e}")

    logger.error("所有并发请求均失败或未返回满足条件的结果。")
    raise HTTPException(
        status_code=503,
        detail="所有上游API请求均失败或返回的响应过短，服务暂时不可用。"
    )

async def stream_response_content(result: dict, content: str):
    """
    将完整的响应内容以流式方式发送给前端。
    """
    response_id = result.get("id", f"chatcmpl-{int(time.time())}")
    created_time = result.get("created", int(time.time()))
    model_name = result.get("model", "gemini-2.5-flash")
    
    async def generate_stream():
        # 将内容按字符分割，逐个发送
        chunk_size = max(1, len(content) // 50)  # 分成50个块左右
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            chunk_data = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": chunk
                        },
                        "finish_reason": None
                    }
                ]
            }
            
            yield f"data: {json.dumps(chunk_data)}\n\n"
            await asyncio.sleep(0.01)
        
        final_data = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        
        yield f"data: {json.dumps(final_data)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

# --- API端点定义 ---

@app.post("/v1/chat/completions")
async def chat_completions_proxy(chat_request: ChatRequest, request: Request):
    """
    API密钥认证中间件
    """
    api_key_header = request.headers.get("Authorization")
    
    if not api_key_header or not api_key_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=f"缺少API密钥或格式不正确。请在请求头中添加 Authorization: Bearer {API_KEY}"
        )
    
    provided_key = api_key_header.split(" ")[1]
    if provided_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API密钥无效。"
        )
    
    logger.info("API密钥认证成功")
    return await chat_completions_proxy_handler(chat_request, request)

async def chat_completions_proxy_handler(chat_request: ChatRequest, request: Request):
    """
    代理OpenAI的chat completions端点。
    """
    current_keys = get_current_api_keys()
    if not current_keys:
        raise HTTPException(
            status_code=500,
            detail="服务器未配置有效的API密钥。请使用GUI配置API密钥。"
        )

    request_data = await request.json()

    if chat_request.stream:
        logger.info("检测到流式响应请求，返回流式响应")
        return await generate_fake_stream_response(request_data)

    current_keys = get_current_api_keys()
    logger.info(f"使用第 {2 - current_group_index} 组API密钥进行并发请求")
    
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(send_single_request(client, key, request_data))
            for key in current_keys
        ]

        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                
                if result:
                    if "choices" in result and result["choices"]:
                        message_content = result["choices"][0].get("message", {}).get("content", "")
                        
                        if len(message_content) >= MIN_RESPONSE_LENGTH:
                            logger.info(f"找到满足条件的响应 (长度: {len(message_content)}), 立即返回。")
                            
                            for task in tasks:
                                if not task.done():
                                    task.cancel()
                            
                            return JSONResponse(content=result)
                        else:
                            logger.warning(f"收到一个过短的响应 (长度: {len(message_content)}), 已丢弃。")
                    else:
                        logger.warning(f"收到一个格式不正确的响应: {result}")

            except asyncio.CancelledError:
                logger.info("一个任务被成功取消。")
            except Exception as e:
                logger.error(f"处理任务时发生错误: {e}")

    logger.error("所有并发请求均失败或未返回满足条件的结果。")
    raise HTTPException(
        status_code=503,
        detail="所有上游API请求均失败或返回的响应过短，服务暂时不可用。"
    )

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "message": "LLM并发中转服务正在运行。请向 /v1/chat/completions 发送POST请求。",
        "config": {
            "port": PORT,
            "host": HOST,
            "min_response_length": MIN_RESPONSE_LENGTH,
            "request_timeout": REQUEST_TIMEOUT
        }
    }

@app.get("/health")
def health_check():
    """健康检查端点"""
    current_keys = get_current_api_keys()
    return {
        "status": "healthy",
        "api_keys_count": len(current_keys),
        "config": {
            "port": PORT,
            "host": HOST,
            "min_response_length": MIN_RESPONSE_LENGTH,
            "request_timeout": REQUEST_TIMEOUT
        }
    }

# --- 运行服务器 ---

if __name__ == "__main__":
    print("=" * 50)
    print("LLM代理服务已启动！")
    print(f"访问地址: http://{HOST}:{PORT}")
    print(f"API密钥: {API_KEY}")
    print("使用方法: 在请求头中添加 Authorization: Bearer <API密钥>")
    print("=" * 50)
    
    # 检查是否有有效的API密钥
    current_keys = get_current_api_keys()
    if not current_keys:
        print("警告: 没有配置有效的API密钥，服务可能无法正常工作！")
        print("请使用GUI程序配置API密钥。")
    
    uvicorn.run(app, host=HOST, port=PORT)
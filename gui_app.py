#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM代理服务GUI应用程序
提供图形化界面配置和管理LLM代理服务
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import os
import sys
import signal
import time
from config_manager import config_manager

class LLMProxyGUI:
    """LLM代理服务GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LLM代理服务管理器")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 设置窗口图标（如果有的话）
        try:
            # 尝试使用ICO图标
            self.root.iconbitmap('app_icon.ico')
        except:
            try:
                # 如果ICO文件不存在，尝试使用PNG
                from PIL import Image, ImageTk
                icon_image = Image.open('app_icon.png')
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
            except:
                # 如果都失败，使用默认图标
                pass
        
        # 服务进程
        self.server_process = None
        self.is_running = False
        
        # 创建GUI组件
        self.create_widgets()
        
        # 加载配置
        self.load_config()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 配置标签页
        self.create_basic_config_tab()
        self.create_api_keys_tab()
        self.create_log_tab()
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 启动/停止按钮
        self.start_button = ttk.Button(control_frame, text="启动服务", command=self.toggle_server)
        self.start_button.grid(row=0, column=0, padx=5)
        
        # 保存配置按钮
        save_button = ttk.Button(control_frame, text="保存配置", command=self.save_config)
        save_button.grid(row=0, column=1, padx=5)
        
        # 重置配置按钮
        reset_button = ttk.Button(control_frame, text="重置配置", command=self.reset_config)
        reset_button.grid(row=0, column=2, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("服务未运行")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def create_basic_config_tab(self):
        """创建基础配置标签页"""
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="基础配置")
        
        # 图片显示区域
        try:
            from PIL import Image, ImageTk
            img = Image.open('app_icon.png')
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            self.app_icon = ImageTk.PhotoImage(img)  # 保持引用
            
            icon_label = ttk.Label(basic_frame, image=self.app_icon)
            icon_label.grid(row=0, column=0, pady=(0, 10))
        except:
            # 如果图片加载失败，显示文字
            icon_label = ttk.Label(basic_frame, text="🤖 LLM代理服务", font=("Arial", 16))
            icon_label.grid(row=0, column=0, pady=(0, 10))
        
        # 服务器配置
        server_frame = ttk.LabelFrame(basic_frame, text="服务器配置", padding="10")
        server_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        server_frame.columnconfigure(1, weight=1)
        
        # 端口
        ttk.Label(server_frame, text="端口:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.port_var = tk.StringVar()
        self.port_entry = ttk.Entry(server_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 主机
        ttk.Label(server_frame, text="主机:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.host_var = tk.StringVar()
        self.host_entry = ttk.Entry(server_frame, textvariable=self.host_var)
        self.host_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # API配置
        api_frame = ttk.LabelFrame(basic_frame, text="API配置", padding="10")
        api_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        # 服务API密钥
        ttk.Label(api_frame, text="服务API密钥:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 基础URL
        ttk.Label(api_frame, text="基础URL:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.base_url_var = tk.StringVar()
        self.base_url_entry = ttk.Entry(api_frame, textvariable=self.base_url_var)
        self.base_url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 响应配置
        response_frame = ttk.LabelFrame(basic_frame, text="响应配置", padding="10")
        response_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        response_frame.columnconfigure(1, weight=1)
        
        # 最小响应长度
        ttk.Label(response_frame, text="最小响应字符数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.min_length_var = tk.StringVar()
        self.min_length_entry = ttk.Entry(response_frame, textvariable=self.min_length_var, width=10)
        self.min_length_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 请求超时时间
        ttk.Label(response_frame, text="请求超时时间(秒):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.timeout_var = tk.StringVar()
        self.timeout_entry = ttk.Entry(response_frame, textvariable=self.timeout_var, width=10)
        self.timeout_entry.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
    
    def create_api_keys_tab(self):
        """创建API密钥管理标签页"""
        keys_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(keys_frame, text="API密钥管理")
        
        # 配置网格权重
        keys_frame.columnconfigure(0, weight=1)
        keys_frame.rowconfigure(1, weight=1)
        
        # 第一组密钥
        group1_frame = ttk.LabelFrame(keys_frame, text="第一组API密钥", padding="10")
        group1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        group1_frame.columnconfigure(0, weight=1)
        group1_frame.rowconfigure(0, weight=1)
        
        self.group1_text = scrolledtext.ScrolledText(group1_frame, height=8, width=50)
        self.group1_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 第二组密钥
        group2_frame = ttk.LabelFrame(keys_frame, text="第二组API密钥", padding="10")
        group2_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        group2_frame.columnconfigure(0, weight=1)
        group2_frame.rowconfigure(0, weight=1)
        
        self.group2_text = scrolledtext.ScrolledText(group2_frame, height=8, width=50)
        self.group2_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 按钮框架
        button_frame = ttk.Frame(keys_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        # 导入按钮
        import_button = ttk.Button(button_frame, text="从文件导入", command=self.import_keys)
        import_button.grid(row=0, column=0, padx=5)
        
        # 导出按钮
        export_button = ttk.Button(button_frame, text="导出到文件", command=self.export_keys)
        export_button.grid(row=0, column=1, padx=5)
        
        # 清空按钮
        clear_button = ttk.Button(button_frame, text="清空所有", command=self.clear_keys)
        clear_button.grid(row=0, column=2, padx=5)
    
    def create_log_tab(self):
        """创建日志标签页"""
        log_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(log_frame, text="运行日志")
        
        # 配置网格权重
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=20, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志控制按钮
        button_frame = ttk.Frame(log_frame)
        button_frame.grid(row=1, column=0, pady=(10, 0))
        
        clear_log_button = ttk.Button(button_frame, text="清空日志", command=self.clear_log)
        clear_log_button.grid(row=0, column=0, padx=5)
        
        save_log_button = ttk.Button(button_frame, text="保存日志", command=self.save_log)
        save_log_button.grid(row=0, column=1, padx=5)
    
    def load_config(self):
        """加载配置到界面"""
        try:
            # 加载服务器配置
            server_config = config_manager.get_server_config()
            self.port_var.set(str(server_config['port']))
            self.host_var.set(server_config['host'])
            self.api_key_var.set(server_config['api_key'])
            self.min_length_var.set(str(server_config['min_response_length']))
            self.timeout_var.set(str(server_config['request_timeout']))
            
            # 加载基础URL
            self.base_url_var.set(config_manager.get_base_url())
            
            # 加载API密钥
            api_keys = config_manager.get_api_keys()
            self.group1_text.delete(1.0, tk.END)
            self.group1_text.insert(1.0, '\n'.join(api_keys['group1']))
            self.group2_text.delete(1.0, tk.END)
            self.group2_text.insert(1.0, '\n'.join(api_keys['group2']))
            
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
    
    def save_config(self):
        """保存配置"""
        try:
            # 验证输入
            port = int(self.port_var.get())
            if not (1 <= port <= 65535):
                raise ValueError("端口必须在1-65535之间")
            
            min_length = int(self.min_length_var.get())
            if min_length < 0:
                raise ValueError("最小响应长度不能为负数")
            
            timeout = int(self.timeout_var.get())
            if timeout <= 0:
                raise ValueError("超时时间必须大于0")
            
            # 保存服务器配置
            config_manager.set_server_config(
                port=port,
                host=self.host_var.get(),
                api_key=self.api_key_var.get(),
                min_response_length=min_length,
                request_timeout=timeout
            )
            
            # 保存基础URL
            config_manager.set_base_url(self.base_url_var.get())
            
            # 保存API密钥
            group1_keys = [key.strip() for key in self.group1_text.get(1.0, tk.END).split('\n') if key.strip()]
            group2_keys = [key.strip() for key in self.group2_text.get(1.0, tk.END).split('\n') if key.strip()]
            config_manager.set_api_keys(group1_keys, group2_keys)
            
            messagebox.showinfo("成功", "配置已保存")
            
        except ValueError as e:
            messagebox.showerror("错误", f"配置保存失败: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置时发生错误: {str(e)}")
    
    def reset_config(self):
        """重置配置为默认值"""
        if messagebox.askyesno("确认", "确定要重置所有配置为默认值吗？"):
            try:
                # 删除配置文件
                if os.path.exists("config.ini"):
                    os.remove("config.ini")
                
                # 重新创建默认配置
                global config_manager
                config_manager = ConfigManager()
                
                # 重新加载配置
                self.load_config()
                messagebox.showinfo("成功", "配置已重置为默认值")
                
            except Exception as e:
                messagebox.showerror("错误", f"重置配置失败: {str(e)}")
    
    def toggle_server(self):
        """启动/停止服务"""
        if not self.is_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """启动服务"""
        try:
            # 保存当前配置
            self.save_config()
            
            # 启动服务
            self.server_process = subprocess.Popen([
                sys.executable, "llm_proxy.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.is_running = True
            self.start_button.config(text="停止服务")
            self.status_var.set("服务运行中...")
            
            # 启动日志线程
            self.log_thread = threading.Thread(target=self.update_log, daemon=True)
            self.log_thread.start()
            
            messagebox.showinfo("成功", "服务已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动服务失败: {str(e)}")
    
    def stop_server(self):
        """停止服务"""
        try:
            if self.server_process:
                # 终止进程
                if os.name == 'nt':  # Windows
                    self.server_process.terminate()
                else:  # Unix
                    self.server_process.send_signal(signal.SIGTERM)
                
                # 等待进程结束
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                
                self.server_process = None
            
            self.is_running = False
            self.start_button.config(text="启动服务")
            self.status_var.set("服务已停止")
            
            messagebox.showinfo("成功", "服务已停止")
            
        except Exception as e:
            messagebox.showerror("错误", f"停止服务失败: {str(e)}")
    
    def update_log(self):
        """更新日志显示"""
        if self.server_process:
            while self.is_running:
                try:
                    # 读取输出
                    line = self.server_process.stdout.readline()
                    if line:
                        self.log_text.config(state='normal')
                        self.log_text.insert(tk.END, line)
                        self.log_text.see(tk.END)
                        self.log_text.config(state='disabled')
                    
                    # 读取错误
                    error_line = self.server_process.stderr.readline()
                    if error_line:
                        self.log_text.config(state='normal')
                        self.log_text.insert(tk.END, f"ERROR: {error_line}", 'error')
                        self.log_text.tag_config('error', foreground='red')
                        self.log_text.see(tk.END)
                        self.log_text.config(state='disabled')
                        
                except Exception:
                    break
    
    def import_keys(self):
        """从文件导入API密钥"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="选择API密钥文件",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    keys = [line.strip() for line in f if line.strip()]
                
                # 根据当前标签页决定导入到哪一组
                current_tab = self.notebook.tab(self.notebook.select(), "text")
                
                if "第一组" in current_tab:
                    self.group1_text.delete(1.0, tk.END)
                    self.group1_text.insert(1.0, '\n'.join(keys))
                elif "第二组" in current_tab:
                    self.group2_text.delete(1.0, tk.END)
                    self.group2_text.insert(1.0, '\n'.join(keys))
                
                messagebox.showinfo("成功", f"已导入 {len(keys)} 个API密钥")
                
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def export_keys(self):
        """导出API密钥到文件"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="保存API密钥文件",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                # 获取当前标签页的内容
                current_tab = self.notebook.tab(self.notebook.select(), "text")
                
                if "第一组" in current_tab:
                    keys = self.group1_text.get(1.0, tk.END).strip()
                elif "第二组" in current_tab:
                    keys = self.group2_text.get(1.0, tk.END).strip()
                else:
                    # 导出所有密钥
                    group1 = self.group1_text.get(1.0, tk.END).strip()
                    group2 = self.group2_text.get(1.0, tk.END).strip()
                    keys = f"第一组密钥:\n{group1}\n\n第二组密钥:\n{group2}"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(keys)
                
                messagebox.showinfo("成功", "API密钥已导出")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def clear_keys(self):
        """清空API密钥"""
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            
            if messagebox.askyesno("确认", f"确定要清空{current_tab}的所有API密钥吗？"):
                if "第一组" in current_tab:
                    self.group1_text.delete(1.0, tk.END)
                elif "第二组" in current_tab:
                    self.group2_text.delete(1.0, tk.END)
                
                messagebox.showinfo("成功", "API密钥已清空")
                
        except Exception as e:
            messagebox.showerror("错误", f"清空失败: {str(e)}")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def save_log(self):
        """保存日志到文件"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="保存日志文件",
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                log_content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                messagebox.showinfo("成功", "日志已保存")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存日志失败: {str(e)}")
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            if messagebox.askyesno("确认", "服务正在运行，确定要关闭程序吗？"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = LLMProxyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
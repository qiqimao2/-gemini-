// LLM代理服务 - Web版 JavaScript

class LLMProxyApp {
    constructor() {
        this.socket = null;
        this.currentConfig = null;
        this.init();
    }

    init() {
        this.initSocket();
        this.initEventListeners();
        this.loadConfig();
        this.updateWebUrl();
    }

    initSocket() {
        // 连接Socket.IO
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Socket连接成功');
            this.showNotification('连接成功', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Socket连接断开');
            this.showNotification('连接断开', 'error');
        });

        this.socket.on('server_status', (data) => {
            this.updateServerStatus(data);
        });
    }

    initEventListeners() {
        // 侧边栏导航
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(link.dataset.tab);
            });
        });

        // 按钮事件
        document.getElementById('save-config-btn').addEventListener('click', () => {
            this.saveConfig();
        });

        document.getElementById('reload-config-btn').addEventListener('click', () => {
            this.loadConfig();
        });

        document.getElementById('start-server-btn').addEventListener('click', () => {
            this.startServer();
        });

        document.getElementById('stop-server-btn').addEventListener('click', () => {
            this.stopServer();
        });

        // 实时配置更新
        this.setupRealTimeConfigUpdate();
    }

    setupRealTimeConfigUpdate() {
        // 为所有配置输入框添加实时更新事件
        const configInputs = [
            'api-port', 'api-host', 'web-port', 'web-host',
            'api-key', 'min-length', 'timeout', 'base-url',
            'group1-keys', 'group2-keys'
        ];

        configInputs.forEach(inputId => {
            const element = document.getElementById(inputId);
            if (element) {
                element.addEventListener('input', () => {
                    this.debounce(this.saveConfig.bind(this), 1000)();
                });
            }
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async switchTab(tabName) {
        // 更新导航状态
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 切换内容
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (!response.ok) {
                throw new Error('加载配置失败');
            }

            const data = await response.json();
            this.currentConfig = data;
            this.updateConfigUI(data);
            this.showNotification('配置加载成功', 'success');
        } catch (error) {
            console.error('加载配置失败:', error);
            this.showNotification('加载配置失败: ' + error.message, 'error');
        }
    }

    updateConfigUI(data) {
        // 更新服务器配置
        if (data.server) {
            document.getElementById('api-port').value = data.server.port;
            document.getElementById('api-host').value = data.server.host;
            document.getElementById('web-port').value = data.server.web_port;
            document.getElementById('web-host').value = data.server.web_host;
            document.getElementById('api-key').value = data.server.api_key;
            document.getElementById('min-length').value = data.server.min_response_length;
            document.getElementById('timeout').value = data.server.request_timeout;
        }

        // 更新基础URL
        if (data.base_url) {
            document.getElementById('base-url').value = data.base_url;
        }

        // 更新API密钥
        if (data.api_keys) {
            document.getElementById('group1-keys').value = data.api_keys.group1.join('\n');
            document.getElementById('group2-keys').value = data.api_keys.group2.join('\n');
        }
    }

    async saveConfig() {
        try {
            const config = this.getConfigFromUI();
            
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error('保存配置失败');
            }

            const result = await response.json();
            if (result.success) {
                this.showNotification('配置保存成功', 'success');
                this.currentConfig = config;
            } else {
                throw new Error(result.error || '保存配置失败');
            }
        } catch (error) {
            console.error('保存配置失败:', error);
            this.showNotification('保存配置失败: ' + error.message, 'error');
        }
    }

    getConfigFromUI() {
        return {
            server: {
                port: parseInt(document.getElementById('api-port').value),
                host: document.getElementById('api-host').value,
                web_port: parseInt(document.getElementById('web-port').value),
                web_host: document.getElementById('web-host').value,
                api_key: document.getElementById('api-key').value,
                min_response_length: parseInt(document.getElementById('min-length').value),
                request_timeout: parseInt(document.getElementById('timeout').value)
            },
            api_keys: {
                group1: document.getElementById('group1-keys').value
                    .split('\n')
                    .map(key => key.trim())
                    .filter(key => key.length > 0),
                group2: document.getElementById('group2-keys').value
                    .split('\n')
                    .map(key => key.trim())
                    .filter(key => key.length > 0)
            },
            base_url: document.getElementById('base-url').value
        };
    }

    async startServer() {
        try {
            this.setButtonLoading('start-server-btn', true);
            
            const response = await fetch('/api/server/start', {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('启动服务器失败');
            }

            const result = await response.json();
            if (result.success) {
                this.showNotification('API服务器启动成功', 'success');
                this.updateServerButtons(true);
            } else {
                throw new Error(result.error || '启动服务器失败');
            }
        } catch (error) {
            console.error('启动服务器失败:', error);
            this.showNotification('启动服务器失败: ' + error.message, 'error');
        } finally {
            this.setButtonLoading('start-server-btn', false);
        }
    }

    async stopServer() {
        try {
            this.setButtonLoading('stop-server-btn', true);
            
            const response = await fetch('/api/server/stop', {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('停止服务器失败');
            }

            const result = await response.json();
            if (result.success) {
                this.showNotification('API服务器停止成功', 'success');
                this.updateServerButtons(false);
            } else {
                throw new Error(result.error || '停止服务器失败');
            }
        } catch (error) {
            console.error('停止服务器失败:', error);
            this.showNotification('停止服务器失败: ' + error.message, 'error');
        } finally {
            this.setButtonLoading('stop-server-btn', false);
        }
    }

    updateServerStatus(data) {
        const statusIndicator = document.getElementById('status-indicator');
        const apiStatus = document.getElementById('api-status');
        const apiUrl = document.getElementById('api-url');

        if (data.status === 'running') {
            statusIndicator.className = 'badge bg-success';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> 服务运行中';
            
            apiStatus.className = 'badge bg-success';
            apiStatus.textContent = '运行中';
            
            if (data.url) {
                apiUrl.textContent = data.url;
            }
            
            this.updateServerButtons(true);
        } else {
            statusIndicator.className = 'badge bg-secondary';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> 服务未运行';
            
            apiStatus.className = 'badge bg-secondary';
            apiStatus.textContent = '未运行';
            
            apiUrl.textContent = '-';
            
            this.updateServerButtons(false);
        }
    }

    updateServerButtons(isRunning) {
        const startBtn = document.getElementById('start-server-btn');
        const stopBtn = document.getElementById('stop-server-btn');

        startBtn.disabled = isRunning;
        stopBtn.disabled = !isRunning;
    }

    updateWebUrl() {
        const webUrl = document.getElementById('web-url');
        if (webUrl) {
            const protocol = window.location.protocol;
            const host = window.location.host;
            webUrl.textContent = `${protocol}//${host}`;
        }
    }

    setButtonLoading(buttonId, isLoading) {
        const button = document.getElementById(buttonId);
        if (isLoading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.dataset.originalText = originalText;
            button.innerHTML = '<span class="loading"></span> 处理中...';
        } else {
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
            }
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        // 显示通知
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // 自动隐藏
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.llmProxyApp = new LLMProxyApp();
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (window.llmProxyApp && window.llmProxyApp.socket) {
        window.llmProxyApp.socket.disconnect();
    }
});
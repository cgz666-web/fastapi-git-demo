from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


# 存储活跃的WebSocket连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # 向所有连接的客户端广播消息
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# 提供前端页面
@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI WebSocket 交互演示</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }
        body {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .container {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        .header {
            background: #007bff;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
        }
        .message {
            margin: 0.5rem 0;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            max-width: 70%;
        }
        .server-message {
            background: #e9ecef;
            align-self: flex-start;
        }
        .client-message {
            background: #007bff;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        .input-area {
            display: flex;
            padding: 1rem;
            border-top: 1px solid #ddd;
        }
        #message-input {
            flex: 1;
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            border-radius: 4px 0 0 4px;
            outline: none;
        }
        #message-input:focus {
            border-color: #007bff;
        }
        #send-btn {
            padding: 0.5rem 1.5rem;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 0 4px 4px 0;
            cursor: pointer;
        }
        #send-btn:hover {
            background: #0056b3;
        }
        .status {
            text-align: center;
            margin: 1rem 0;
            color: #6c757d;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // 生成随机客户端ID
            const clientId = `user-${Math.floor(Math.random() * 1000)}`;
            document.getElementById('client-id').textContent = clientId;

            // WebSocket 连接：匹配后端 /ws/{client_id} 路径
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/${clientId}`);

            // DOM 元素
            const chatBox = document.getElementById('chat-box');
            const messageInput = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');
            const statusText = document.getElementById('status');

            // 连接成功
            ws.onopen = () => {
                statusText.textContent = '✅ 已连接到服务器';
                statusText.style.color = 'green';
            };

            // 接收消息
            ws.onmessage = (event) => {
                addMessage(event.data, 'server');
            };

            // 连接关闭/错误
            ws.onclose = () => {
                statusText.textContent = '❌ 与服务器断开连接';
                statusText.style.color = 'red';
            };
            ws.onerror = (error) => {
                console.error('WebSocket 错误:', error);
                statusText.textContent = '❌ WebSocket 连接出错';
                statusText.style.color = 'red';
            };

            // 发送消息
            const sendMessage = () => {
                const message = messageInput.value.trim();
                if (!message) return;

                // 发送到服务器
                ws.send(message);
                // 显示自己的消息
                addMessage(message, 'client');
                // 清空输入框
                messageInput.value = '';
            };

            // 添加消息到聊天框
            const addMessage = (text, type) => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type === 'server' ? 'server-message' : 'client-message'}`;
                messageDiv.textContent = text;
                chatBox.appendChild(messageDiv);
                // 滚动到底部
                chatBox.scrollTop = chatBox.scrollHeight;
            };

            // 绑定事件
            sendBtn.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FastAPI WebSocket 实时交互</h1>
            <p>客户端ID: <span id="client-id"></span></p>
        </div>
        <div id="chat-box" class="chat-box"></div>
        <div class="input-area">
            <input type="text" id="message-input" placeholder="输入消息并发送...">
            <button id="send-btn">发送</button>
        </div>
    </div>
    <div class="status" id="status">🔄 正在连接服务器...</div>
</body>
</html>
    """)


# WebSocket 端点：路径为 /ws/{client_id}，匹配前端请求
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        # 发送欢迎消息（包含客户端ID）
        await websocket.send_text(f"欢迎 {client_id} 连接到WebSocket服务！请发送消息...")
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            # 广播消息（带客户端ID）
            await manager.broadcast(f"{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} 断开了连接")
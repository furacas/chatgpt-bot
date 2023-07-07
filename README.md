# ChatGPT Bot

ChatGPT聊天机器人

## 支持列表

- 钉钉机器人
- 微信

## 安装步骤

### Docker

```bash
docker run -p 8000:8000 --restart always --name chat -v ~/.app/chat/db:/app/db -e PANDORA_SERVER_URL=http://pandora:1024 -e WE_SERVICE=wechat_service furacas/chatgpt-bot:latest
```

其中`PANDORA_SERVER_URL`可以参考 https://github.com/pengzhile/pandora  
其中`WE_SERVICE`可以参考 https://github.com/ChisBread/wechat-service

# ChatGPT Bot

ChatGPT聊天机器人

## 支持列表

- 钉钉机器人
- 微信
- QQ

## 安装步骤

### Docker

```bash
docker run -p 8000:8000 --restart always --name chat -v ~/.app/chat/db:/app/db -e PANDORA_SERVER_URL=http://pandora:1024 furacas/chatgpt-bot:latest
```

环境变量

| 环境变量            | 是否可选     | 详情                                                                       |
|-----------------|----------|--------------------------------------------------------------------------|
| PANDORA_SERVER_URL | Required | [Pandora GitHub](https://github.com/pengzhile/pandora)                   |
| WE_SERVICE      | Optional | [WeChat Service GitHub](https://github.com/ChisBread/wechat-service)     |
| QQ_SERVICE      | Optional | [Mirai API HTTP GitHub](https://github.com/project-mirai/mirai-api-http) |
| QQ_NUM          | Optional | Bot QQ号                                                                  |

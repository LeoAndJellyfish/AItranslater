# AItranslater
翻译工具，分为本地与api两种模式。能自定义翻译命令。

[在线体验(仅支持api模式 )](https://aitranslater-jellyfish.streamlit.app/)

# 本地模式使用模型
Helsinki-NLP/opus-mt-zh-en

Helsinki-NLP/opus-mt-en-zh

# API模式
支持openai格式的api接口。

// 调试 streamlit run web.py --server.address 127.0.0.1 --server.port 6006 

# 本地部署（不再更新）

## 安装环境
```
pip install -r requirements.txt
```

## 启动
```
streamlit run app.py --server.address 127.0.0.1 --server.port 6006
```

# TODO
- [x] 新增账号密码登录功能
- [x] 优化界面
- [x] 区分任务要求与翻译文本
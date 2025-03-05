12|
13|# 加密货币相关性监控系统
14|## 安装说明
15|```bash
16|# 克隆仓库
17|git clone https://github.com/yourusername/trad-program.git
18|
19|# 手动配置步骤：
20|1. 前往 GitHub 官网创建名为 'trad-program' 的新仓库
21|2. 设置本地Git配置（在项目目录执行）：
22|git config user.email "您的邮箱"
23|git config user.name "您的用户名"
24|3. 关联远程仓库：
25|git remote add origin https://github.com/您的用户名/trad-program.git
26|4. 推送代码到仓库：
27|git push -u origin main
28|```
29|# 安装依赖
30|pip install -r requirements.txt
31|# 配置环境变量
32|cp .env.example .env
```

## 配置说明
1. 在`.env`文件中添加：
```
TELEGRAM_TOKEN=你的机器人token
TELEGRAM_CHAT_ID=你的聊天ID
```
2. 通过[BotFather](https://t.me/BotFather)创建Telegram机器人

## 运行系统
```bash
python main.py
```

## 文件结构
```
├── main.py          # 主程序
├── requirements.txt # 依赖库
├── .env.example     # 环境变量示例
└── README.md        # 说明文档
```
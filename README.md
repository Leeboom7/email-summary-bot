# 个人AI邮件总结助手 (Email Summary Bot)

这是一个基于GitHub Actions的自动化工具，它能每日定时读取你指定的邮箱文件夹，使用**DeepSeek**的语言模型进行智能总结，并将一份邮件汇总报告发送到你的另一个邮箱。

## ✨ 特点

- **完全自动化**：每日定时运行，无需人工干预。
- **免费运行**：充分利用GitHub Actions的免费额度。
- **高度安全**：所有敏感信息均存储在GitHub的加密Secrets中。
- **高度可定制**：你可以自由修改Python代码和`SYSTEM_PROMPT`。
- **无需服务器**：你不需要购买或维护任何服务器。

## 🚀 配置步骤

**1. Fork本仓库**

点击仓库右上角的 "Fork" 按钮，将本仓库复制到你自己的GitHub账户下。

**2. 准备你的凭据**

你需要准备好以下信息：

- **① 用于读取的邮箱 (IMAP)**
    - `IMAP_EMAIL`: 你的邮箱地址。
    - `IMAP_AUTH_CODE`: 上述邮箱的IMAP授权码。
    - `IMAP_SERVER`: 你邮箱的IMAP服务器地址 (例如 `imap.qq.com`)。

- **② DeepSeek API密钥**
    - `DEEPSEEK_API_KEY`: 前往 [DeepSeek开放平台](https://platform.deepseek.com/api_keys) 创建你的API密钥。

- **③ 用于发送总结报告的邮箱 (SMTP)**
    - `SENDER_EMAIL`: 用于发送报告的邮箱。
    - `SENDER_AUTH_CODE`: 上述发件邮箱的SMTP授权码。
    - `RECEIVER_EMAIL`: 你希望接收总结报告的邮箱地址。
    - `SMTP_SERVER`: 发件邮箱的SMTP服务器地址 (例如 `smtp.qq.com`)。
    - `SMTP_PORT`: SMTP服务器的SSL端口 (例如 `465`)。

- **④ 目标文件夹**
    - `TARGET_FOLDER`: 运行 `find_folders.py` 脚本来找到它的“真实名称”。
      1. 在你的电脑上安装Python。
      2. 下载本仓库中的 `find_folders.py`。
      3. 在终端中运行 `python find_folders.py`，并按提示操作。
      4. 脚本会打印出你所有的邮箱文件夹。找到你需要的文件夹，**完整地复制它引号内的那部分** (例如 `&UXZO1mWHTvZZOQ-/HKU`)。

**3. 在GitHub中设置Secrets**

1.  在你Fork的仓库页面，点击 `Settings` -> `Secrets and variables` -> `Actions`。
2.  点击 `New repository secret`，依次创建以下**所有**Secrets：
    - `IMAP_EMAIL`
    - `IMAP_AUTH_CODE`
    - `IMAP_SERVER`
    - `TARGET_FOLDER`
    - `DEEPSEEK_API_KEY`
    - `SENDER_EMAIL`
    - `SENDER_AUTH_CODE`
    - `RECEIVER_EMAIL`
    - `SMTP_SERVER`
    - `SMTP_PORT`

**4. 启用并测试GitHub Actions**

1.  点击仓库顶部的 `Actions` 标签页。
2.  如有提示，请点击 "I understand my workflows, go ahead and enable them"。
3.  在左侧，点击 "Daily Email Summary" 工作流。
4.  在右侧，点击 "Run workflow" 下拉按钮，然后点击绿色的 "Run workflow" 按钮来手动触发一次任务。
5.  你可以点击运行记录，实时查看任务的执行日志。如果一切顺利，几分钟后你的收件箱就会收到第一封总结报告。

---

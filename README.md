# 个人AI邮件总结助手 (Email Summary Bot)

这是一个基于GitHub Actions的自动化工具，它能每日定时读取你指定的邮箱文件夹，使用OpenAI的GPT模型进行智能总结，并将一份精美的纯文本报告发送到你的另一个邮箱。

## ✨ 特点

- **完全自动化**：每日定时运行，无需人工干预。
- **免费运行**：充分利用GitHub Actions的免费额度。
- **高度安全**：所有敏感信息（如密码、API密钥）均存储在GitHub的加密Secrets中，代码中不包含任何个人凭据。
- **高度可定制**：你可以自由修改Python代码和`SYSTEM_PROMPT`来满足你的个性化需求。
- **无需服务器**：你不需要购买或维护任何服务器。

## 🚀 配置步骤

**1. Fork本仓库**

点击仓库右上角的 "Fork" 按钮，将本仓库复制到你自己的GitHub账户下。接下来的所有操作都在你Fork后的仓库中进行。

**2. 准备你的凭据**

在开始配置之前，你需要准备好以下信息。请将它们保存在一个临时的地方。

- **① 用于读取的邮箱 (IMAP)**
    - `IMAP_EMAIL`: 你的邮箱地址，例如 `your_forwarding_target@qq.com`。
    - `IMAP_AUTH_CODE`: 上述邮箱的IMAP授权码。请参考你邮箱服务商的官方教程获取。
    - `IMAP_SERVER`: 你邮箱的IMAP服务器地址，例如 `imap.qq.com`。

- **② OpenAI API密钥**
    - `OPENAI_API_KEY`: 前往 [OpenAI官网](https://platform.openai.com/api-keys) 创建你的API密钥。**注意：调用API会产生少量费用。**

- **③ 用于发送总结报告的邮箱 (SMTP)**
    - `SENDER_EMAIL`: 用于发送报告的邮箱，可以和读取的邮箱是同一个。
    - `SENDER_AUTH_CODE`: 上述发件邮箱的SMTP授权码（通常和IMAP授权码是同一个）。
    - `RECEIVER_EMAIL`: 你希望接收总结报告的邮箱地址。
    - `SMTP_SERVER`: 发件邮箱的SMTP服务器地址，例如 `smtp.qq.com`。
    - `SMTP_PORT`: SMTP服务器的SSL端口，例如 `465` (QQ邮箱)。

- **④ 目标文件夹**
    - `TARGET_FOLDER`: 这是最关键的一步。由于不同邮箱的文件夹路径编码不同，你需要运行一个脚本来找到它的“真实名称”。
      1. 在你的电脑上，确保已安装Python。
      2. 将本仓库中的 `find_folders.py` 文件下载到你的电脑上。
      3. 打开终端（命令提示符），进入 `find_folders.py` 所在的目录。
      4. 运行命令 `python find_folders.py`。
      5. 根据提示，依次输入你的**读取邮箱地址**、**IMAP授权码**和**IMAP服务器地址**。
      6. 脚本会打印出你所有的邮箱文件夹。找到你设置了邮件转发规则的那个文件夹（例如，你创建的`HKU`文件夹），**完整地复制它引号内的那部分**，它可能看起来像 `&UXZO1mWHTvZZOQ-/HKU`。这就是你的`TARGET_FOLDER`的值。

**3. 在GitHub中设置Secrets**

1.  在你Fork的仓库页面，点击 `Settings` -> `Secrets and variables` -> `Actions`。
2.  点击 `New repository secret`，依次创建以下**所有**Secrets，将你上一步获取到的值粘贴进去：
    - `IMAP_EMAIL`
    - `IMAP_AUTH_CODE`
    - `IMAP_SERVER`
    - `TARGET_FOLDER`
    - `OPENAI_API_KEY`
    - `SENDER_EMAIL`
    - `SENDER_AUTH_CODE`
    - `RECEIVER_EMAIL`
    - `SMTP_SERVER`
    - `SMTP_PORT`

**4. 启用并测试GitHub Actions**

1.  点击仓库顶部的 `Actions` 标签页。
2.  如果看到一个黄色的提示条，请点击 "I understand my workflows, go ahead and enable them"。
3.  在左侧，点击 "Daily Email Summary" 工作流。
4.  在右侧，你会看到一个 "Run workflow" 的下拉按钮，点击它，然后点击绿色的 "Run workflow" 按钮。
5.  这会立即手动触发一次任务。你可以点击运行记录，实时查看任务的执行日志，检查是否有报错。如果一切顺利，几分钟后你的收件箱就会收到第一封总结报告！

**5. （可选）修改运行时间**

默认的运行时间是每天UTC时间10:00（北京时间18:00）。你可以通过修改 `.github/workflows/main.yml` 文件中的`cron`表达式来调整为你需要的时间。

---

**大功告成！** 你的个人AI邮件助手已经配置完毕，将从设定的时间开始为你服务。
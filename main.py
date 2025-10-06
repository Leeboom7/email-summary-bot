# main.py

# ==============================================================================
# 导入必要的库
# ==============================================================================
import os
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import openai
import json
import markdown2

# ==============================================================================
# 全局常量与配置
# ==============================================================================

# SYSTEM_PROMPT: 定义了与大语言模型交互的核心指令。
# 使用Markdown格式是因为它对LLM更友好，且在Prompt中易于阅读和维护。
# {{emails}} 是一个占位符，将在运行时被真实的邮件数据替换。
SYSTEM_PROMPT = """
# 角色
你是一名专业的邮件分析助手，专注于从结构化邮件数据中提取关键信息，生成**Markdown格式**的邮件摘要报告。

# 目标
基于提供的邮件JSON数据，生成清晰简洁的**Markdown格式**邮件摘要报告，帮助用户快速了解邮件核心内容和需要采取的行动。

# 任务指令
1. 仔细阅读提供的邮件JSON数据。
2. 精确统计邮件的总数量。
3. 按顺序逐一处理每一封邮件，并为每封邮件提取以下信息：
   - **发件人**：提取发件人的姓名或邮箱地址。
   - **主题**：直接使用邮件的原主题。
   - **摘要**：用1-2句话概括邮件的核心内容和主要信息。
   - **关键行动点**：识别邮件中要求执行的具体任务，如果没有明确的行动点，则填写"无"。

# 输出格式要求
生成**Markdown格式**的报告，使用以下结构：

### 每日邮件汇总
**总览：共 [AI计算出的总邮件数] 封邮件**

---

#### 邮件 1：[邮件主题]
- **发件人**：[发件人信息]
- **摘要**：[用1-2句话简洁概括]
- **行动点**：[具体行动或"信息性邮件，无需行动"]

---

#### 邮件 2：[邮件主题]
- **发件人**：[发件人信息]
- **摘要**：[用1-2句话简洁概括]
- **行动点**：[具体行动或"信息性邮件，无需行动"]

---
... (继续所有邮件)

# 特别说明
- 语言：使用简体中文。
- 简洁性：摘要和行动点必须精炼。
- 客观性：严格基于邮件内容进行总结。
- 社团邮件标记：如果邮件内容明显是关于社团、学生会组织的活动通知，请在邮件主题的末尾添加标签 `[社团邮件]`。
- 忽略广告和垃圾邮件：如是明显广告或系统通知，在摘要中注明类型，行动点标记为"无"。

# 待分析的邮件数据
{{emails}}
"""

# 从GitHub Secrets安全地加载环境变量
IMAP_EMAIL = os.environ.get("IMAP_EMAIL")
IMAP_AUTH_CODE = os.environ.get("IMAP_AUTH_CODE")
IMAP_SERVER = os.environ.get("IMAP_SERVER")
TARGET_FOLDER = os.environ.get("TARGET_FOLDER")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_AUTH_CODE = os.environ.get("SENDER_AUTH_CODE")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587)) # 默认使用587端口，兼容性最好

# ==============================================================================
# 核心功能函数
# ==============================================================================

def get_emails_from_target_date(target_date):
    """
    通过IMAP连接到邮箱，获取指定日期的邮件。

    为了解决特定IMAP服务器对日期查询不准的问题，本函数采用“客户端过滤”策略：
    1. 向服务器请求一个比目标日期稍大的范围（例如，从昨天开始）。
    2. 在本地代码中，精确解析每封邮件的Date头，只保留日期完全匹配的邮件。

    Args:
        target_date (datetime.datetime): 目标日期。

    Returns:
        list: 一个包含邮件信息的字典列表，每个字典代表一封邮件。
    """
    mail_list = []
    try:
        conn = imaplib.IMAP4_SSL(IMAP_SERVER)
        conn.login(IMAP_EMAIL, IMAP_AUTH_CODE)
        conn.select(f'"{TARGET_FOLDER}"')
        
        fetch_since_dt = target_date - timedelta(days=1)
        fetch_since_str = fetch_since_dt.strftime("%d-%b-%Y")
        search_query = f'(SINCE "{fetch_since_str}")'
        
        status, messages = conn.search(None, search_query)
        if status != "OK":
            print(f"IMAP search failed for query: {search_query}")
            conn.logout()
            return []
            
        email_ids = messages[0].split()
        
        for email_id in reversed(email_ids):
            _, msg_data = conn.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            try:
                date_header = msg.get("Date")
                if not date_header: continue
                
                email_dt = parsedate_to_datetime(date_header)
                
                if email_dt.date() != target_date.date():
                    continue

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes): subject = subject.decode(encoding if encoding else "utf-8")

                from_, encoding = decode_header(msg.get("From"))[0]
                if isinstance(from_, bytes): from_ = from_.decode(encoding if encoding else "utf-8")

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try: body = part.get_payload(decode=True).decode(); break
                            except: continue
                else:
                    try: body = msg.get_payload(decode=True).decode()
                    except: body = "无法解码正文。"
                
                mail_list.append({ "from_sender": from_, "subject": subject, "body_preview": body[:1500] })
            except Exception as e:
                print(f"解析邮件 {email_id.decode()} 时出错: {e}")
                continue
                
        conn.logout()
        print(f"成功从'{TARGET_FOLDER}'文件夹获取并过滤出 {len(mail_list)} 封邮件。")
        return mail_list
    except Exception as e:
        print(f"获取邮件失败: {e}")
        return []

def summarize_with_llm(email_list):
    """
    调用DeepSeek API对邮件列表进行总结。

    Args:
        email_list (list): 从get_emails_from_target_date获取的邮件列表。

    Returns:
        str: 由大模型生成的Markdown格式的总结报告。
    """
    if not email_list:
        return "### 每日邮件汇总\n**总览：共 0 封邮件**\n\n--- \n\n今日没有收到新邮件。"
        
    client = openai.OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    
    emails_json_str = json.dumps(email_list, ensure_ascii=False, indent=2)
    prompt_filled = SYSTEM_PROMPT.replace("{{emails}}", emails_json_str)
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": prompt_filled}]
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"调用DeepSeek API失败: {e}")
        return f"### 生成邮件摘要失败\n\n**错误详情**:\n`{e}`"

def send_email_notification(summary_md):
    """
    将Markdown格式的总结报告转换为HTML，并通过SMTP (STARTTLS) 发送邮件。
    使用最简化的邮件头以确保最高的兼容性。
    """
    if not SENDER_EMAIL or not SENDER_AUTH_CODE or not RECEIVER_EMAIL:
        print("发送邮件所需的环境变量不完整，跳过发送。")
        return

    # 将Markdown转换为HTML
    html_content = markdown2.markdown(summary_md, extras=["tables", "fenced-code-blocks"])
    
    # --- 关键修改：使用最简单的邮件对象构造方式 ---
    message = MIMEText(html_content, 'html', 'utf-8')
    
    # 1. Subject: 使用Header编码，但确保格式简单
    subject_str = f"每日邮件总结 - {datetime.now().strftime('%Y-%m-%d')}"
    message['Subject'] = Header(subject_str, 'utf-8')
    
    # 2. From: 直接使用邮箱地址，这是已验证的成功方式
    message['From'] = SENDER_EMAIL
    
    # 3. To: 直接使用邮箱地址，放弃复杂的显示名称
    message['To'] = RECEIVER_EMAIL
    # --- 修改结束 ---

    try:
        # 使用STARTTLS，这是更通用和推荐的SMTP加密方式
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        # 开启调试模式，以便在GitHub Actions中看到详细日志
        server.set_debuglevel(1)
        
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_AUTH_CODE)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], message.as_string())
        server.quit()
        print(f"成功发送邮件总结到 {RECEIVER_EMAIL}！")
    except Exception as e:
        print(f"发送邮件失败: {e}")
        import traceback
        traceback.print_exc() # 打印完整错误堆栈

# ==============================================================================
# 主执行入口
# ==============================================================================
if __name__ == "__main__":
    # 在执行核心逻辑前，进行一次必要的环境变量检查
    required_vars = ["IMAP_EMAIL", "IMAP_AUTH_CODE", "TARGET_FOLDER", "DEEPSEEK_API_KEY", 
                     "SENDER_EMAIL", "SENDER_AUTH_CODE", "RECEIVER_EMAIL", "SMTP_SERVER", "SMTP_PORT"]
    if not all(os.environ.get(var) for var in required_vars):
        print("错误：一个或多个必要的环境变量未设置。请检查GitHub Secrets配置。")
        exit(1)

    print(f"任务启动于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    today = datetime.now()
    emails = get_emails_from_target_date(today)
    summary_report = summarize_with_llm(emails)
    send_email_notification(summary_report)
    
    print(f"任务执行完毕于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
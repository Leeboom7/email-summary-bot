# find_folders.py
import imaplib
import getpass

print("--- 邮箱文件夹查找工具 ---")
print("本工具将帮助你找到邮件文件夹的“真实名称”，以便在配置中使用。")
print("你的输入信息不会被保存，请放心使用。\n")

EMAIL_ACCOUNT = input("请输入你的邮箱地址 (例如 12345@qq.com): ")
AUTH_CODE = getpass.getpass("请输入你的邮箱IMAP授权码 (输入时不可见): ")
IMAP_SERVER = input("请输入你的IMAP服务器地址 (例如 imap.qq.com): ")

try:
    conn = imaplib.IMAP4_SSL(IMAP_SERVER)
    conn.login(EMAIL_ACCOUNT, AUTH_CODE)
    print("\n✅ 登录成功！正在获取文件夹列表...\n")
    
    status, folder_list = conn.list()
    
    if status == 'OK':
        print("--- 你的邮箱文件夹列表 (请找到你需要的文件夹，并复制引号内的完整路径) ---")
        for folder in folder_list:
            print(folder.decode('utf-8'))
        print("\n例如，如果你想使用的文件夹显示为: (\\HasNoChildren) \"/\" \"INBOX/MyFolder\"")
        print("那么你需要复制的值就是: INBOX/MyFolder")
        print("---------------------------------------------------------------------------------")
    else:
        print("❌ 获取文件夹列表失败。")
        
    conn.logout()
except Exception as e:
    print(f"\n❌ 发生错误: {e}")
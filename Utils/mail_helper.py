import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import logging
from datetime import datetime


def send_test_failure_email(subject, body, to_emails, attachment_path=None, smtp_conf=None, html=False):
    """
    发送测试失败的邮件通知。

    参数:
    - subject: 邮件主题。
    - body: 邮件正文。
    - to_emails: 收件人邮箱列表。
    - attachment_path: 附件路径（可选）。
    - smtp_conf: SMTP配置字典，包括host、port、username和password（可选）。
    """
    # 生成当前时间戳
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 将时间插入正文最前面
    body = f"🕒 测试时间：{current_time}\n\n{body}"

    logging.info(f"📤 开始发送邮件 → 主题: {subject}，收件人: {to_emails}")

    # 如果未提供SMTP配置，则使用默认的QQ邮箱配置
    if smtp_conf is None:
        smtp_conf = {
            'host': 'smtp.qq.com',  # smtp.qiye.aliyun.com
            'port': 587,  # 465
            'username': '1121470915@qq.com',  # xiehua@vuv-tech.com
            'password': 'mxtkzssmatlfficb'  # 请将此替换为你从QQ邮箱生成的授权码
        }

    # 创建一个带附件的MIME邮件对象
    msg = MIMEMultipart()
    msg['From'] = smtp_conf['username']
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    # 将邮件正文附加到邮件对象中
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    # 如果提供了附件路径且文件存在，则读取附件并附加到邮件对象中
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

    try:
        # 尝试与SMTP服务器建立连接
        with smtplib.SMTP(smtp_conf['host'], smtp_conf['port']) as server:
            server.starttls()
            server.login(smtp_conf['username'], smtp_conf['password'])

            try:
                # 尝试发送邮件
                server.send_message(msg)
                logging.info("📬 错误报告邮件发送成功 ✅")
            except Exception as send_err:
                # 处理邮件发送阶段可能出现的异常
                logging.warning(f"📭 邮件发送阶段异常（可能已发送）：{send_err}")

    except smtplib.SMTPException as conn_err:
        # 处理SMTP连接建立失败的异常
        logging.error(f"❌ SMTP 建立连接失败：{conn_err}")
    except Exception as outer_err:
        # 处理SMTP关闭阶段的其他异常，通常是无害的，可以忽略
        logging.debug(f"🔁 SMTP 关闭阶段异常（无害，可忽略）：{outer_err}")



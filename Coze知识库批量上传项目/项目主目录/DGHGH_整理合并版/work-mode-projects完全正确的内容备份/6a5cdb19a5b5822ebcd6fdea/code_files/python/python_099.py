# alert_manager.py
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class AlertManager:
    def __init__(self, config):
        self.config = config
    
    def send_alert(self, subject: str, message: str, level: str = "error"):
        """发送告警"""
        if level not in self.config['alerts']['levels']:
            return
        
        # 邮件告警
        if 'email' in self.config['alerts']:
            self.send_email_alert(subject, message)
        
        # Webhook告警
        if 'webhook' in self.config['alerts']:
            self.send_webhook_alert(subject, message, level)
    
    def send_email_alert(self, subject: str, message: str):
        """发送邮件告警"""
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = f"[Coze自动化告警] {subject}"
        msg['From'] = self.config['alerts']['email']['from']
        msg['To'] = ', '.join(self.config['alerts']['email']['to'])
        
        with smtplib.SMTP(self.config['alerts']['email']['smtp_server']) as server:
            server.send_message(msg)
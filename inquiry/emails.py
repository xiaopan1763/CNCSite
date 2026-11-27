import threading
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def _send_emails_task(inquiry_id):
    """内部实际发送邮件的函数，将在后台线程中运行"""
    from .models import Inquiry
    
    try:
        inquiry = Inquiry.objects.get(id=inquiry_id)
    except Inquiry.DoesNotExist:
        return

    # 1. 发送给销售团队（管理员）
    admin_subject = f"【New RFQ】{inquiry.company or inquiry.name} - {inquiry.service_type}"
    admin_html = render_to_string('inquiry/email_admin_notification.html', {'inquiry': inquiry})
    
    msg_admin = EmailMultiAlternatives(
        subject=admin_subject,
        body=strip_tags(admin_html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['bonnie@guanhaoauto.com'], # 你的接收邮箱
    )
    msg_admin.attach_alternative(admin_html, "text/html")
    msg_admin.send(fail_silently=True)

    # 2. 自动回复客户
    user_subject = "Thank you for contacting Forest Machining - RFQ Received"
    user_html = render_to_string('inquiry/email_user_autoreply.html', {'inquiry': inquiry})
    
    msg_user = EmailMultiAlternatives(
        subject=user_subject,
        body=strip_tags(user_html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[inquiry.email],
    )
    msg_user.attach_alternative(user_html, "text/html")
    msg_user.send(fail_silently=True)

def send_inquiry_emails_async(inquiry_id):
    """对外暴露的接口：启动一个后台线程发送邮件"""
    thread = threading.Thread(target=_send_emails_task, args=(inquiry_id,))
    thread.daemon = True # 设置为守护线程，主程序结束时会自动退出
    thread.start()
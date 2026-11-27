from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InquiryForm
from .models import Inquiry
import json
from django.urls import reverse
from .emails import send_inquiry_emails_async

# 移除强制的 @login_required，改为公开访问
def submit_inquiry(request):
    if request.method == 'POST':
        # 如果未登录直接提交，阻断并提示
        if not request.user.is_authenticated:
            return redirect('user:login') # 这里可以替换为你首页弹窗的逻辑
            
        form = InquiryForm(request.POST, request.FILES)
        if form.is_valid():
            inquiry = form.save(commit=False)
            user = request.user
            inquiry.user = user
            inquiry.email = user.email
            inquiry.name = f"{user.first_name} {user.last_name}".strip() or user.username
            if hasattr(user, 'mobile'):
                inquiry.phone = user.mobile
            if hasattr(user, 'country'):
                inquiry.country = str(user.country.name)
            inquiry.save()
            # 【新增】将邮件任务推入后台线程异步执行
            send_inquiry_emails_async(inquiry.id)
            return redirect('inquiry:success')
    else:
        form = InquiryForm()

    # 获取绝对 URL 供 JSON-LD 和 Canonical 使用
    current_url = request.build_absolute_uri()

    # 【SEO/GEO 核心优化】深度结构化数据
    geo_schema = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Request a Quote - Forest Machining",
        "description": "Submit your CNC machining, injection molding, or 3D printing requests. Upload CAD files for a fast, precision quote.",
        "url": current_url,
        "mainEntity": {
            "@type": "Organization",
            "name": "Forest Machining",
            "url": "https://guanhaoauto.com",
            "email": "sales@forestmachining.com",
            "areaServed": ["US", "CA", "GB", "EU", "AU"],
            "potentialAction": {
                # 【关键】告诉 AI 这是一个获取报价的动作，并且有响应时间承诺
                "@type": "ReserveAction", 
                "name": "Request a Quote",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": current_url,
                    "actionPlatform": [
                        "http://schema.org/DesktopWebPlatform",
                        "http://schema.org/MobileWebPlatform"
                    ]
                },
                "result": {
                    "@type": "Thing",
                    "name": "CNC Machining Quote Document"
                }
            }
        }
    }

    seo_context = {
        'meta_description': "Request a fast, accurate quote for your custom manufacturing projects. Upload your 3D CAD files (STEP, STP, IGES) and get feedback within 24 hours.",
        'canonical_url': current_url,
        'geo_schema_json': json.dumps(geo_schema, ensure_ascii=False)
    }

    return render(request, 'inquiry/submit.html', {'form': form, **seo_context})

def success(request):
    return render(request, 'inquiry/success.html')
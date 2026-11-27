import json
from django.views.generic import TemplateView
from .models import Banner, FactSpec, FAQ, StatItem, OrderStep, Testimonial, CaseStudy
from capability.models import Category, Capability, Industry
from django.db.models import Avg, Count
from django.core.cache import cache
from user import forms

class IndexView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 首屏轮播
        context['banners'] = Banner.objects.filter(is_active=True).order_by('order')

        # 首页推荐分类（最多 3 个，由 Category.clean() 保证）
        context['featured_categories'] = Category.objects.filter(
            show_on_home=True
        ).order_by('order')[:3]

        # 首页推荐工艺（勾选 show_on_home 的工艺）
        context['featured_capabilities'] = Capability.objects.filter(
            show_on_home=True
        ).select_related('category').order_by('order')

        # 全部行业（用于"Industries We Serve"板块）
        context['industries'] = Industry.objects.all().order_by('name')

        # 首页专用数据（从 home 应用读取）
        context['fact_specs'] = FactSpec.objects.filter(is_active=True).order_by('order')
        faq_items = FAQ.objects.filter(is_active=True).order_by('order')
        context['faq_items'] = faq_items
        # 下单步骤
        context['order_steps'] = OrderStep.objects.filter(is_active=True).order_by('order')
        # 客户评价 + 汇总
        testimonials = Testimonial.objects.all()
        active_testimonials = testimonials.filter(is_active=True).order_by('order')
        context['testimonials'] = active_testimonials

        # 聚合计算综合评分（可选：加缓存）
        agg = testimonials.aggregate(
            avg_rating=Avg('rating'),
            total=Count('id')
        )
        context['avg_rating'] = round(agg['avg_rating'] or 0, 1)
        context['review_count'] = agg['total']



        # Stats：分成两组
        all_stats = StatItem.objects.filter(is_active=True).order_by('order')
        context['stats_partner'] = all_stats.filter(display_in__in=['partner', 'both'])
        context['stats_order'] = all_stats.filter(display_in__in=['order', 'both'])

        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.answer,
                    },
                }
                for item in faq_items
            ],
        }
        context['faq_schema_json'] = json.dumps(faq_schema, ensure_ascii=False)
        # 从 session 读取模态框和错误
        context['open_modal'] = self.request.session.pop('open_modal', None)
        # 不再重建 form_obj，让注册模态框使用 context_processors 提供的空表单
        context['login_error'] = self.request.session.pop('login_error', None)
        # 注册错误（从 session 取，并转换成纯字符串列表）
        register_errors_json = self.request.session.pop('register_errors', None)
        if register_errors_json:
            raw = json.loads(register_errors_json)
            context['register_errors'] = {
                field: [item['message'] for item in items]
                for field, items in raw.items()
            }
        else:
            context['register_errors'] = {}

        return context

# ============================================================
# 【SEO/GEO 终极优化版】关于我们页面视图
# ============================================================
class AboutView(TemplateView):
    template_name = 'home/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 复用首页的数据统计和客户评价，增加真实感
        context['stats_partner'] = StatItem.objects.filter(
            is_active=True, display_in__in=['partner', 'both']
        ).order_by('order')
        context['testimonials'] = Testimonial.objects.filter(is_active=True).order_by('order')[:3]
        
        # SEO 配置
        context['canonical_url'] = self.request.build_absolute_uri()
        context['meta_description'] = "Learn about Forest Machining. Discover our state-of-the-art CNC machining factory, our commitment to quality, and why top global companies trust us for custom parts."
        
        # 【GEO 优化】注入 AboutPage 及 Organization 增强数据
        geo_schema = {
            "@context": "https://schema.org",
            "@type": "AboutPage",
            "name": "About Forest Machining",
            "description": context['meta_description'],
            "url": context['canonical_url'],
            "mainEntity": {
                "@type": "Organization",
                "name": "Forest Machining",
                "url": "https://guanhaoauto.com",
                "logo": "https://guanhaoauto.com/static/image/logo.jpeg",
                "foundingDate": "2015", # 建议替换为你的真实建厂年份
                "numberOfEmployees": {
                    "@type": "QuantitativeValue",
                    "value": 50 # 建议替换为真实员工数，这能增加 AI 的信任度
                },
                "knowsAbout": ["CNC Machining", "3D Printing", "Injection Molding", "Die Casting", "Precision Manufacturing"],
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Dongguan",
                    "addressRegion": "Guangdong",
                    "addressCountry": "CN"
                },
                "sameAs": [
                    "https://www.linkedin.com/your-company-page",
                    "https://www.youtube.com/your-channel"
                ]
            }
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
        return context


# ============================================================
# 【新增】联系我们页面视图
# ============================================================
class ContactView(TemplateView):
    template_name = 'home/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # SEO 配置
        context['canonical_url'] = self.request.build_absolute_uri()
        context['meta_description'] = "Contact Forest Machining for custom CNC machining quotes. Reach out via email, phone, or visit our factory in Dongguan, China."
        
        # GEO 优化：本地商家 Schema
        contact_schema = {
            "@context": "https://schema.org",
            "@type": "ContactPage",
            "mainEntity": {
                "@type": "Organization",
                "name": "Forest Machining",
                "url": "https://guanhaoauto.com",
                "logo": "https://guanhaoauto.com/static/image/logo.jpeg",
                "contactPoint": [
                    {
                        "@type": "ContactPoint",
                        "telephone": "+86 123 4567 8901", # 替换为你的真实电话
                        "contactType": "sales",
                        "email": "sales@forestmachining.com",
                        "areaServed": ["US", "CA", "GB", "EU", "AU"],
                        "availableLanguage": "English"
                    }
                ],
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Your Factory Address", # 替换为真实地址
                    "addressLocality": "Dongguan",
                    "addressRegion": "Guangdong",
                    "postalCode": "523000",
                    "addressCountry": "CN"
                }
            }
        }
        import json
        context['geo_schema_json'] = json.dumps(contact_schema, ensure_ascii=False)
        return context    

# ============================================================
# 【SEO/GEO 终极优化版】设计与法律相关页面视图
# ============================================================

class DesignGuidelinesView(TemplateView):
    template_name = 'home/design_guidelines.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['canonical_url'] = self.request.build_absolute_uri()
        context['meta_description'] = "Explore our comprehensive design guidelines for CNC machining, 3D printing, and injection molding. Learn about tolerances, wall thickness, and material selection."
        
        # 【GEO 优化】告诉 AI 这是一个权威的技术指南
        geo_schema = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": "Manufacturing Design Guidelines",
            "description": context['meta_description'],
            "author": {
                "@type": "Organization",
                "name": "Forest Machining"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Forest Machining",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://guanhaoauto.com/static/image/logo.jpeg"
                }
            },
            "url": context['canonical_url']
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
        return context


class CaseStudiesView(TemplateView):
    template_name = 'home/case_studies.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case_studies = CaseStudy.objects.filter(is_active=True).order_by('order', '-created_at')
        context['case_studies'] = case_studies
        
        context['canonical_url'] = self.request.build_absolute_uri()
        context['meta_description'] = "Read our latest case studies. See how Forest Machining helps global companies manufacture complex parts with precision."
        
        # 【GEO 优化】如果后台有案例，生成包含多个案例的 ItemList
        if case_studies.exists():
            item_list = []
            for idx, study in enumerate(case_studies):
                item_list.append({
                    "@type": "ListItem",
                    "position": idx + 1,
                    "item": {
                        "@type": "Article",
                        "headline": study.title,
                        "about": study.client_industry,
                        "description": study.challenge[:150] + "...",
                        "image": self.request.build_absolute_uri(study.image.url) if study.image else "",
                    }
                })
            
            geo_schema = {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "Case Studies",
                "description": context['meta_description'],
                "url": context['canonical_url'],
                "mainEntity": {
                    "@type": "ItemList",
                    "itemListElement": item_list
                }
            }
            context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
            
        return context 


class TermsView(TemplateView):
    template_name = 'home/terms.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['canonical_url'] = self.request.build_absolute_uri()
        # 【补齐 Meta Description】
        context['meta_description'] = "Read the Terms and Conditions for using Forest Machining's manufacturing services and website."
        
        # 【GEO 优化】基础的 WebPage 声明
        geo_schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "Terms and Conditions",
            "url": context['canonical_url']
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
        return context


class PrivacyView(TemplateView):
    template_name = 'home/privacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['canonical_url'] = self.request.build_absolute_uri()
        # 【补齐 Meta Description】
        context['meta_description'] = "Learn how Forest Machining protects your data, intellectual property, and CAD files. Read our full Privacy Policy."
        
        # 【GEO 优化】基础的 WebPage 声明
        geo_schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "Privacy Policy",
            "url": context['canonical_url']
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
        return context


   
    
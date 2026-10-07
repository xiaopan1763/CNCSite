import json
from django.views.generic import TemplateView
from .models import Banner, FactSpec, FAQ, StatItem, OrderStep, Testimonial
from capability.models import Category, Capability, Industry
from django.db.models import Avg, Count
from django.core.cache import cache

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
        
        return context
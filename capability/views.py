from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count
from .models import Category, Capability
from home.models import FAQ, OrderStep, Testimonial


class CapabilityListView(ListView):
    model = Category
    template_name = 'capability/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(
            is_featured=True
        ).prefetch_related('capabilities').order_by('order')


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'capability/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class CapabilityDetailView(DetailView):
    model = Capability
    template_name = 'capability/detail.html'
    context_object_name = 'capability'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 复用首页组件（全部从 home.models 读）
        context['order_steps'] = OrderStep.objects.filter(is_active=True).order_by('order')
        context['faq_items'] = FAQ.objects.filter(is_active=True).order_by('order')

        # 客户评价 + 综合评分聚合
        testimonials = Testimonial.objects.all()
        active_testimonials = testimonials.filter(is_active=True).order_by('order')
        context['testimonials'] = active_testimonials

        agg = testimonials.aggregate(
            avg_rating=Avg('rating'),
            total=Count('id')
        )
        context['avg_rating'] = round(agg['avg_rating'] or 0, 1)
        context['review_count'] = agg['total']

        # 同分类下的其他工艺
        context['related_capabilities'] = Capability.objects.filter(
            category=self.object.category
        ).exclude(pk=self.object.pk).order_by('order')[:4]

        return context
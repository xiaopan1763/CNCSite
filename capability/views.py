import json
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Q, Prefetch
from .models import Category, Capability, Material, Industry
from home.models import FAQ, OrderStep, Testimonial, StatItem

class CapabilityDetailView(DetailView):
    model = Capability
    template_name = 'capability/detail.html'
    context_object_name = 'capability'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    # 【优化 1】使用 get_queryset 预加载关联数据，提升页面加载速度
    def get_queryset(self):
        return Capability.objects.select_related('category').prefetch_related(
            'industries', 
            'materials', 
            'surface_finishes', 
            'specs'  # 预加载规格表格
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. 动态获取相关的 FAQ
        # 提取当前页面的工艺名称，例如 "CNC Turning"
        current_capability_name = self.object.title 
        
        # 查找问题或回答中包含该工艺名称的 FAQ
        related_faqs = FAQ.objects.filter(
            Q(question__icontains=current_capability_name) | 
            Q(answer__icontains=current_capability_name)
        ).order_by('order')

        # 如果针对该工艺没有录入特定的 FAQ，可以设置一个兜底方案（选填）
        # 比如：显示前 4 个通用的 FAQ
        if not related_faqs.exists():
            # 这里拿掉前 4 个（通常包含 CNC Machining 等通用问答）
            related_faqs = FAQ.objects.filter(is_active=True).order_by('order')[:4]

        context['faq_items'] = related_faqs

        # 2. 其他原有代码保持不变
        context['order_steps'] = OrderStep.objects.filter(is_active=True).order_by('order')
        
        # 【优化 2】评价统计统一使用启用的评价
        active_testimonials = Testimonial.objects.filter(is_active=True).order_by('order')
        context['testimonials'] = active_testimonials

        agg = active_testimonials.aggregate(
            avg_rating=Avg('rating'),
            total=Count('id')
        )
        context['avg_rating'] = round(agg['avg_rating'] or 0, 1)
        context['review_count'] = agg['total']

        # 同分类下的其他工艺
        context['related_capabilities'] = Capability.objects.filter(
            category=self.object.category
        ).exclude(pk=self.object.pk).order_by('order')[:4]

        # 【新增】获取首页的统计数据，用于底部的 CTA 板块
        context['stats_order'] = StatItem.objects.filter(
            is_active=True, 
            display_in__in=['order', 'both']
        ).order_by('order')

        # 【新增】将规格数据分成两个列表
        specs = self.object.specs.all()
        context['tolerance_specs'] = specs.filter(spec_type='tolerance')
        context['guideline_specs'] = specs.filter(spec_type='guideline')

        # 【新增】将材料按类别提前分好，方便前端智能渲染 Tab
        materials = self.object.materials.all()
        context['metals'] = materials.filter(category='metal')
        context['plastics'] = materials.filter(category='plastic')
        context['others'] = materials.filter(category='other')

        return context
    
# ============================================================
# 【新增】工艺分类列表页视图
# ============================================================
class CapabilityListView(ListView):
    model = Category
    template_name = 'capability/list.html'
    context_object_name = 'categories'
    paginate_by = None # 列表页如果不需要分页可以设为 None，如果需要分页可以设置每页数量

    def get_queryset(self):
        # 核心逻辑：
        # 1. filter(capabilities__isnull=False) 过滤掉没有配置任何工艺的“空分类”，防止前端出现空白区块
        # 2. prefetch_related 预加载关联的工艺，并在预加载时应用 Capability 模型自带的 Meta ordering ('order', 'title')
        # 3. distinct() 去除因为联表查询产生的重复分类
        return Category.objects.filter(capabilities__isnull=False).prefetch_related(
            'capabilities'
        ).distinct().order_by('order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取底部 CTA 需要的统计数据
        context['stats_order'] = StatItem.objects.filter(
            is_active=True, 
            display_in__in=['order', 'both']
        ).order_by('order')
        # 【SEO优化】1. 动态 Canonical URL
        context['canonical_url'] = self.request.build_absolute_uri(self.request.path)
        
        # 【SEO优化】2. 动态 Meta Description (结合后台数据的描述)
        # 这里提取所有分类的名字拼接成一句话，供搜索引擎展示
        cat_names = [cat.name for cat in context['categories']]
        context['meta_description'] = f"Explore Forest Machining's capabilities including {', '.join(cat_names)}. Precision manufacturing services for aerospace, automotive, and medical industries."

        # 【GEO优化】3. 构建 ItemList 结构化数据 (JSON-LD)
        item_list_elements = []
        position = 1
        for cat in context['categories']:
            for cap in cat.capabilities.all():
                item_list_elements.append({
                    "@type": "ListItem",
                    "position": position,
                    "item": {
                        "@type": "Service",
                        "name": cap.title,
                        "url": self.request.build_absolute_uri(reverse('capability:detail', kwargs={'slug': cap.slug})),
                        "description": cap.excerpt or cap.description[:160],
                        "provider": {
                            "@type": "Organization",
                            "name": "Forest Machining"
                        }
                    }
                })
                position += 1

        geo_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Manufacturing Capabilities",
            "description": context['meta_description'],
            "url": context['canonical_url'],
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(item_list_elements),
                "itemListElement": item_list_elements
            }
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
        
        return context
    
# ============================================================
# 【新增】材料列表页视图
# ============================================================
class MaterialListView(ListView):
    model = Material
    template_name = 'capability/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        return Material.objects.all().order_by('category', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 获取底部 CTA 需要的统计数据
        context['stats_order'] = StatItem.objects.filter(
            is_active=True, 
            display_in__in=['order', 'both']
        ).order_by('order')
        
        # 分类数据（用于前端 Tab）
        context['metals'] = self.get_queryset().filter(category='metal')
        context['plastics'] = self.get_queryset().filter(category='plastic')
        context['others'] = self.get_queryset().filter(category='other')

        # SEO 配置
        context['canonical_url'] = self.request.build_absolute_uri(self.request.path)
        context['meta_description'] = "Explore our comprehensive selection of metals and plastics for precision CNC machining. From Aluminum 6061 to PEEK, we have the materials for your project."

        # GEO 结构化数据 (ItemList)
        item_list = []
        for idx, mat in enumerate(context['materials']):
            item_list.append({
                "@type": "ListItem",
                "position": idx + 1,
                "item": {
                    "@type": "DefinedTerm",
                    "name": mat.name,
                    "description": mat.desc or f"High-quality {mat.name} material."
                }
            })
        
        geo_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Materials",
            "description": context['meta_description'],
            "url": context['canonical_url'],
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": item_list
            }
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)
        
        return context


# ============================================================
# 【新增】行业列表页视图
# ============================================================
class IndustryListView(ListView):
    model = Industry
    template_name = 'capability/industry_list.html'
    context_object_name = 'industries'

    def get_queryset(self):
        # 预加载该行业下的工艺，方便前端展示数量或关联
        return Industry.objects.all().prefetch_related('capabilities').order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 获取底部 CTA 需要的统计数据
        context['stats_order'] = StatItem.objects.filter(
            is_active=True, 
            display_in__in=['order', 'both']
        ).order_by('order')
        
        # SEO 配置
        context['canonical_url'] = self.request.build_absolute_uri(self.request.path)
        context['meta_description'] = "Forest Machining serves a wide range of industries including aerospace, automotive, medical, and electronics. Discover our industry-specific manufacturing solutions."

        # GEO 结构化数据
        item_list = []
        for idx, ind in enumerate(context['industries']):
            item_list.append({
                "@type": "ListItem",
                "position": idx + 1,
                "item": {
                    "@type": "DefinedTerm",
                    "name": ind.name,
                    "description": ind.desc or f"Manufacturing solutions for the {ind.name} industry."
                }
            })

        geo_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Industries We Serve",
            "description": context['meta_description'],
            "url": context['canonical_url'],
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": item_list
            }
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)

        return context
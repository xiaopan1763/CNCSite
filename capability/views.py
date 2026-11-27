import json
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Q, Prefetch
from .models import Category, Capability, Material, Industry, SurfaceFinish
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
# 工艺分类列表页视图
# ============================================================
class CapabilityListView(ListView):
    model = Category
    template_name = 'capability/list.html'
    context_object_name = 'categories'
    paginate_by = None # 列表页如果不需要分页可以设为 None，如果需要分页可以设置每页数量

    def get_queryset(self):
        # 1. 基础 Queryset：所有工艺
        cap_queryset = Capability.objects.all().order_by('order', 'title')
        
        # 2. 获取 URL 参数
        material_id = self.request.GET.get('material')
        industry_id = self.request.GET.get('industry')
        finish_id = self.request.GET.get('finish')
        category_name = self.request.GET.get('category_name')

        # 【新增】获取名称参数和材料大类参数
        material_name = self.request.GET.get('material_name')
        industry_name = self.request.GET.get('industry_name')
        finish_name = self.request.GET.get('finish_name')
        material_category = self.request.GET.get('material_category')
        
        # 3. 根据参数过滤工艺
        if material_id:
            cap_queryset = cap_queryset.filter(materials__id=material_id)
        if industry_id:
            cap_queryset = cap_queryset.filter(industries__id=industry_id)
        if finish_id:
            cap_queryset = cap_queryset.filter(surface_finishes__id=finish_id)
        if category_name: 
            cap_queryset = cap_queryset.filter(category__name=category_name)

        # 【新增】按名称和大类过滤
        if material_name:
            cap_queryset = cap_queryset.filter(materials__name__iexact=material_name)
        if industry_name:
            cap_queryset = cap_queryset.filter(industries__name__iexact=industry_name)
        if finish_name:
            cap_queryset = cap_queryset.filter(surface_finishes__name__iexact=finish_name)
        if material_category:
            cap_queryset = cap_queryset.filter(materials__category=material_category)

        # 【关键修复】去除多对多联表查询产生的重复工艺
        cap_queryset = cap_queryset.distinct()
        
        # 4. 过滤分类并预加载
        return Category.objects.filter(
            capabilities__in=cap_queryset
        ).prefetch_related(
            # 【核心】用 Prefetch 对象确保分类下只预加载符合条件的工艺
            Prefetch('capabilities', queryset=cap_queryset)
        ).distinct().order_by('order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取底部 CTA 需要的统计数据
        context['stats_order'] = StatItem.objects.filter(
            is_active=True, 
            display_in__in=['order', 'both']
        ).order_by('order')

        # 【SEO优化】1. 动态 Canonical URL
        context['canonical_url'] = self.request.build_absolute_uri()
        
        # 【核心修改】处理筛选提示条的上下文（合并了ID与名称双重过滤逻辑）
        material_id = self.request.GET.get('material')
        industry_id = self.request.GET.get('industry')
        finish_id = self.request.GET.get('finish')
        category_name = self.request.GET.get('category_name')
        
        # 新增导航栏传来的名称参数
        material_name = self.request.GET.get('material_name')
        industry_name = self.request.GET.get('industry_name')
        finish_name = self.request.GET.get('finish_name')
        material_category = self.request.GET.get('material_category')

        context['active_filter'] = None
        context['clear_filter_url'] = reverse('capability:list')

        # 1. 判断分类
        if category_name:
            context['active_filter'] = f"Category: {category_name}"
            
        # 2. 判断材料 (优先处理ID，再处理名称，最后处理大类)
        elif material_id:
            try:
                mat = Material.objects.get(id=material_id)
                context['active_filter'] = f"Material: {mat.name}"
            except Material.DoesNotExist:
                pass
        elif material_name:
            context['active_filter'] = f"Material: {material_name}"
        elif material_category:
            # 将英文缩写转为更美观的展示文字
            cat_dict = {'metal': 'Metals', 'plastic': 'Plastics', 'other': 'Others'}
            context['active_filter'] = f"Material Type: {cat_dict.get(material_category, material_category)}"
            
        # 3. 判断行业
        elif industry_id:
            try:
                ind = Industry.objects.get(id=industry_id)
                context['active_filter'] = f"Industry: {ind.name}"
            except Industry.DoesNotExist:
                pass
        elif industry_name:
            context['active_filter'] = f"Industry: {industry_name}"
            
        # 4. 判断表面处理
        elif finish_id:
            try:
                fin = SurfaceFinish.objects.get(id=finish_id)
                context['active_filter'] = f"Surface Finish: {fin.name}"
            except SurfaceFinish.DoesNotExist:
                pass
        elif finish_name:
            context['active_filter'] = f"Surface Finish: {finish_name}"

        # 【SEO优化】2. 动态 Meta Description
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
    
# ============================================================
# 【新增】表面处理列表页视图
# ============================================================
class SurfaceFinishListView(ListView):
    model = SurfaceFinish
    template_name = 'capability/finish_list.html'
    context_object_name = 'finishes'

    def get_queryset(self):
        # 预加载关联的工艺，用于统计数量
        return SurfaceFinish.objects.all().prefetch_related('capabilities').order_by('order', 'id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['stats_order'] = StatItem.objects.filter(
            is_active=True, display_in__in=['order', 'both']
        ).order_by('order')
        
        context['canonical_url'] = self.request.build_absolute_uri(self.request.path)
        context['meta_description'] = "Explore our professional surface finishing services including anodizing, powder coating, bead blasting, and more. Enhance the durability and aesthetics of your CNC machined parts."

        # GEO 结构化数据
        item_list = []
        for idx, fin in enumerate(context['finishes']):
            item_list.append({
                "@type": "ListItem",
                "position": idx + 1,
                "item": {
                    "@type": "DefinedTerm",
                    "name": fin.name,
                    "description": fin.desc or f"Professional {fin.name} services."
                }
            })

        geo_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Surface Finishes",
            "description": context['meta_description'],
            "url": context['canonical_url'],
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": item_list
            }
        }
        context['geo_schema_json'] = json.dumps(geo_schema, ensure_ascii=False)

        return context
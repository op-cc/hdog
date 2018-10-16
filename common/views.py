from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View

from categories.models import Category

from hdog.forms import GoodsRowForm, GoodsRowFormSet, TransferForm
from hdog.models import (
    Category,
    Goods,
    Measure,
    StorePlace,
    Transfer,
    TransferedGoods,
    InventoryNumber,
)


def redirect_to_stock(request):
    store_place_pk = request.COOKIES.get('store_place_pk')

    if not store_place_pk:
        try:
            store_place_pk = StorePlace.objects.all()[0].pk
        except IndexError:
            store_place_pk = 1

    return redirect('stock_overview', store_place_pk=store_place_pk)


def stock_overview(request, store_place_pk):
    template = 'common/goods_table.html'

    get_only_in_stock = int(request.GET.get('in_stock', '1'))
    selected_categories = request.GET.getlist('category')

    goods_name = request.GET.get('goods_name', None)

    all_store_places = True if request.GET.get('all_store_places', 'false') == 'true' else False

    if all_store_places:
        store_places = StorePlace.objects.all()
        display_store_in_table = True
    else:
        store_places = StorePlace.objects.filter(pk=store_place_pk)
        display_store_in_table = False

    goods = Goods.objects.filter(store_place__in=store_places)

    if get_only_in_stock == 1:
        goods = goods.filter(quantity__gte=1)
    elif get_only_in_stock == 0:
        goods = goods.filter(quantity=0)

    if goods_name:
        goods = goods.filter(name__icontains=goods_name)

    if selected_categories:
        goods = goods.filter(category__slug__in=selected_categories)

    goods = goods.prefetch_related(
        'category',
        'unit',
        'store_place',
    )

    page = int(request.GET.get('page', '1'))
    paginator = Paginator(goods, settings.GOODS_PER_PAGE)
    goods_page = paginator.get_page(page)

    categories_set = Category.objects.filter(
        goods__store_place__pk__in=store_places).distinct()

    context = {
        'store_place_pk': store_place_pk,
        'goods_page': goods_page,
        'categories_set': categories_set,
        'store_places': StorePlace.objects.all().prefetch_related('stock', 'staff'),
        'title': 'Список ТМЦ',
        'get_only_in_stock': get_only_in_stock,
        'selected_categories': selected_categories,
        'goods_name': goods_name,
        'all_store_places': all_store_places,
        'display_store_in_table': display_store_in_table,
        'paginator': paginator,
        'goods_number_offset': (goods_page.number - 1) * settings.GOODS_PER_PAGE,
    }

    return render(request, template, context=context)


class RegisterIncomeView(View):
    template_name = 'common/register_income.html'

    def get_context_data(self, request):
        goods = Goods.objects.all()
        categories = Category.objects.all()
        measures = Measure.objects.all()
        store_place_pk = request.COOKIES.get('store_place_pk', StorePlace.objects.all()[0].pk)

        context = {
            'store_place_pk': int(store_place_pk),
            'store_places': StorePlace.objects.all(),
            'goods_set': goods,
            'categories_set': categories,
            'measures_set': measures,
            'title': 'Поступление',
            'transfer_form': TransferForm(),
            'goods_form_set': GoodsRowFormSet(),
        }

        return context

    def get(self, request, **kwargs):
        context = self.get_context_data(request)

        return render(request, self.template_name, context=context)

    def post(self, request, **kwargs):
        context = self.get_context_data(request)

        transfer_form = TransferForm(request.POST)

        transfer_is_valid = transfer_form.is_valid()

        if transfer_is_valid:
            store = StorePlace.objects.get(pk=context['store_place_pk'])

            income = Transfer(**transfer_form.cleaned_data)
            income.save()
            income.refresh_from_db()

            goods_form_set = GoodsRowFormSet(request.POST)

            for form in goods_form_set:
                form.transfer = income
                form.recepient = store

        if transfer_is_valid and goods_form_set.is_valid():
            for goods_row in goods_form_set.cleaned_data:
                TransferedGoods.create(
                    income,
                    goods_name=goods_row['goods'],
                    price=goods_row['price'],
                    quantity=goods_row['quantity'],
                    recepient=store,
                    generate_inv_numbers=goods_row['generate_inv_numbers'],
                    inv_numbers=goods_row['inv_numbers'],
                    category=goods_row['category'],
                    measure=goods_row['measure'],
                )
        else:
            context['transfer_form'] = transfer_form
            context['goods_form_set'] = goods_form_set

            income.delete()

        return render(request, self.template_name, context=context)

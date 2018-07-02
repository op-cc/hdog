from django.shortcuts import render, redirect

from categories.models import Category

from hdog.models import Goods, StorePlace


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

    get_only_in_stock = True if request.GET.get('in_stock', '1') == '1' else False
    selected_categories = request.GET.getlist('category')

    store_place = StorePlace.objects.get(pk=store_place_pk)
    goods = Goods.objects.filter(store_place__pk=store_place_pk)

    if get_only_in_stock:
        goods = goods.filter(quantity__gte=1)
    else:
        goods = goods.filter(quantity=0)

    if selected_categories:
        goods = goods.filter(category__slug__in=selected_categories)

    context = {
        'store_place_pk': store_place_pk,
        'goods_set': goods,
        'categories_set': Category.objects.filter(goods__store_place=store_place),
        'store_places': StorePlace.objects.all(),
        'title': 'Список ТМЦ',
        'get_only_in_stock': get_only_in_stock,
        'selected_categories': selected_categories,
    }

    return render(request, template, context=context)

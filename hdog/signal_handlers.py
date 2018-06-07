from .models import InventoryNumber, TransferedGoods


def update_inv_numbers_on_transfer(instance, action, model, pk_set, **kwargs):
    if isinstance(instance, TransferedGoods) and \
       model == InventoryNumber:
        goods_for_inv_number = instance.recepient_goods if instance.recepient_goods else None
        model.objects.filter(pk__in=pk_set).update(supply=goods_for_inv_number)

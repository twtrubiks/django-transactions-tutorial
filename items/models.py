import threading
import time

from django.db import models
from django.db import transaction


class Item(models.Model):
    stock = models.IntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    """ track of changes """
    version = models.IntegerField(default=0)


def create_items_no_transaction(**kwargs):
    count = int(kwargs.get('count'))
    result_code = 200
    try:
        for i in range(0, count):
            if i == count - 2:
                Item.objects.create(stock=100, price='error')
            else:
                Item.objects.create(stock=100, price=10)
    except Exception as e:
        Exception('Unexpected error: {}'.format(e))
        result_code = 500
    return result_code


def create_items_with_transaction(**kwargs):
    count = int(kwargs.get('count'))
    result_code = 200
    try:
        with transaction.atomic():
            for i in range(0, count):
                if i == count - 2:
                    Item.objects.create(stock=100, price='error')
                else:
                    Item.objects.create(stock=100, price=10)
    except Exception as e:
        Exception('Unexpected error: {}'.format(e))
        result_code = 500
    return result_code


def data_no_consistency_purchase(delay=0.02):
    for i in range(0, 100):
        item = Item.objects.get(id=1)
        item.stock = item.stock + 1
        item.save()
        time.sleep(delay)
    print('data_no_consistency_purchase done')


def data_no_consistency_pick_up(delay=0.05):
    for i in range(0, 100):
        item = Item.objects.get(id=1)
        item.stock = item.stock - 1
        item.save()
        time.sleep(delay)
    print('data_no_consistency_pick_up done')


def data_no_consistency():
    threading.Thread(target=data_no_consistency_purchase).start()
    threading.Thread(target=data_no_consistency_pick_up).start()
    return 200


def consistency_optimistic_purchase(delay=0.01):
    i = 0
    """use version (add field) track of changes """
    while i < 100:
        old_item = Item.objects.get(id=1)
        stock = old_item.stock
        version = old_item.version
        item = Item.objects.filter(id=1, version=version).update(stock=stock + 1, version=version + 1)
        if item:
            i += 1
        else:
            print('item is null (optimistic_purchase)')
        time.sleep(delay)
    """use stock track of changes """
    while i < 100:
        old_item = Item.objects.get(id=1)
        stock = old_item.stock
        item = Item.objects.filter(id=1, stock=stock).update(stock=stock + 1)
        if item:
            i += 1
        else:
            print('item is null (optimistic_purchase)')
        time.sleep(delay)
    print('data_no_consistency_purchase done')
    return 200


def consistency_optimistic_pick_up(delay=0.02):
    i = 0
    """use version (add field) track of changes """
    while i < 100:
        old_item = Item.objects.get(id=1)
        stock = old_item.stock
        version = old_item.version
        item = Item.objects.filter(id=1, version=version).update(stock=stock - 1, version=version + 1)
        if item:
            i += 1
        else:
            print('item is null (optimistic_pick_up)')
        time.sleep(delay)
    """use stock track of changes """
    while i < 100:
        old_item = Item.objects.get(id=1)
        stock = old_item.stock
        item = Item.objects.filter(id=1, stock=stock).update(stock=stock - 1)
        if item:
            i += 1
        else:
            print('item is null (optimistic_pick_up)')
        time.sleep(delay)
    print('data_no_consistency_purchase done')
    return 200


def consistency_pessimistic_purchase(delay=0.02):
    for i in range(0, 100):
        try:
            with transaction.atomic():
                item = Item.objects.select_for_update().get(id=1)
                item.stock = item.stock + 1
                item.save()
                time.sleep(delay)
        except Exception as e:
            Exception('Unexpected error: {}'.format(e))
    print('data_no_consistency_pick_up done')


def consistency_pessimistic_pick_up(delay=0.05):
    for i in range(0, 100):
        try:
            with transaction.atomic():
                item = Item.objects.select_for_update().get(id=1)
                item.stock = item.stock - 1
                item.save()
                time.sleep(delay)
        except Exception as e:
            Exception('Unexpected error: {}'.format(e))
    print('data_no_consistency_pick_up done')


def data_consistency():
    """ use pessimistic """
    # threading.Thread(target=consistency_pessimistic_purchase).start()
    # threading.Thread(target=consistency_pessimistic_pick_up).start()
    """ use optimistic """
    threading.Thread(target=consistency_optimistic_purchase).start()
    threading.Thread(target=consistency_optimistic_pick_up).start()
    return 200
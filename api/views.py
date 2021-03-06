from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils import timezone

from api.utils import clean_orders, calculate_total
from menu.models import Item, Order


def add(request):
    json = {}

    if request.method == 'GET' and 'id' in request.GET:
        item_id = request.GET['id']

        try:
            item = Item.objects.get(id=item_id)

            basket = request.session.get('basket', {})

            if item in basket:
                basket[item] += 1
            else:
                basket[item] = 1

            request.session['basket'] = basket

            # TODO: Remove debug print
            print(basket)

            json['success'] = True
        except Item.DoesNotExist:
            print("Invalid item item: %s" % item_id)

    if 'success' not in json:
        json['success'] = 'false'

    return JsonResponse(json)


def remove(request):
    json = {}

    if request.method == 'GET' and 'id' in request.GET:
        item_id = request.GET['id']

        try:
            item = Item.objects.get(id=item_id)
            basket = request.session.get('basket', {})

            quantity = 1
            if 'q' in request.GET:
                quantity = int(request.GET['q'])

            if item in basket:
                basket[item] -= quantity

                json['quantity'] = 0
                json['subtotal'] = 0

                if basket[item] <= 0:
                    del basket[item]
                else:
                    json['quantity'] = basket[item]
                    json['subtotal'] = item.final_price() * basket[item]

                request.session['basket'] = basket
                json['success'] = True

        except Item.DoesNotExist:
            print("Invalid item item: %s" % item_id)

    if 'success' not in json:
        json['success'] = 'false'

    return JsonResponse(json)


def count(request):
    items = 0
    basket = request.session.get('basket', {})
    for k, v in basket.items():
        items += v

    return JsonResponse({'count': items})


def clean(request):
    return JsonResponse({"cleaned": clean_orders()})


def empty(request):
    request.session['basket'] = {}
    return JsonResponse({"success": True})


def total(request):
    return JsonResponse({"total": calculate_total(request.session.get("basket", {}))})



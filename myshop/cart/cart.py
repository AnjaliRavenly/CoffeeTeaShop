from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart(object):
    def __init__(self, request):
        """
        Inicjacja koszyka na zakuoy
        :param request:
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            #zapisz pustego koszyka
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Dodanie lub zmaina ilości produktu w koszyku.
        konwersja na str dla jsona
        :param product:
        :param quantity:
        :param update_quantity:
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        """
        usunięcie productu z koszyka
        :param product:
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iteracja przez elementy w koszyku i pobieranie produktów z Bazy Danych
        :yield:item
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        suma ilości produktów w koszyku
        :return: sum
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        suma ceny za wszystkie produkty w koszyku
        :return: sum
        """
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        usunięcie koszyka na zakupy z sesji
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
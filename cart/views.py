from django.shortcuts import render, redirect
from django.views import generic
from .utils import get_or_set_order_session, get_or_set_favorite_session
from django.shortcuts import get_object_or_404, reverse
from .forms import AddToCartForm, PaymentForm, CustommerInformationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

from .models import Product, OrderItem, FavoriteProduct, Payment, CustommerDetail, ProductDetail, District, City, Category, Review
from django.utils.decorators import method_decorator
from .choices import limit_choices as l, price_choices, sort_choice
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.decorators import api_view


class ProductListView(generic.TemplateView):
    template_name = 'product_list.html'

    def get_context_data(self, **kwargs):
        limit = 6
        if ('limit' in self.request.GET):
            limit = self.request.GET['limit']
        products = Product.objects.all()

        # Category
        category = ''
        if "category" in self.request.GET:
            category = self.request.GET['category']
            if category:
                try:
                    print("ahih")
                    category = Category.objects.get(title=category)
                    products = products.filter(category=category)
                except:
                    products = products.filter(category=None)

        # Search
        search = ''
        if "search" in self.request.GET:
            search = self.request.GET['search']
            if search:
                products = products.filter(title__icontains=search)

        # Sort
        sort = ''
        if "sort" in self.request.GET:
            sort = self.request.GET['sort']
            if sort:
                products = products.order_by(sort)
        # paginator
        paginator = Paginator(products, limit)
        page = 1
        if ('page' in self.request.GET):
            page = self.request.GET['page']
        paged_listings = paginator.get_page(page)

        context = super(ProductListView, self).get_context_data(**kwargs)
        context['products'] = paged_listings
        liked = []
        if self.request.user.is_authenticated:
            for like_item in FavoriteProduct.objects.filter(user=self.request.user):
                liked.append(like_item.product.id)

            self.request.session['products_in_favorite'] = FavoriteProduct.objects.filter(
                user=self.request.user).count()
        categories = Category.objects.all()

        # Choices
        limit_choices = l
        context['limit'] = limit
        context['limit_choices'] = limit_choices
        context['sort_choices'] = sort_choice
        context['sort'] = sort
        context['categories'] = categories
        context['category'] = category
        context['search'] = search
        context['liked'] = liked

        return context


class ProductDetailView(generic.FormView):
    template_name = 'product.html'
    form_class = AddToCartForm

    def get_object(self):
        print("get object")
        return get_object_or_404(Product, slug=self.kwargs["slug"])

    def get_success_url(self):
        print("get success url")
        return reverse("cart:summary")
        # return
        # HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_form_kwargs(self):
        kwargs = super(ProductDetailView, self).get_form_kwargs()
        kwargs['product_id'] = self.get_object().id

        return kwargs

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        product = self.get_object()

        item_filter = order.items.filter(
            product=product)

        if item_filter.exists():
            item = item_filter.first()
            item.quantity = int(form.cleaned_data['quantity'])
            item.save()

        else:
            new_item = form.save(commit=False)
            new_item.product = product
            new_item.order = order
            new_item.save()

        return super(ProductDetailView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        reviews = Review.objects.filter(product=self.get_object())

        try:
            liked = None
            if self.request.user.is_authenticated:
                liked = FavoriteProduct.objects.get(
                    user=self.request.user, product=self.get_object())
        except FavoriteProduct.DoesNotExist:
            liked = None

        if ('review_limit' in self.request.GET):
            reviews = reviews[:int(self.request.GET['review_limit'])]
        context['object'] = self.get_object()
        context['categories'] = categories
        context['reviews'] = reviews

        context['liked'] = liked

        return context


class CartView(generic.TemplateView):
    template_name = "order_summary.html"

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context["object"] = get_or_set_order_session(self.request)
        return context


class CheckOutView(generic.TemplateView):
    template_name = "payment.html"

    def get_context_data(self, **kwargs):
        context = super(CheckOutView, self).get_context_data(**kwargs)
        context["object"] = get_or_set_order_session(self.request)

        return context


class IncreaseQuantityView(generic.View):
    def get(sefl, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.quantity += 1
        order_item.save()
        return redirect("cart:summary")


class DecreaseQuantityView(generic.View):
    def get(sefl, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.save()
        return redirect("cart:summary")


class RemoveFromCartView(generic.View):
    def get(sefl, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect("cart:summary")


@api_view(['GET', ])
def TymOrUnTym(request, product_id):

    if request.user.is_authenticated:
        if request.method == 'GET':
            liked = True
            product = Product.objects.get(pk=product_id)
            try:
                favorite = FavoriteProduct.objects.get(
                    product=product.id, user=request.user)
                favorite.delete()
                liked = False
            except FavoriteProduct.DoesNotExist:

                new_favorite = FavoriteProduct()
                new_favorite.user = request.user
                new_favorite.product = product
                new_favorite.save()

            count = FavoriteProduct.objects.filter(
                user=request.user).count()
            return Response({'liked': liked, 'count': count})
    return Response({'messages': "login_required"})


class PaymentView(generic.FormView):
    template_name = 'payment.html'
    form_class = PaymentForm

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context["object"] = get_or_set_order_session(self.request)
        return context


def payment_information(request):
    form = CustommerInformationForm()
    if request.method == "GET":
        if (request.user.is_authenticated):
            form = CustommerInformationForm(instance=request.user)
        user_info = None
        if ('user_info' in request.session):
            user_info = request.session['user_info']

        districts = District.objects.all()
        cities = City.objects.all()
        return render(request, 'payment_information.html', {'form': form,
                                                            'user_info': user_info,
                                                            'districts': districts,
                                                            'cities': cities})

    if request.method == "POST":
        request.session['user_info'] = request.POST

        return redirect("/cart/payment_products")
    return redirect('/cart/payment_information')


def payment_products(request):

    user_info = request.session.get('user_info')
    cart = get_or_set_order_session(request)
    district = District.objects.get(
        id=user_info['district'])
    ship = district.ship_fee
    user_info['totalprice'] = cart.get_total_price + ship
    address = request.session['user_info']['address'] + " , " + \
        district.name+" , "+district.city.name
    user_info['ship'] = ship

    return render(request, 'payment_products.html', {'object': cart, 'user_info': user_info, 'address': address})


def payment_process(request):
    if (request.method == 'POST'):
        payment = None
        # Create Payment
        try:

            user = request.session['user_info']
            district = District.objects.get(
                id=user['district'])

            payment = Payment.objects.create()
            user_info = CustommerDetail.objects.create()
            user_info.payment = payment
            user_info.full_name = user['full_name']
            user_info.email = user['email']
            user_info.mobile = user['mobile']
            user_info.dictrict = district.name
            user_info.city = district.city.name
            user_info.address = user['address']

            user_info.save()
            print(1)
            # Create Product details
            cart = get_or_set_order_session(request)
            total_price = 0
            print(cart)

            for item in cart.items.all():
                total_price = total_price + item.get_total_item_price()
                product = ProductDetail(payment=payment,
                                        product_id=item.product.id,
                                        product_name=item.product.title,
                                        image=item.product.images.first,
                                        product_amount=item.quantity,
                                        product_price=item.product.price,
                                        product_promotion=item.product.promotion)
                product.save()
            print(3)

            payment.amount = total_price+request.session['user_info']['ship']

            payment.ship = request.session['user_info']['ship']
            payment.note = request.POST.get('note')
            if (request.user.is_authenticated):
                payment.user = request.user

            payment.save()
            cart.delete()
            request.session['products_in_cart'] = 0
            messages.success(request, "payment successfully")
            return render(request, 'payment_process.html', {'success': True})
        except:
            # Delete payment

            if (payment is not None):
                payment.delete()
            return render(request, 'payment_process.html', {'success': False})
            pass
    else:
        return redirect('/')


def review(request):
    if (request.method == 'POST'):
        print(request.POST)
        product = get_object_or_404(Product, pk=request.POST['product'])
        params = request.POST
        review = Review.objects.create(product=product,
                                       full_name=params['full_name'], subject=params['subject'], content=params['content'], rating=params['rating'])
        print(request.POST)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

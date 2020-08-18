from django.shortcuts import render, redirect
from django.views import generic
from .utils import get_or_set_order_session, get_or_set_favorite_session
from django.shortcuts import get_object_or_404, reverse
from .forms import AddToCartForm, PaymentForm, CustommerInformationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

from .models import Product, OrderItem, FavoriteProduct, Payment, CustommerDetail, ProductDetail
from django.utils.decorators import method_decorator
from .choices import limit_choices as l, price_choices, sort_choice


class ProductListView(generic.TemplateView):
    template_name = 'product_list.html'

    def get_context_data(self, **kwargs):
        limit = 1
        if ('limit' in self.request.GET):
            limit = self.request.GET['limit']
        products = Product.objects.all()

        # Category
        category = ''
        if "category" in self.request.GET:
            category = self.request.GET['category']
            if category:
                products = products.filter(category=category)

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

        # Choices
        limit_choices = l
        context['limit'] = limit
        context['limit_choices'] = limit_choices
        context['sort_choices'] = sort_choice
        context['sort'] = sort
        context['category'] = category
        context['search'] = search
        context['liked'] = liked

        return context


class ProductDetailView(generic.FormView):
    template_name = 'product.html'
    form_class = AddToCartForm

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs["slug"])

    def get_success_url(self):
        return reverse("cart:summary")
        # return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

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
        context['object'] = self.get_object()
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


class TymOrUnTym(generic.View):
    @ method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['product_id'])
        try:

            favorite = FavoriteProduct.objects.get(
                product=product.id, user=request.user)
            print("Delete")
            favorite.delete()
        except FavoriteProduct.DoesNotExist:
            print("add new")
            new_favorite = FavoriteProduct()
            new_favorite.user = request.user
            new_favorite.product = product
            new_favorite.save()

        request.session['products_in_favorite'] = FavoriteProduct.objects.filter(
            user=request.user).count()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # if favorite_item:
        #     favorite_item.delete()
        # else:
        #     favorite = get_or_set_favorite_session(self.request)
        #     product = self.get_object()

        #     new_tym = Favorite()
        #     new_tym.product = product
        #     new_tym.order = favorite
        #     new_tym.save()


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
            form = CustommerInformationForm(initial={
                                            'full_name': request.user.username, 'email': request.user.email, 'mobile': request.user.mobile})

        user_info = None

        if ('user_info' in request.session):
            user_info = request.session['user_info']

        return render(request, 'payment_information.html', {'form': form, 'user_info': user_info})

    if request.method == "POST":
        request.session['user_info'] = request.POST

        print("POST")
        print(request.session['user_info'])

        return redirect("/cart/payment_products")

    return redirect('/cart/payment_information')


def payment_products(request):
    cart = get_or_set_order_session(request)
    return render(request, 'payment_products.html', {'object': cart})


def payment_process(request):
    if (request.method == 'POST'):
        payment = None

        # Create Payment
        try:
            payment = Payment.objects.create()

            user = request.session['user_info']
            print(user)
            user_info = CustommerDetail.objects.create(
                full_name=user['full_name'], email=user['email'], mobile=user['mobile'], payment=payment)
            print("ahih")
            if (request.user.is_authenticated):
                print(11)
                user_info.user = request.user
            print(1)
            user_info.save()
            print(2)
            # Create Product details
            cart = get_or_set_order_session(request)
            total_price = 0
            for item in cart.items.all():
                # print(100)
                # print(item.product.id)
                # print(item.product.title)
                # print(item.quantity)
                # print(item.product.price)
                # print(item.product.promotion)
                total_price = total_price + item.get_total_item_price()
                product = ProductDetail(payment=payment, product_id=item.product.id, product_name=item.product.title,
                                        product_amount=item.quantity, product_price=item.product.price, product_promotion=item.product.promotion)
                product.save()
            print(cart.items.all())
            print(3)
            payment.amount = total_price
            if (request.user.is_authenticated):
                payment.user = request.user
            payment.save()

            cart.delete()
            request.session['products_in_cart'] = 0

            return render(request, 'payment_process.html', {'success': True})
        except:
            # Delete payment
            if (payment is not None):
                payment.delete()

            return render(request, 'payment_process.html', {'success': False})
            pass

    else:
        return redirect('/')

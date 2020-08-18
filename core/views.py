from django.core.mail import send_mail
from django.shortcuts import reverse, render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views import generic
from .forms import ContactForm
from cart.models import Product, FavoriteProduct
from .models import Contact


class HomeView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        products = Product.objects.filter(active=True)[:4]
        context['products'] = products
        liked = []
        if self.request.user.is_authenticated:
            for like_item in FavoriteProduct.objects.filter(user=self.request.user):
                liked.append(like_item.product.id)

            self.request.session['products_in_favorite'] = FavoriteProduct.objects.filter(
                user=self.request.user).count()

        context['liked'] = liked

        return context


class ContactView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'contact.html')

    def post(self, request, *args, **kwargs):

        new_contact = Contact()
        new_contact.first_name = request.POST.get('firstname')
        new_contact.last_name = request.POST.get('lastname')
        new_contact.email = request.POST.get('email')
        new_contact.phone = request.POST.get('phone')
        new_contact.subject = request.POST.get('subject')
        new_contact.message = request.POST.get('message')
        new_contact.save()
        subject = request.POST.get('email')+" vừa gửi 1 câu chửi tới sếp"
        message = " nội dung Lời chửi bới" + request.POST.get('message')
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject=subject,
                  message=message,
                  from_email=from_email,
                  recipient_list=['minhthienpham0611@gmail.com'],
                  fail_silently=False,
                  auth_user=None,
                  auth_password=None,
                  html_message=None
                  )
        messages.success(request, " update successfully !")

        return redirect('/contact')


class AboutView(generic.TemplateView):
    template_name = 'about.html'


class TymView(generic.TemplateView):
    template_name = 'tym.html'

    # @login_required
    def get_context_data(self, **kwargs):
        context = super(TymView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            favorites = FavoriteProduct.objects.filter(user=self.request.user)
            context['favorites'] = favorites
        else:
            context['favorites'] = None

        return context
# Create your views here.

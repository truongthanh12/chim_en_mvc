from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import RegisterForm, LoginForm, CustomUserChangeForm, CustomPasswordChangeForm, CustomPasswordResetForm, AddressChangeForm, ChangeEmailForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

# Create your views here.

# Send email Token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core import mail
from django.conf import settings
from django.utils.html import strip_tags
from cart.models import Address, Payment, City, District

from .models import User as UserModel
from django.core.exceptions import ObjectDoesNotExist


def login(request):
    if request.method == "GET":
        next = ''
        if 'next' in request.GET:
            next = request.GET['next']
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form, 'next': next})
    form = LoginForm(request.POST)
    if form.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            next_url = request.GET.get('next')

            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                messages.success(request, "Login success!")
                return redirect('/')
        else:
            messages.warning(request, "wrong info")
            return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})
    return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})


def logout(request):
    auth_logout(request)
    messages.success(request, 'Logout success')
    return redirect('/accounts/login')


def register(request):
    if (request.user.is_authenticated):
        return redirect("index")

    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'accounts/register.html', {'form': form})

    form = RegisterForm(request.POST)
    if form.is_valid():

        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(request)

        subject = 'Activate your account'
        html_message = render_to_string(
            'accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = request.POST['email']

        try:
            mail.send_mail(subject=subject, message=plain_message, from_email=from_email, fail_silently=False,
                           auth_user=None,
                           auth_password=None,
                           recipient_list=[to], html_message=html_message)
            messages.success(
                request, 'Please confirm your email address to complete the registration')
            return redirect('register')
        except:
            return redirect('register')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == "GET":
        form = CustomUserChangeForm(instance=request.user)

        return render(request, 'accounts/profile.html', {'form': form, 'url': 'profile'})
    form = CustomUserChangeForm(data=request.POST, instance=request.user)

    if form.is_valid():
        user = form.save(commit=False)
        if request.POST.get('city'):
            city = City.objects.get(id=request.POST.get('city'))
            user.city = city
        if request.POST.get('district'):
            district = District.objects.get(id=request.POST.get('district'))
            user.district = district

        user.save()
        messages.success(request, " update successfully !")

    return redirect('/accounts/profile', {'url': 'profile'})


@ login_required
def AddressView(request):
    try:
        address = Address.objects.get(user=request.user)
    except ObjectDoesNotExist:
        address = Address()
    if request.method == "GET":
        form = AddressChangeForm(instance=address)
        return render(request, 'accounts/address.html', {'form': form})
    form = AddressChangeForm(data=request.POST, instance=address)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, " update successfully !")

    return redirect('/accounts/profile/address')


@ login_required
def changePassword(request):
    if request.method == "GET":
        form = CustomPasswordChangeForm(request.user)
        return render(request, 'accounts/password_change.html', {'form': form,  'url': 'change-password'})

    form_edit_password = CustomPasswordChangeForm(
        request.user, data=request.POST)
    if form_edit_password.is_valid():
        form_edit_password.save()
        messages.success(request, " update successfully !")
        return redirect('/accounts/profile')
    else:
        messages.warning(request, "password wrong format !")
        return render(request, 'accounts/password_change.html', {'form': form_edit_password, 'url': 'change-password'})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        messages.success(request, " Now you can login your account")
        return redirect('/accounts/login')
    else:
        return HttpResponse('Activation link is invalid!')


def verify_change_email(request, user):

    user = UserModel.objects.get(pk=user)
    if user and request.GET.get('new_email'):
        user.email = request.GET.get('new_email')
        user.save()
        messages.success(request, " change email successfully !")
        return redirect('/')
    else:
        return HttpResponse('This  link is invalid!')


@ login_required
def user_payments(request):
    if (request.method == 'GET'):
        payments = Payment.objects.filter(user=request.user)

        context = {
            'payments': payments,
            'url': 'payment'
        }
        return render(request, 'accounts/user_payments.html', context)


@ login_required
def user_payment(request, id):
    if (request.method == 'GET'):
        payment = get_object_or_404(Payment, pk=id)

        if (payment.user != request.user):
            return redirect('/')
        return render(request, 'accounts/user_payment.html', {'payment': payment, 'url': 'payment'})


@ login_required
def change_email(request):
    if request.method == "GET":
        form = ChangeEmailForm()
        return render(request, 'accounts/change_email.html', {'form': form, 'url': 'change-email'})

    form = ChangeEmailForm(request.POST)
    if form.is_valid():

        user = request.user
        current_site = get_current_site(request)
        print(current_site)
        subject = 'Change new email'
        html_message = render_to_string(
            'accounts/verify_change_email.html', {
                'user': user.id,
                'domain': current_site.domain,
                'new_email': request.POST['email']
            })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = request.POST['email']

        try:
            mail.send_mail(subject=subject, message=plain_message, from_email=from_email, fail_silently=False,
                           auth_user=None,
                           auth_password=None,
                           recipient_list=[to], html_message=html_message)
            messages.success(
                request, "Please confirm your email address to complete the change email")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            return render(request, 'accounts/change_email.html', {'form': form})

        # messages.success(request, 'Register success')

    return render(request, 'accounts/change_email.html', {'form': form, 'url': 'change-email'})

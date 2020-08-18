from django.urls import path
from . import views
from .API import apis
app_name = 'cart'

urlpatterns = [
    path('payment', views.PaymentView.as_view(), name='payment'),
    path('payment_information/', views.payment_information,
         name='payment_information'),
    path('payment_process/', views.payment_process,
         name='payment_process'),
    path('payment_products/', views.payment_products,
         name='payment_products'),
    path('', views.CartView.as_view(), name='summary'),
    path('shop/', views.ProductListView.as_view(), name='product-list'),
    path('<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('increase-quantity/<pk>', views.IncreaseQuantityView.as_view(),
         name='increase-quantity'),
    path('descrease-quantity/<pk>', views.DecreaseQuantityView.as_view(),
         name='descrease-quantity'),
    path('remove_from_cart/<pk>', views.RemoveFromCartView.as_view(),
         name='remove_from_cart'),
    path('check_out/', views.CheckOutView.as_view(), name='check_out'),
    path('tym_or_unTym/<product_id>',
         views.TymOrUnTym, name='tym'),

    path('review', views.review, name='review')
]

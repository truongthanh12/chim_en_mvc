from django import forms
from .models import OrderItem, ColorVariation, Product, SizeVariation, FavoriteProduct, Payment, Address, CustommerDetail, ProductDetail


class AddToCartForm(forms.ModelForm):
    # color = forms.ModelChoiceField(queryset=ColorVariation.objects.none())
    # size = forms.ModelChoiceField(queryset=SizeVariation.objects.none())
    class Meta:
        model = OrderItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id')
        product = Product.objects.get(id=product_id)
        super().__init__(*args, **kwargs)

        # self.fields['color'].queryset = product.available_colors.all()
        # self.fields['size'].queryset = product.available_sizes.all()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'


class CustommerInformationForm(forms.ModelForm):
    class Meta:
        model = CustommerDetail
        fields = ('full_name', 'email',
                  'mobile', 'city', 'dictrict', 'address')

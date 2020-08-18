from ..models import ProductImage, Payment, Product, Address, ColorVariation, SizeVariation, OrderItem, Order, Payment,  Favorite, FavoriteProduct, Category, BlogImage, City, District, CustommerDetail, ProductDetail
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    products = serializers.StringRelatedField(many=True)

    class Meta:
        model = Payment
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'product', 'image')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = '__all__'


class ProductInlineSerializer(serializers.ModelSerializer):
    images = ProductImageInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'images', 'sku')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductInlineSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    items = OrderItemSerializer(read_only=True, many=True)
    get_total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = '__all__'


class CustommerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustommerDetail
        fields = '__all__'


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    customer_details = CustommerDetailSerializer(read_only=True, many=True)
    product_details = ProductDetailsSerializer(read_only=True, many=True)

    class Meta:
        model = Payment
        fields = '__all__'


class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'product', 'image')


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ('id', 'image', 'product')

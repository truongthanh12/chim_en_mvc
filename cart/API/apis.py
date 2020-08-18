from ..models import Payment, Product, ColorVariation, SizeVariation, OrderItem, Order, Payment,  Favorite, FavoriteProduct, ProductImage, BlogImage, Category, City, District
from .serializers import PaymentSerializer, ProductSerializer, OrderItemSerializer, OrderSerializer, ProductImageSerializer, FavoriteProductSerializer, BlogImageSerializer, CategorySerializer, CitySerializer, DistrictSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from ecom.helpers import modify_input_for_multiple_files, modify_input_for_single_image
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

import json

from django.http import HttpResponse

from accounts.models import User


def dash_board(request):
    if (request.method == 'GET'):
        users = User.objects.count()
        products = Product.objects.count()
        payments = Payment.objects.count()

        return HttpResponse(json.dumps({'users': users, 'payments': payments, 'products': products}), status=200)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['status', 'note']

    search_fields = ['status']


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['title', 'active']

    search_fields = ['title']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.DjangoObjectPermissions]
    permission_classes = [permissions.DjangoModelPermissions]

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['title']

    search_fields = ['title']


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['']

    search_fields = ['']


class ProductImageView(APIView):

    def get(self, request):
        all_images = ProductImage.objects.all()
        serializer = ProductImageSerializer(all_images, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, *args, **kwargs):
        parser_classes = (MultiPartParser, FormParser)

        product_id = request.data['product']
        product = get_object_or_404(Product, pk=product_id)

        # converts querydict to original dict
        images = dict((request.data).lists())['images']
        flag = 1
        arr = []
        for img_name in images:
            modified_data = modify_input_for_multiple_files(
                product_id, img_name)
            file_serializer = ProductImageSerializer(data=modified_data)
            if file_serializer.is_valid():
                file_serializer.save()
                arr.append(file_serializer.data)
            else:
                flag = 0

        if flag == 1:
            return Response(arr, status=status.HTTP_201_CREATED)
        else:
            return Response(arr, status=status.HTTP_400_BAD_REQUEST)

    def delete(selt, request, *args, **kwargs):
        parser_classes = (JSONParser,)

        print(request.data)
        if 'ids' in request.data:
            image_ids = request.data['ids']
            images = ProductImage.objects.filter(id__in=image_ids)
            try:
                images.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogImageViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)

    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        print(request.data['image'])
        image = request.data['image']
        try:
            image = BlogImage.objects.create(image=image)
            print(3)
            print(image.image.url)
            return HttpResponse(json.dumps({'id': image.id, 'data': {"location": 'http://localhost:8000' + image.image.url}}), status=200)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)

    search_fields = ['name']


class DistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['name']

    search_fields = ['name']

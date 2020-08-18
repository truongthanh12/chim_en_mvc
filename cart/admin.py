from django.contrib import admin
from .models import SizeVariation, Product, Order, OrderItem, Payment, ColorVariation, ProductImage, Category, Address, City, District, CustommerDetail, ProductDetail, Review, Reply


class ProductImageInline(admin.TabularInline):
    extra = 1
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductImageInline,)


admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(ColorVariation)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(City)
admin.site.register(District)
admin.site.register(CustommerDetail)
admin.site.register(ProductDetail)


class ReplyInline(admin.TabularInline):
    extra = 1
    model = Reply


class ReviewAdmin(admin.ModelAdmin):
    inlines = (ReplyInline,)


admin.site.register(Review, ReviewAdmin)


# Register your models here.

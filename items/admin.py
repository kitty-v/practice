from django.contrib import admin
from .models import Category, Item, ItemImage, Favorite, Message

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order')
    prepopulated_fields = {'slug': ('name',)}

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'condition', 'status', 'seller', 'created_at')
    list_filter = ('status', 'condition', 'category')
    search_fields = ('title', 'description', 'seller__username')
    inlines = [ItemImageInline]

@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('item', 'is_primary', 'uploaded_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'item', 'is_read', 'created_at')
    list_filter = ('is_read',)

from django.contrib import admin
from .models import Category, Blog, Rating, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'views')
    list_filter = ('status', 'category', 'created_at', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'created_at')
    list_filter = ('created_at',)

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('authors/', views.authors_view, name='authors'),
    path('create/', views.blog_create_view, name='create'),
    path('my-blogs/', views.my_blogs_view, name='my_blogs'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='detail'),
    path('blog/<slug:slug>/edit/', views.blog_edit_view, name='edit'),
    path('blog/<slug:slug>/delete/', views.blog_delete_view, name='delete'),
    path('blog/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('blog/<slug:slug>/rate/', views.rate_blog, name='rate_blog'),
]

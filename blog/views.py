from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Blog, Category, Rating, Favorite
from .forms import BlogForm, CategoryForm

User = get_user_model()

def home_view(request):
    blogs = Blog.objects.filter(status='published').select_related('author', 'category').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) | 
            Q(body__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        blogs = blogs.filter(category_id=category_id)
    
    # Author filter
    author_id = request.GET.get('author')
    if author_id:
        blogs = blogs.filter(author_id=author_id)
    
    # Sort by rating
    sort_by = request.GET.get('sort')
    if sort_by == 'rating':
        blogs = blogs.annotate(avg_rating=Avg('ratings__score')).order_by('-avg_rating', '-created_at')
    elif sort_by == 'views':
        blogs = blogs.order_by('-views', '-created_at')
    
    # Pagination
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and authors for filters
    categories = Category.objects.all()
    authors = User.objects.filter(role__in=['author', 'admin'], blogs__status='published').distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'authors': authors,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_author': author_id,
        'sort_by': sort_by,
    }
    return render(request, 'blog/home.html', context)

def blog_detail_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    
    # Increment views
    blog.views += 1
    blog.save(update_fields=['views'])
    
    # Get user's rating if authenticated
    user_rating = None
    is_favorited = False
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(blog=blog, user=request.user)
        except Rating.DoesNotExist:
            pass
        is_favorited = Favorite.objects.filter(blog=blog, user=request.user).exists()
    
    # Get recent blogs by same author
    related_blogs = Blog.objects.filter(
        author=blog.author, 
        status='published'
    ).exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'user_rating': user_rating,
        'is_favorited': is_favorited,
        'related_blogs': related_blogs,
    }
    return render(request, 'blog/detail.html', context)

@login_required
def blog_create_view(request):
    if request.user.role not in ['author', 'admin']:
        messages.error(request, 'You need to be an author to create blogs.')
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Blog created successfully!')
            return redirect('blog:detail', slug=blog.slug)
    else:
        form = BlogForm()
    
    return render(request, 'blog/create.html', {'form': form})

@login_required
def blog_edit_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog updated successfully!')
            return redirect('blog:detail', slug=blog.slug)
    else:
        form = BlogForm(instance=blog)
    
    return render(request, 'blog/edit.html', {'form': form, 'blog': blog})

@login_required
def blog_delete_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully!')
        return redirect('blog:my_blogs')
    
    return render(request, 'blog/delete.html', {'blog': blog})

@login_required
def my_blogs_view(request):
    if request.user.role not in ['author', 'admin']:
        messages.error(request, 'You need to be an author to access this page.')
        return redirect('blog:home')
    
    blogs = Blog.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/my_blogs.html', {'page_obj': page_obj})

def authors_view(request):
    authors = User.objects.filter(
        role__in=['author', 'admin'],
        blogs__status='published'
    ).distinct().order_by('first_name', 'last_name')
    
    # Pagination
    paginator = Paginator(authors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/authors.html', {'page_obj': page_obj})

@login_required
@require_POST
def toggle_favorite(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    favorite, created = Favorite.objects.get_or_create(user=request.user, blog=blog)
    
    if not created:
        favorite.delete()
        is_favorited = False
        message = 'Removed from favorites'
    else:
        is_favorited = True
        message = 'Added to favorites'
        
        # Send email notification (simplified for console backend)
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'You favorited: {blog.title}'
        message_body = f'''
        Hi {request.user.get_full_name()},
        
        You have added "{blog.title}" by {blog.author.get_full_name()} to your favorites.
        
        You can view all your favorites at: {request.build_absolute_uri('/accounts/favorites/')}
        
        Best regards,
        Blog Site Team
        '''
        
        send_mail(
            subject,
            message_body,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=True,
        )
    
    return JsonResponse({
        'is_favorited': is_favorited,
        'message': message
    })

@login_required
@require_POST
def rate_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    score = int(request.POST.get('score', 0))

    if not (0 <= score <= 6):
        return JsonResponse({'error': 'Invalid rating score'}, status=400)

    rating, created = Rating.objects.get_or_create(
        blog=blog,
        user=request.user,
        defaults={'score': score}
    )

    if not created:
        rating.score = score
        rating.save()

    return JsonResponse({
        'success': True,
        'average_rating': blog.get_average_rating(),
        'rating_count': blog.get_rating_count(),
        'user_rating': score
    })




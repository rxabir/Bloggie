from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Blog, Category

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'body', 'category', 'featured_image', 'status']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 15, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'category',
            'body',
            'featured_image',
            'status',
            Submit('submit', 'Save Blog', css_class='btn btn-primary me-2'),
        )
    
    def save(self, commit=True):
        blog = super().save(commit=False)
        if not blog.slug:
            blog.slug = slugify(blog.title)
            # Ensure unique slug
            original_slug = blog.slug
            counter = 1
            while Blog.objects.filter(slug=blog.slug).exists():
                blog.slug = f"{original_slug}-{counter}"
                counter += 1
        if commit:
            blog.save()
        return blog

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Submit('submit', 'Save Category', css_class='btn btn-primary')
        )


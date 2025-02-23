from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, Tag, Profile, Comment
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . import forms
import datetime

# Create your views here.
def homepage(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'socialapp/base.html', {
        'categories': categories,
        'tags': tags
    })

def home_page_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    tags = Tag.objects.all()
    form = forms.SearchForm(request.GET)

    if form.is_valid():
        search_query = form.cleaned_data.get('search', '').strip()
        author_query = form.cleaned_data.get('author', '').strip()
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        media_type = form.cleaned_data.get('media_type')

        if search_query:
            if search_query.capitalize() in [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]:
                month_number = datetime.datetime.strptime(search_query, "%B").month
                posts = posts.filter(created_at__month=month_number)
            else:
                posts = posts.filter(
                    content__icontains=search_query
                ) | posts.filter(title__icontains=search_query)

        if author_query:
            posts = posts.filter(author__username__icontains=author_query)

        if date_from:
            posts = posts.filter(created_at__date__gte=date_from)
        if date_to:
            posts = posts.filter(created_at__date__lte=date_to)

        if media_type:
            if media_type == 'image':
                posts = posts.filter(image__isnull=False)
            elif media_type == 'video':
                posts = posts.filter(video__isnull=False)
            elif media_type == 'text':
                posts = posts.filter(image__isnull=True, video__isnull=True)

    query = request.GET.get('query', '').strip()
    if query:
        posts = posts.filter(title__icontains=query)

    print(posts.query)  # Debugging

    return render(request, 'socialapp/home_page_posts.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'form': form,
    })


@login_required(login_url='user_login')
def post_details(request, id):
    post = Post.objects.get(id=id)
    return render(request, 'socialapp/post_details.html', {
        'post': post
    })

@login_required
def create_post(request):
    if request.method == "POST":
        form = forms.PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('home_page_posts')
    else:
        form = forms.PostForm()
    return render(request, 'socialapp/create_post.html', {'form': form})

@login_required
def update_post(request, id):
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        messages.error(request, "You can only edit your own posts.")
        return redirect('home_page_posts')

    if request.method == "POST":
        form = forms.PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            if not request.FILES.get('image'): 
                form.instance.image = post.image
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('home_page_posts')
    else:
        form = forms.PostForm(instance=post)
    
    return render(request, 'socialapp/update_post.html', {'form': form})


@login_required(login_url='user_login')
def like_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('home_page_posts')

@login_required(login_url='user_login')
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == "POST":
        comment_text = request.POST.get("comment").strip()
        if comment_text:
            Comment.objects.create(post=post, user=request.user, content=comment_text)
    return redirect('home_page_posts')


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        messages.error(request, "You can only delete your own posts.")
        return redirect('home_page_posts')

    post.delete()
    messages.success(request, "Post deleted successfully!")
    return redirect('home_page_posts')

@login_required(login_url='user_login')
def category_posts(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category)
    return render(request, 'socialapp/category_posts.html', {'category': category, 'posts': posts})


@login_required(login_url='user_login')
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    return render(request, 'socialapp/profile.html', {'profile': profile, 'posts': posts})

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = forms.ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile", user_id=request.user.id)  # Redirect to profile page

    else:
        form = forms.ProfileForm(instance=profile)

    return render(request, "socialapp/edit_profile.html", {"form": form})

def post_list(request):
    posts = Post.objects.all()
    form = forms.PostFilterForm(request.GET)

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        author = form.cleaned_data.get('author')
        media_type = form.cleaned_data.get('media_type')
        date = form.cleaned_data.get('date')

        if keyword:
            posts = posts.filter(title__icontains=keyword) | posts.filter(content__icontains=keyword)
        if author:
            posts = posts.filter(author=author)
        if media_type == "image":
            posts = posts.exclude(image="")
        elif media_type == "text":
            posts = posts.filter(image="")
        if date:
            posts = posts.filter(created_at__date=date)

    return render(request, 'socialapp/home.html', {'posts': posts, 'form': form})


@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if comment.user != request.user:
        messages.error(request, "You can only delete your own comments.")
        return redirect('home_page_posts')

    comment.delete()
    messages.success(request, "Comment deleted successfully!")
    return redirect('home_page_posts')


def sign_up(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sign Up Successfully")
            return redirect('home_page_posts')
    else:
        form = forms.SignUpForm()
    return render(request, 'socialapp/sign_up.html', {'form': form})


def user_login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username = username, password = password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login Success')
                return redirect('home_page_posts')
            else:
                messages.error(request, 'Login Unsuccessful. Try Again :(')

    return render(request, 'socialapp/user_login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Successfully Logout')
    return redirect('home_page_posts')
from django import forms
from . import models
from django.forms.widgets import DateInput, TimeInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PostForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ['title', 'content', 'category', 'image']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ["profile_picture", "bio"]

class PostFilterForm(forms.Form):
    keyword = forms.CharField(required=False, label="Search", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search posts...'}))
    author = forms.ModelChoiceField(queryset=models.Post.objects.values_list('author', flat=True).distinct(), required=False, label="Author", widget=forms.Select(attrs={'class': 'form-control'}))
    media_type = forms.ChoiceField(choices=[('', 'All'), ('image', 'Image'), ('text', 'Text')], required=False, label="Media Type", widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.DateField(required=False, label="Date", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control me-sm-2', 'placeholder': 'Search...'})
    )
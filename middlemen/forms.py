from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Product, RestaurantRequest, Message


class SignUpForm(forms.ModelForm):
    ROLE_CHOICES = [('producer', 'Producer'), ('buyer', 'Buyer')]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='buyer')
    business_name = forms.CharField(max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Green Farm LLC'}))
    city = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Portland'}))
    state = forms.CharField(max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'OR'}))
    zip_code = forms.CharField(max_length=10, required=False,
        widget=forms.TextInput(attrs={'placeholder': '97201'}))
    password1 = forms.CharField(label='Password', min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Min 6 characters'}))
    password2 = forms.CharField(label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'John'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Doe'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'username':   forms.TextInput(attrs={'placeholder': 'Choose a username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))
    remember_me = forms.BooleanField(required=False)


class ProfileEditForm(forms.ModelForm):
    """
    business_name = forms.CharField(max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your Business Name'}))
    city = forms.CharField(max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(max_length=2, required=False,
        widget=forms.TextInput(attrs={'placeholder' : "State e.g. 'NE'"}))
    zip_code = forms.CharField(max_length=5, require=False,
        widget=forms.TextInput(attrs={'placeholder':'12345'}))
    bio = forms.CharField(max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your Bio'}))
    avatar = forms.ImageField() """
    email = forms.CharField(max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}))

    class Meta:
        model = Profile
        fields = ['business_name', 'city', 'state', 'zip_code', 'bio', 'avatar']
        widgets = {
            'business_name': forms.TextInput(attrs={'placeholder': 'Your business name'}),
            'city':          forms.TextInput(attrs={'placeholder': 'City'}),
            'state':         forms.TextInput(attrs={'placeholder': 'State'}),
            'zip_code':      forms.TextInput(attrs={'placeholder': 'Zip'}),
            'bio':           forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell buyers about your business...'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'organic', 'category', 'description', 'price', 'weight', 'available', 'image']
        help_texts = {'weight' : "lb(s)"}
        widgets = {
            'name':        forms.TextInput(attrs={'placeholder': 'e.g. Organic Tomatoes'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your product...'}),
            'price':       forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'weight':        forms.NumberInput(attrs={'placeholder': '0'}),
        }


class RestaurantRequestForm(forms.ModelForm):
    class Meta:
        model = RestaurantRequest
        fields = ['title', 'category', 'description', 'budget_min', 'budget_max']
        widgets = {
            'title':       forms.TextInput(attrs={'placeholder': 'e.g. Looking for organic tomatoes'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe what you need...'}),
            'budget_min':  forms.NumberInput(attrs={'placeholder': '500', 'step': '0.01', 'min': '0'}),
            'budget_max':  forms.NumberInput(attrs={'placeholder': '1000', 'step': '0.01', 'min': '0'}),
        }

class BrowseFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'All Categories')] + [
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Dairy & Eggs', 'Dairy & Eggs'),
        ('Meat & Poultry', 'Meat & Poultry'),
    ]
    SORT_CHOICES = [
        ('name', 'Name A–Z'),
        ('price', 'Price: Low to High'),
        ('-price', 'Price: High to Low'),
    ]

    search   = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    state    = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'State e.g. OR'}))
    max_price = forms.DecimalField(required=False, min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Max price', 'step': '0.01'}))
    available_only = forms.BooleanField(required=False)
    sort     = forms.ChoiceField(choices=SORT_CHOICES, required=False)

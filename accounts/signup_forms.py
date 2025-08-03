from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from allauth.account.forms import SignupForm

User = get_user_model()

class CustomSignupForm(SignupForm):
    """Custom signup form that adds a mobile number field."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}
        )
    )
    
    phone_regex = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Mobile number must be 10 digits long and start with 6-9"
    )
    mobile_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter 10 digit mobile number'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

    def save(self, request):
        """Save the user with mobile number."""
        user = super().save(request)
        user.mobile_number = self.cleaned_data['mobile_number']
        user.save()
        return user 
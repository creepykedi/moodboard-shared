from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Img, TheMoodboard
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# overwrite default register to show email
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email',
                             error_messages={'exists': 'This email already exists'})
    class Meta:
        model = User
        fields = ('email', 'username')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError(self.fields['email'].error_messages['exists'])
        return self.cleaned_data['email']



class UserUpdateForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ('password1', 'password2')
        fields = ['email', 'username']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
       # del self.fields['password1']
       # del self.fields['password2']
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        self.fields['password1'].help_text = 'Enter your password to confirm changes'

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UploadImgForm(ModelForm):
    class Meta:
        model = Img
        fields = ['image', 'url_img', 'moodboard']
        labels = {
            'image': 'Upload image',
            'moodboard': 'To Moodboard',
            'url_img': 'Link to image'
        }

    def __init__(self, user, *args, **kwargs):
        super(UploadImgForm, self).__init__(*args, **kwargs)  # populates the post
        # limit uploading to user owned moodboards
        self.fields['moodboard'].queryset = TheMoodboard.objects.filter(owner=user)


# form to create Moodboard
class TheMoodboardForm(ModelForm):
    class Meta:
        model = TheMoodboard
        readonly_fields = 'date_created'
        fields = ['projectName', 'picsContained', 'isPrivate', 'owner']
        exclude = ['picsContained', 'owner']
        labels = {
            'projectName': 'Moodboard name',
            'isPrivate': 'Private',
        }

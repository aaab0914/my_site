from django import forms
# forms: Django's form handling module for creating and validating forms

from .models import Comment
# Comment: The comment model (imported from the current app)

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'body']

class SearchForm(forms.Form):
    query = forms.CharField()
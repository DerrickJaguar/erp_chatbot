from django import forms

class ChatMessageForm(forms.Form):
    step = forms.IntegerField()
    message = forms.CharField(max_length=1000)

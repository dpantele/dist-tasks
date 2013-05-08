# Create your views here.
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.views.generic import FormView

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

    def __init__(self, password_optional=False, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        if password_optional:
            self.fields['password'].required = False

class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        if self.request.method == 'POST' and self.request.POST.get('recover', False):
            kwargs['password_optional'] = True

        return kwargs


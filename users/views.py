# Create your views here.
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import int_to_base36
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from users.models import MyUser
from django.utils.translation import ugettext, ugettext_lazy as _



class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

    error_messages = {
        'invalid_login': _("Please enter a correct email and password. "
                           "Note that password is case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is blocked. Please, contact out support."),
    }

    def __init__(self, request=None, password_optional=False, *args, **kwargs):
        self.user_cache = None
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

        if password_optional:
            self.fields['password'].required = False

    def clean(self):
        username = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login']
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])

        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(self.error_messages['no_cookies'])

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'

    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs['request'] = self.request
        if self.request.method == 'POST' and self.request.POST.get('recover', False):
            kwargs['password_optional'] = True

        return kwargs

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_success_url())

        return super(LoginView, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        if form.get_user():
            return self.login_user(form.get_user())
        else:
            return self.email_login(form.cleaned_data.get('email'))

    def login_user(self, user):
        login(self.request, user)
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return HttpResponseRedirect(reverse('home'))

    def email_login(self, email):
        user, created = MyUser.objects.get_or_create(email=email, defaults={'password': make_password(None)})
        context = {
            'domain': self.request.get_host(),
            'uid': int_to_base36(user.pk),
            'token': default_token_generator.make_token(user),
        }




class ManagerHome(TemplateView):
    template_name = 'manager_home.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ManagerHome, self).dispatch(request, *args, **kwargs)
    
    
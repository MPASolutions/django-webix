import re
from functools import update_wrapper
from weakref import WeakSet

from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db.models.base import ModelBase
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, resolve, reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django.utils.text import capfirst
from django.utils.translation import get_language, gettext, gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django_webix.contrib.admin import ModelWebixAdmin

all_sites = WeakSet()


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class AdminWebixSite:
    # Text to put at the end of each page's <title>.
    site_title = _("Django webix site admin")

    # Text to put in each page's <h1>.
    site_header = _("Django webix administration")

    # Text to put at the top of the admin index page.
    index_title = _("Site administration")

    site_url = "/"

    urls_namespace = "dwadmin"

    login_form = None

    label_width = None

    webix_container_id = "content_right"
    webix_menu_type = "menu"  # ['menu', 'sidebar']

    webix_menu_width = 180

    index_template = None
    login_template = None
    logout_template = None
    dashboard_template = "django_webix/admin/dashboard.js"
    password_change_template = None
    password_change_done_template = None

    def __init__(self, name="dwadmin"):
        self._registry = {}
        self.name = name
        all_sites.add(self)

    def model_admin_menu(self):
        from django_webix.contrib.admin.models import WebixAdminMenu

        return WebixAdminMenu

    def get_label_width(self):
        return self.label_width

    def is_hijack_enable(self):
        return apps.is_installed("hijack")

    def is_webgis_enable(self):
        return apps.is_installed("django_webix_leaflet")

    def is_webix_filter_enable(self):
        return apps.is_installed("django_webix.contrib.filter")

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active

    def get_object_url(self, content_type, object_pk=None):
        if content_type is not None:
            model = content_type.model_class()
            if model is not None:
                info = (model._meta.app_label, model._meta.model_name)
                try:
                    if object_pk is None:
                        return reverse(f"{self.urls_namespace}:%s.%s.list" % info, current_app=self.name)
                    else:
                        return reverse(
                            f"{self.urls_namespace}:%s.%s.update" % info,
                            current_app=self.name,
                            kwargs={"pk": object_pk},
                        )
                except NoReverseMatch:
                    pass
        return None

    #    def check(self, app_configs): # TODO
    #        if app_configs is None:
    #            app_configs = apps.get_app_configs()
    #        app_configs = set(app_configs)  # Speed up lookups below
    #
    #        errors = []
    #        modeladmins = (o for o in self._registry.values() if o.__class__ is not ModelWebixAdmin)
    #        for modeladmin in modeladmins:
    #            if modeladmin.model._meta.app_config in app_configs:
    #                errors.extend(modeladmin.check())
    #        return errors

    def register(self, model_or_iterable, admin_class=None, prefix=None, **options):
        """
        Register the given model(s) with the given admin class.
        The model(s) should be Model classes, not instances.
        If an admin class isn't given, use ModelWebixAdmin (the default admin
        options). If keyword arguments are given -- e.g., list_display --
        apply them as options to the admin class.
        If a model is already registered, raise AlreadyRegistered.
        If a model is abstract, raise ImproperlyConfigured.
        """

        admin_class = admin_class or ModelWebixAdmin
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model is not None:
                if model._meta.abstract:
                    raise ImproperlyConfigured(
                        "The model %s is abstract, so it cannot be registered with admin." % model.__name__
                    )

                if (model, prefix) in self._registry:
                    registered_admin = str(self._registry[(model, prefix)])
                    msg = "The model %s is already registered " % model.__name__
                    if registered_admin.endswith(".ModelWebixAdmin"):
                        # Most likely registered without a ModelWebixAdmin subclass.
                        msg += "in app %r." % re.sub(r"\.ModelWebixAdmin$", "", registered_admin)
                    else:
                        msg += "with %r." % registered_admin
                    raise AlreadyRegistered(msg)

                # Ignore the registration if the model has been
                # swapped out.
                if prefix is not None:
                    if options:
                        options["prefix"] = prefix
                    else:
                        options = {"prefix": prefix}

                if self.get_label_width() is not None:
                    if options:
                        options["label_width"] = self.get_label_width()
                    else:
                        options = {"label_width": self.get_label_width()}

                if not model._meta.swapped:

                    # If we got **options then dynamically construct a subclass of
                    # admin_class with those **options.
                    if options:
                        # For reasons I don't quite understand, without a __module__
                        # the created class appears to "live" in the wrong place,
                        # which causes issues later on.
                        options["__module__"] = __name__
                        admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)

                    # Instantiate the admin class to save in the registry
                    self._registry[(model, prefix)] = admin_class(model, self)
                # else:
                #     raise Exception(model, 'errore swap')

    def unregister(self, model_or_iterable, prefix=None):
        """
        Unregister the given model(s).
        If a model isn't already registered, raise NotRegistered.
        """

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [(model_or_iterable, prefix)]

        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered("The model {} is not registered".format(model))
            del self._registry[model]

    def is_registered(self, model, prefix=None):
        """
        Check if a model class is registered with this `AdminWebixSite`.
        """
        return (model, prefix) in self._registry

    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {m: m_a for m, (m_a, _p) in self._registry.items() if m._meta.app_label == label}
        else:
            models = self._registry

        for (model, _prefix), model_admin in models.items():
            app_label = model._meta.app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                "prefix": _prefix,
                "name": capfirst(model._meta.verbose_name_plural),
                "object_name": model._meta.object_name,
                "model_name": model._meta.model_name,
                "perms": perms,
                "admin_url": None,
                "add_url": None,
            }
            if perms.get("change") or perms.get("view"):
                model_dict["view_only"] = not perms.get("change")
                try:
                    model_dict["admin_url"] = reverse(
                        f"{self.urls_namespace}:%s.%s.list" % info, current_app=self.name
                    )
                except NoReverseMatch:
                    pass
            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse(f"{self.urls_namespace}:%s.%s.add" % info, current_app=self.name)
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]["models"].append(model_dict)
            else:
                app_dict[app_label] = {
                    "name": apps.get_app_config(app_label).verbose_name,
                    "app_label": app_label,
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        if label:
            return app_dict.get(label)
        return app_dict

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app["models"].sort(key=lambda x: x["name"])

        return app_list

    def available_menu_items(self, user):
        queryset = self.model_admin_menu().objects.all()
        if user.is_superuser:
            out = queryset.values_list("pk", flat=True)
        else:
            out = []
            for el in queryset.filter(enabled=True).filter(Q(active_all=True) | Q(groups__in=user.groups.all())):
                if el.model is not None:
                    if user.has_perm(el.model.app_label + ".view_" + el.model.model):
                        out.append(el.id)
                else:
                    out.append(el.id)
        return out

    def get_tree(self, items, available_items, language: str):
        out = []
        for item in items:
            if item.id in available_items:
                menu_item = {
                    "id": "menu_{}".format(item.id),
                    "value": "{}".format(item.get_label(language=language)),
                    "icon": item.icon if item.icon not in ["", None] else "fas fa-archive",
                }
                soons = (
                    self.model_admin_menu()
                    .objects.filter(parent=item, id__in=available_items)
                    .order_by("tree_id", "lft")
                )
                children = self.get_tree(soons, available_items, language=language)

                if children:
                    if self.webix_menu_type == "sidebar":
                        menu_item["data"] = children  # for sidebar
                    elif self.webix_menu_type == "menu":
                        menu_item["submenu"] = children  # for menu
                    enable = True
                elif item.model is not None or item.url not in ["", None]:
                    if item.get_url is None:
                        URL = ""
                    else:
                        URL = item.get_url(urls_namespace=self.urls_namespace)
                    menu_item["url"] = URL
                    menu_item["loading_type"] = "js_script"
                    enable = True
                else:
                    enable = False
                if enable is True:
                    out.append(menu_item)
        return out

    def get_menu_list(self, request):
        if self.model_admin_menu() is None or request.user.is_anonymous:
            return {}
        available = self.available_menu_items(request.user)

        return self.get_tree(
            self.model_admin_menu().objects.filter(level=0, id__in=available).order_by("tree_id", "lft"),
            available,
            language=get_language(),
        )

    def admin_view(self, view, cacheable=False):
        """
        Decorator to create an admin view attached to this ``AdminWebixSite``. This
        wraps the view and provides permission checking by calling
        ``self.has_permission``.
        By default, admin_views are marked non-cacheable using the
        ``never_cache`` decorator. If the view can be safely cached, set
        cacheable=True.
        """

        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.path == reverse(f"{self.urls_namespace}:logout", current_app=self.name):
                    index_path = reverse(f"{self.urls_namespace}:index", current_app=self.name)
                    return HttpResponseRedirect(index_path)
                # Inner import to prevent django.contrib.admin (app) from
                # importing django.contrib.auth.models.User (unrelated model).
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(
                    request.get_full_path(), reverse(f"{self.urls_namespace}:login", current_app=self.name)
                )
            return view(request, *args, **kwargs)

        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, "csrf_exempt", False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    def get_urls(self):
        from django.urls import include, path

        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.contenttypes.views imports ContentType.
        from django_webix.contrib.admin import forms, views

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = [  # prefix = f'{self.urls_namespace}:XXXX
            path("", wrap(self.index), name="index"),
            path("login/", self.login, name="login"),
            path("logout/", wrap(self.logout), name="logout"),
            path("dashboard/", wrap(self.dashboard), name="dashboard"),
            path("index/", wrap(self.index), name="index"),
            path("password_change/", wrap(self.password_change, cacheable=True), name="password_change"),
            path(
                "password_change/done/", wrap(self.password_change_done, cacheable=True), name="password_change_done"
            ),
            # ################################################ user update ############################################
            path("account/update/", views.UserUpdate.as_view(), name="account_update"),
            # ############################################ Reset password by email ####################################
            # nessuna di queste view deve essere sotto wrap perche si deve poter accedere anche non essendo loggati
            path("password_reset/", self.password_reset, name="password_reset"),
            # OLD
            # path('reset/<uidb64>/<token>/', self.password_reset_confirm, name='password_reset_confirm'),
            # path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
            #     form_class=forms.WebixSetPasswordForm,
            #     success_url=reverse_lazy(f'{self.urls_namespace}:password_reset_complete'),
            #     template_name='django_webix/admin/account/password_reset_confirm.html'
            # ), name='password_reset_confirm'),
            path(
                "reset/<uidb64>/<token>/",
                views.PasswordResetConfirmViewCustom.as_view(
                    form_class=forms.WebixSetPasswordForm,
                    success_url=reverse_lazy(f"{self.urls_namespace}:password_reset_complete"),
                    template_name="django_webix/admin/account/password_reset_confirm.html",
                ),
                name="password_reset_confirm",
            ),
            path("password_reset/done/", self.password_reset_done, name="password_reset_done"),
            path("reset/done/", self.password_reset_complete, name="password_reset_complete"),
        ]
        if apps.is_installed("two_factor"):
            urlpatterns += [
                path("two_factor/", wrap(self.two_factor_profile), name="two_factor_profile"),
            ]

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        # valid_app_labels = []

        for (model, prefix), model_admin in self._registry.items():
            if prefix is None:
                urlpatterns += [
                    path("%s/%s/" % (model._meta.app_label, model._meta.model_name), include(model_admin.urls)),
                ]
            else:
                urlpatterns += [
                    path(
                        "%s/%s/%s/" % (prefix, model._meta.app_label, model._meta.model_name),
                        include(model_admin.urls),
                    ),
                ]
            # if model._meta.app_label not in valid_app_labels:
            #    valid_app_labels.append(model._meta.app_label)

        # If there were ModelAdmins registered, we should have a list of app
        # labels for which we need to allow access to the app_index view,
        # if valid_app_labels:
        #    regex = r'^(?P<app_label>' + '|'.join(valid_app_labels) + ')/$'
        #    urlpatterns += [
        #        re_path(regex, wrap(self.app_index), name='app_list'),
        #    ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.urls_namespace, self.name

    def _get_user_model_list_url(self):
        UserModel = get_user_model()
        if UserModel is not None:
            return f"{self.urls_namespace}:" + UserModel._meta.app_label + "." + UserModel._meta.model_name + ".list"
        else:
            return None

    def each_context(self, request, permission_check=True):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.
        For sites running on a subpath, use the SCRIPT_NAME value if site_url
        hasn't been customized.
        """
        script_name = request.META["SCRIPT_NAME"]
        site_url = script_name if self.site_url == "/" and script_name else self.site_url
        return {
            "site_title": self.site_title,
            "site_header": self.site_header,
            "site_url": site_url,
            "is_webgis_enable": self.is_webgis_enable(),
            "is_hijack_enable": self.is_hijack_enable(),
            "is_webix_filter_enable": self.is_webix_filter_enable(),
            "has_permission": self.has_permission(request) if permission_check else False,  # utils for menu
            "menu_list": self.get_menu_list(request) if permission_check else False,  # utils for menu
            "available_apps": self.get_app_list(request) if permission_check else False,  # utils for menu
            "webix_container_id": self.webix_container_id,
            "webix_menu_type": self.webix_menu_type,
            "webix_menu_width": self.webix_menu_width,
            "user_list_url": self._get_user_model_list_url(),
            "urls_namespace": self.urls_namespace,
        }

    @method_decorator(never_cache)
    def dashboard(self, request, extra_context=None):
        from django.views.generic import TemplateView

        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.dashboard_template is not None:
            defaults["template_name"] = self.dashboard_template
        return TemplateView.as_view(**defaults)(request)

    def password_change(self, request, extra_context=None):
        """
        Handle the "change password" task -- both form display and validation.
        """
        #        if apps.is_installed("gdpr"):
        #            from gdpr.forms import GDPRPasswordChangeForm as AdminPasswordChangeForm
        #        else:
        #            from django.contrib.admin.forms import AdminPasswordChangeForm
        from django_webix.contrib.admin.views import PasswordChangeViewCustom

        url = reverse(f"{self.urls_namespace}:password_change_done", current_app=self.name)
        defaults = {
            #            'form_class': AdminPasswordChangeForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": self.password_change_template or "django_webix/admin/account/password_change.js",
        }

        request.current_app = self.name
        return PasswordChangeViewCustom.as_view(**defaults)(request)

    def password_change_done(self, request, extra_context=None):
        """
        Display the "success" page after a password change.
        """
        from django.contrib.auth.views import PasswordChangeDoneView

        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": self.password_change_template or "django_webix/admin/account/password_change_done.js",
        }
        request.current_app = self.name
        return PasswordChangeDoneView.as_view(**defaults)(request)

    def password_reset(self, request, extra_context=None):
        """
        Handle the "reset password" task -- both form display and validation.
        """

        from django.contrib.auth.views import PasswordResetView
        from django.contrib.sites.shortcuts import get_current_site
        from django_webix.contrib.admin import forms

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        if extra_context is None:
            extra_context = {}
        extra_context["domain"] = domain
        extra_context["site_name"] = site_name
        extra_context["urls_namespace"] = self.urls_namespace

        template = "django_webix/admin/account/password_reset_form.js"
        if not self.has_permission(request):
            template = "django_webix/admin/account/password_reset_form.html"

        defaults = {
            "template_name": template,
            "email_template_name": "django_webix/admin/account/password_reset_email.html",
            "form_class": forms.WebixPasswordResetForm,
            "success_url": reverse_lazy(f"{self.urls_namespace}:password_reset_done"),
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }

        request.current_app = self.name
        PasswordResetView.extra_email_context = {**self.each_context(request), **(extra_context or {})}
        return PasswordResetView.as_view(**defaults)(request)

    def password_reset_done(self, request, extra_context=None):
        """
        Handle the "reset password" task -- both form display and validation.
        """

        from django.contrib.auth.views import PasswordResetDoneView

        template = "django_webix/admin/account/password_reset_done.js"
        if not self.has_permission(request):
            template = "django_webix/admin/account/password_reset_done.html"

        defaults = {
            "template_name": template,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }

        request.current_app = self.name
        return PasswordResetDoneView.as_view(**defaults)(request)

    # NON so perche non funziona se lo metto nella function
    # def password_reset_confirm(self, request, extra_context=None):
    #
    #     from django.contrib.auth.views import PasswordResetConfirmView
    #     from django_webix.contrib.admin import forms
    #
    #     defaults = {
    #         'template_name': 'django_webix/admin/account/password_reset_confirm.js',
    #         'form_class': forms.WebixSetPasswordForm,
    #         'success_url': reverse_lazy(f'{self.urls_namespace}:password_reset_complete'),
    #         # 'extra_context': {**self.each_context(request)},
    #     }
    #     # raise Exception(extra_context, defaults)
    #     # request.current_app = self.name
    #     return PasswordResetConfirmView.as_view(
    #         form_class=forms.WebixSetPasswordForm,
    #         success_url=reverse_lazy(f'{self.urls_namespace}:password_reset_complete'),
    #         template_name='django_webix/admin/account/password_reset_confirm.js'
    #     )(request)

    def password_reset_complete(self, request, extra_context=None):

        from django.contrib.auth.views import PasswordResetCompleteView

        defaults = {
            "template_name": "django_webix/admin/account/password_reset_complete.html",
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }

        request.current_app = self.name
        return PasswordResetCompleteView.as_view(**defaults)(request)

    def two_factor_profile(self, request, extra_context=None):
        if apps.is_installed("two_factor"):
            from django_webix.views import WebixTemplateView

            defaults = {
                "template_name": "django_webix/admin/account/two_factor.js",
                "extra_context": {**self.each_context(request), **(extra_context or {})},
            }

            request.current_app = self.name
            return WebixTemplateView.as_view(**defaults)(request)
        else:
            return None

    @method_decorator(never_cache)
    def logout(self, request, extra_context=None):
        """
        Log out the user for the given HttpRequest.
        This should *not* assume the user is already logged in.
        """
        from django.contrib.auth.views import LogoutView

        defaults = {
            "extra_context": {
                **self.each_context(request, permission_check=False),
                # Since the user isn't logged out at this point, the value of
                # has_permission must be overridden.
                # 'has_permission': False,
                "template_name": self.logout_template or "django_webix/admin/logged_out.html",
                "site_title": self.site_title,
                **(extra_context or {}),
            },
        }
        request.current_app = self.name
        LogoutView.template_name = self.logout_template or "django_webix/admin/logged_out.html"
        return LogoutView.as_view(**defaults)(request)

    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        """
        Display the login form for the given HttpRequest.
        """
        if request.method == "GET" and request.user.is_authenticated and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse(f"{self.urls_namespace}:index", current_app=self.name)
            return HttpResponseRedirect(index_path)

        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.admin.forms eventually imports User.
        # from django.contrib.admin.forms import AdminAuthenticationForm
        from django.contrib.auth.forms import AuthenticationForm
        from django.contrib.auth.views import LoginView

        class AdminAuthenticationForm(AuthenticationForm):
            """
            A custom authentication form used in the admin app.
            """

            error_messages = {
                **AuthenticationForm.error_messages,
                "invalid_login": gettext(
                    "Please enter the correct %(username)s and password for a staff "
                    "account. Note that both fields may be case-sensitive."
                ),
            }
            required_css_class = "required"

            def confirm_login_allowed(self, user):
                super().confirm_login_allowed(user)
                # if not user.is_staff:
                #    raise forms.ValidationError(
                #        self.error_messages['invalid_login'],
                #        code='invalid_login',
                #        params={'username': self.username_field.verbose_name}
                #    )

        context = {
            **self.each_context(request),
            "title": gettext("Log in"),
            "app_path": request.get_full_path(),
            "username": request.user.get_username(),
            "site_title": self.site_title,
        }

        if REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST:
            context[REDIRECT_FIELD_NAME] = reverse(f"{self.urls_namespace}:index", current_app=self.name)
        context.update(extra_context or {})

        defaults = {
            "extra_context": context,
            "authentication_form": self.login_form or AdminAuthenticationForm,
            "template_name": self.login_template or "django_webix/admin/login.html",
        }
        request.current_app = self.name
        return LoginView.as_view(**defaults)(request)

    def extra_index_context(self, request):
        return {}

    @method_decorator(never_cache)
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """

        history_url = request.GET.get("state", None)
        try:
            resolve(history_url)
        except Exception:
            history_url = None

        active_tab = request.GET.get("tab", None)
        if active_tab not in ["webgis_leaflet", self.webix_container_id]:
            active_tab = self.webix_container_id

        context = {
            **self.each_context(request),
            **self.extra_index_context(request),
            "history_url": history_url,
            "title": self.index_title,
            "app_list": self.get_app_list(request),
            "active_tab": active_tab,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or "django_webix/admin/index.html", context)


class DefaultAdminWebixSite(LazyObject):
    def _setup(self):
        AdminWebixSiteClass = import_string(apps.get_app_config("dwadmin").default_site)
        self._wrapped = AdminWebixSiteClass()

    def __repr__(self):
        return repr(self._wrapped)


# This global object represents the default admin site, for the common case.
# You can provide your own AdminWebixSite using the (Simple)AdminConfig.default_site
# attribute. You can also instantiate AdminWebixSite in your own code to create a
# custom admin site.
site = DefaultAdminWebixSite()

# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django_user_agents.utils import get_user_agent
from django_webix.middleware import get_limit_version


class UserAgentLimit(TemplateView):
    template_name = "django_webix/user_agent_limit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_agent = get_user_agent(self.request)
        family = user_agent.browser.family.lower()
        major_version = user_agent.browser.version[0]
        context['user_agent'] = user_agent
        context['family'] = family
        context['major_version'] = major_version
        context['major_version_minimum'] = get_limit_version(family)
        return context

# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.urls import reverse
from django_user_agents.utils import get_user_agent
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


def get_limit_version(family):
    # Chrom * >= 60(25 / 7 / 2017)
    # IE >= 11.0(26 / 06 / 2013)NO
    # Samsung Internet >= 8(1 / 12 / 2018)
    # Safari >= 11(1 / 1 / 2015)
    # Edge >= 40(1 / 4 / 2017)
    # Firefox >= 60(9 / 5 / 2018)
    # Opera >= 47(9 / 8 / 2017)
    if 'chrom' in family:
        return 60
    elif 'ie' in family:
        return 12  # escludo ogni 11
    elif 'samsung internet' in family:
        return 8
    elif 'safari' in family:
        return 11
    elif 'edge' in family:
        return 40
    elif 'firefox' in family:
        return 60
    elif 'opera' in family:
        return 47


class UserAgentLimitMiddleware(MiddlewareMixin):
    # user_agent.browser  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
    # user_agent.browser.family  # returns 'Mobile Safari'
    # user_agent.browser.version  # returns (5, 1)
    # user_agent.browser.version_string   # returns '5.1'
    def process_request(self, request):

        user_agent = get_user_agent(request)
        if user_agent is not None and \
            user_agent.browser is not None and \
            user_agent.browser.family is not None and \
            user_agent.browser.version is not None and \
            len(user_agent.browser.version) > 0:
            family = user_agent.browser.family.lower()
            major_version = user_agent.browser.version[0]
            url_redirect = getattr(settings, 'WEBIX_USER_AGENT_LIMIT_REDIRECT', 'webix_user_agent_limit')

            limit_version = get_limit_version(family)
            if limit_version is not None and major_version < limit_version:
                if reverse(url_redirect) != request.path:
                    return HttpResponseRedirect(reverse(url_redirect))

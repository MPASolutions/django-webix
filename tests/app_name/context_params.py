from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django_dal.params import ContextParam, ContextParams


class TestContextParams(ContextParams):
    params = [
        ContextParam('user', get_user_model(), 'Django User object'),
        ContextParam('group', Group, 'Django Group object'),
    ]

    def get_from_request(self, request):
        data = {
            'user': None,
            'group': None,
        }
        if request.user.is_authenticated:
            data.update({
                'user': request.user,
                'group': request.user.groups.all().first(),
            })
        return data

    def get_from_request_post(self, request):
        data = {
            'user': None,
            'group': None,
        }
        if request.user.is_authenticated:
            data.update({
                'user': request.user,
                'group': request.user.groups.all().first(),
            })
        return data

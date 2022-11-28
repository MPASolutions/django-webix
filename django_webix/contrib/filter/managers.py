from django.db.models import Q

from django_dal.managers import DALManager, DALQuerySet
from django_dal.params import cxpr


class WebixFilterQueryset(DALQuerySet):
    def delete(self):
        self.query.distinct = False
        return super().delete()


class WebixFilterManager(DALManager.from_queryset(WebixFilterQueryset)):
    def get_filter(self):
        """
        Public: all
        Private: all only if there is no owner
                 users in the same groups as the owner if shared_edit_group
        Restricted: owner
                    all only if there is no owner
                    users in selected groups
                    users in the same groups as the owner if
        """
        if cxpr.user is None:
            return Q(
                Q(visibility='public') |
                (Q(visibility='private') & Q(insert_user__isnull=True)) |
                (Q(visibility='restricted') & Q(insert_user__isnull=True))
            )
        return Q(
            Q(visibility='public') |
            (Q(visibility='private') & (
                Q(insert_user=cxpr.user) |
                Q(insert_user__isnull=True) |
                (Q(shared_edit_group=True) & Q(insert_user__groups__in=cxpr.user.groups.all()))
            )) |
            (Q(visibility='restricted') & (
                Q(insert_user=cxpr.user) |
                Q(insert_user__isnull=True) |
                Q(assignees_groups__in=cxpr.user.groups.all()) |
                (Q(shared_edit_group=True) & Q(insert_user__groups__in=cxpr.user.groups.all()))
            ))
        )

    def get_queryset(self, ignore_filters=False):
        return super().get_queryset(ignore_filters).distinct()

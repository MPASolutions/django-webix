from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django_dal.models import DALModel, DALMPTTModel
from django_dal.mptt_managers import DALTreeManager
from mptt.models import TreeForeignKey


class WebixAdminMenuAbstract(DALMPTTModel):
    objects = DALTreeManager()

    label = models.CharField(verbose_name=_("Node name"), max_length=255, blank=True, null=True)
    icon = models.CharField(verbose_name=_("Icon"), max_length=255, blank=True, null=True)
    url = models.CharField(verbose_name=_("Web link"), max_length=1023, blank=True, null=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True, blank=True)
    active_all = models.BooleanField(verbose_name=_("Active for all"), default=True, blank=True)
    model = models.ForeignKey(ContentType, verbose_name=_("Model"), null=True, blank=True, on_delete=models.CASCADE)
    groups = models.ManyToManyField("auth.Group", blank=True, verbose_name=_("Enabled groups"))
    prefix = models.CharField(verbose_name=_("Prefix"), max_length=1023, blank=True, null=True)
    # fields for mptt tree
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, verbose_name=_("Parent"), null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name = _("Webix Admin Menu")
        verbose_name_plural = _("Webix Admin Menu")
        abstract = True

    def __str__(self):
        return self.get_label(language=settings.LANGUAGE_CODE)

    def get_url(self, urls_namespace):
        if self.model:
            if self.prefix not in ["", None]:
                return reverse(f"{urls_namespace}:{self.model.app_label}.{self.model.model}.list.{self.prefix}")
            else:
                return reverse(f"{urls_namespace}:{self.model.app_label}.{self.model.model}.list")
        if self.url:
            return self.url
        return ""

    def get_label(self, language: str):
        if (
            label_translated := self.webixadminmenulanguage_set.filter(language=language)
            .values_list("label", flat=True)
            .first()
        ):
            return label_translated
        elif self.label:
            return self.label
        elif self.model:
            return capfirst(self.model.model_class()._meta.verbose_name_plural.strip())
        raise Exception("Label or model needed")


class WebixAdminMenu(WebixAdminMenuAbstract):
    class Meta:
        verbose_name = _("Webix Admin Menu")
        verbose_name_plural = _("Webix Admin Menu")


class WebixAdminMenuLanguage(DALModel):
    menu = models.ForeignKey("dwadmin.WebixAdminMenu", on_delete=models.CASCADE, verbose_name=_("Menu"))
    language = models.CharField(max_length=8, choices=settings.LANGUAGES, verbose_name=_("Language"))
    label = models.CharField(max_length=255, verbose_name=_("Node name"))

    class Meta:
        verbose_name = _("Webix Admin Menu Language")
        verbose_name_plural = _("Webix Admin Menu Languages")
        unique_together = (("menu", "language"),)

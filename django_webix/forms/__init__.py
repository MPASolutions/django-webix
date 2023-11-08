
from django_webix.forms.forms import WebixForm, WebixModelForm
from django_webix.forms.formsets import (WebixInlineFormSet,
                                         WebixStackedInlineFormSet,
                                         WebixTabularInlineFormSet,
                                         )
#from django_webix.forms.formsets_generic import (WebixGenericStackedInlineFormSet,
#                                                 WebixGenericTabularInlineFormSet
#                                                 )

__all__ = [
    # forms
    'WebixForm',
    'WebixModelForm',
    # formset and inlines
    'WebixInlineFormSet',
    'WebixStackedInlineFormSet',
    'WebixTabularInlineFormSet',
  #  'WebixGenericStackedInlineFormSet',
  # 'WebixGenericTabularInlineFormSet'
]

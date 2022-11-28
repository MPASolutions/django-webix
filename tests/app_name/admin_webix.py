from django_webix.contrib import admin
from django_webix.forms import WebixModelForm
from tests.app_name.models import MyModel


class MyModelForm(WebixModelForm):
    class Meta:
        localized_fields = ('__all__')
        model = MyModel
        fields = [  'field',
                    'email',
                    'floatfield',
                    'decimalfield',
                    'integerfield',
                    'integerfield_null',
                    'integerfield_default',
                    'readonly',
                    'boolean',
                    'datefield',
                    'datefield_empty',
                    'datefield_2',
                    'datetimefield',
                    'datetimefield_empty',
                    'datetimefield_2',
                    'booleanfield',
                    'datetimefield_null',
                    'filepathfield_default']


@admin.register(MyModel)
class MyModelAdmin(admin.ModelWebixAdmin):
    form = MyModelForm
    list_display = ['field',
                    'email',
                    'floatfield',
                    'decimalfield',
                    'integerfield',
                    'integerfield_null',
                    'integerfield_default',
                    'readonly',
                    'boolean',
                    'datefield',
                    'datefield_empty',
                    'datefield_2',
                    'datetimefield',
                    'datetimefield_empty',
                    'datetimefield_2',
                    'booleanfield',
                    'datetimefield_null',
                    'filepathfield_default']

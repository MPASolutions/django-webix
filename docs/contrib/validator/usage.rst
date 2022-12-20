Django Validator
=============

Install dependencies
--------------------

.. code-block::

    $ python -m pip install django-webix[validator]


Usage
-----

Models file ``app/models.py``

.. code-block:: python

    from django.db import models

    class RankingMessages(models.Model):
        subject = models.CharField(max_length=3)
        description = models.CharField(max_length=10, blank=True, null=True)
        score = models.IntegerField()
        message_type = models.ForeignKey('MessageType')


Import file ``app/import.py``

.. code-block:: python

    from django import forms
    from django_validator.utils import ImportValidator
    from app.models import RankingMessages


    # Create with Form
    class TestForm(forms.Form):
        subject = forms.CharField(max_length=3)
        description = forms.CharField(max_length=10, required=False)
        score = forms.IntegerField()
        message_type = forms.ModelChoiceField(queryset=MessageType.objects.all())
        # other fields
        sender = forms.EmailField(required=False)
        cc_myself = forms.BooleanField(label='CC')

        def clean_score(self):
            value = self.cleaned_data['score']
            if value > 10:
                raise forms.ValidationError("The value should be <= 10")
            return value

        def save(self):
            model=RankingMessages()
            model.subject = self.cleaned_data['subject']
            model.description = self.cleaned_data['description']
            model.score = self.cleaned_data['score']
            model.message_type = self.cleaned_data['message_type']
            model.save()


    validator = ImportValidator('file.xlsx', TestForm, sheet_name=1)
    validator.set_filters(sender='example@email.com')
    validator.set_constant_fields(cc_myself=True)
    validator.validate(save='FULL')


    # Create with ModelForm
    class TestModelForm(forms.ModelForm):
        # other fields
        sender = forms.EmailField(required=False, label='mittente')
        cc_myself = forms.BooleanField(label='CC')

        class Meta:
            model = RankingMessages
            fields = '__all__'

        def clean_score(self):
            value = self.cleaned_data['score']
            if value > 10:
                raise forms.ValidationError("The value should be <= 10")
            return value


    validator = ImportValidator('file.xlsx', TestModelForm, sheet_name=1)
    validator.set_filters(sender='example@email.com')
    validator.set_constant_fields(cc_myself=True)
    validator.validate(save='FULL')

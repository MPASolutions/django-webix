List/Admin Actions
==================

Actions allow users to perform bulk operations on selected rows in a ``WebixListView``. Actions are
Python functions decorated with ``@action_config`` that receive the view instance, the request, and
the filtered queryset of selected objects.

.. code-block:: python

    from django_webix.views.generic.decorators import action_config


``@action_config`` Parameters
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``action_key``
     - (required)
     - A unique string identifier for the action. Used in URL params and JS templates.
   * - ``response_type``
     - (required)
     - Type of HTTP response: ``'json'``, ``'script'``, or ``'blank'`` (see below).
   * - ``short_description``
     - ``None``
     - Display label shown in the actions dropdown/buttons.
   * - ``allowed_permissions``
     - ``[]``
     - List of permission keys (e.g., ``['delete']``). The view checks
       ``has_<key>_permission()`` before execution.
   * - ``reload_list``
     - ``True``
     - Whether to reload the list after the action completes.
   * - ``maximum_count``
     - ``None``
     - Maximum number of selected items. If exceeded, returns a 400 error.
   * - ``modal_title``
     - ``"Are you sure..."``
     - Title of the confirmation modal dialog.
   * - ``modal_header``
     - ``"Fill in the form"``
     - Header text inside the modal.
   * - ``modal_click``
     - ``"Go"``
     - Text for the form confirmation button.
   * - ``modal_ok``
     - ``"Proceed"``
     - Text for the confirmation button (non-form actions).
   * - ``modal_cancel``
     - ``"Undo"``
     - Text for the cancel button.
   * - ``form``
     - ``None``
     - A ``WebixForm`` class to display before executing the action. The form receives
       ``request`` and ``queryset`` as kwargs. If the form is valid, the action function
       receives it as the 4th argument.
   * - ``icon``
     - ``None``
     - Font Awesome icon class (e.g., ``'fas fa-download'``).
   * - ``group``
     - ``None``
     - An ``ActionGroup`` for organizing actions into submenus.
   * - ``template_view``
     - ``None``
     - A ``WebixTemplateView`` subclass rendered before execution (e.g., to show
       related objects). Must be a subclass of ``WebixTemplateView``.
   * - ``dynamic``
     - ``False``
     - Whether to dynamically load the action form via AJAX.
   * - ``form_view``
     - ``DynamicTemplateFormView``
     - A ``WebixFormView`` subclass for dynamic form rendering.
   * - ``form_view_template``
     - ``None``
     - Custom template for the dynamic form view.


Action Response Types
---------------------

**``json``** - Return a ``JsonResponse`` with status, message, and optional redirect:

.. code-block:: python

    return JsonResponse({
        'status': True,                    # bool: success or failure
        'message': 'Operation completed',  # displayed to user
        'redirect_url': self.get_url_list(),  # optional: redirect after action
    }, safe=False)

Additional ``json`` response keys:

- ``message_on_popup`` (bool) - Show message in a popup window
- ``message_type`` (str) - Message type: ``'info'``, ``'error'``, etc.

**``script``** - Return an ``HttpResponseRedirect`` to load another view's JavaScript:

.. code-block:: python

    return HttpResponseRedirect(reverse('myapp.report'))

**``blank``** - Return any ``HttpResponse`` (file download, custom content, etc.):

.. code-block:: python

    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response


Action Examples
---------------

Simple Bulk Update
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.http import JsonResponse
    from django_webix.views.generic.decorators import action_config

    @action_config(
        action_key='mark_active',
        response_type='json',
        short_description='Mark as active',
        allowed_permissions=['change'],
        reload_list=True,
    )
    def mark_active_action(self, request, qs):
        count = qs.update(is_active=True)
        return JsonResponse({
            'status': True,
            'message': f'{count} items marked as active.',
            'redirect_url': self.get_url_list(),
        }, safe=False)

Action with Form
~~~~~~~~~~~~~~~~

Use the ``form`` parameter to collect user input before executing the action:

.. code-block:: python

    from django import forms
    from django.http import JsonResponse
    from django_webix.forms import WebixForm
    from django_webix.views.generic.decorators import action_config

    class DateRangeForm(WebixForm):
        date_from = forms.DateField()
        date_to = forms.DateField()

        class Meta:
            localized_fields = '__all__'

        def __init__(self, *args, **kwargs):
            kwargs.pop('queryset', None)
            super().__init__(*args, **kwargs)

    @action_config(
        action_key='filter_by_date',
        response_type='json',
        short_description='Filter by date range',
        form=DateRangeForm,
        modal_title='Select date range',
        modal_ok='Apply',
        modal_cancel='Cancel',
    )
    def filter_by_date_action(self, request, qs, form):
        data = form.cleaned_data
        filtered = qs.filter(
            date__gte=data['date_from'],
            date__lte=data['date_to'],
        )
        count = filtered.count()
        return JsonResponse({
            'status': True,
            'message': f'{count} items found in range.',
        }, safe=False)

Action Returning Redirect
~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``response_type='script'`` to navigate to another view:

.. code-block:: python

    from django.http import HttpResponseRedirect
    from django.urls import reverse
    from django_webix.views.generic.decorators import action_config

    @action_config(
        action_key='generate_report',
        response_type='script',
        short_description='Generate Report',
        allowed_permissions=['view'],
        reload_list=False,
    )
    def generate_report_action(self, request, qs):
        ids = ','.join(str(pk) for pk in qs.values_list('pk', flat=True))
        return HttpResponseRedirect(
            reverse('myapp.report') + f'?ids={ids}'
        )

File Download Action
~~~~~~~~~~~~~~~~~~~~

Use ``response_type='blank'`` for custom responses like file downloads:

.. code-block:: python

    import io
    import zipfile
    from django.http import HttpResponse
    from django_webix.views.generic.decorators import action_config

    @action_config(
        action_key='download_zip',
        response_type='blank',
        short_description='Download as ZIP',
        allowed_permissions=['view'],
        reload_list=False,
        icon='fas fa-download',
    )
    def download_zip_action(self, request, qs):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            for obj in qs:
                if obj.attachment and obj.attachment.storage.exists(obj.attachment.name):
                    zf.writestr(obj.attachment.name, obj.attachment.read())
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="export.zip"'
        return response

Action with Maximum Count
~~~~~~~~~~~~~~~~~~~~~~~~~

Limit the number of selected items:

.. code-block:: python

    @action_config(
        action_key='send_email',
        response_type='json',
        short_description='Send email notification',
        allowed_permissions=['change'],
        maximum_count=50,
        modal_title='Send email to selected items?',
    )
    def send_email_action(self, request, qs):
        for obj in qs:
            send_notification_email(obj)
        return JsonResponse({
            'status': True,
            'message': f'Email sent to {qs.count()} items.',
        }, safe=False)

Action with Template View
~~~~~~~~~~~~~~~~~~~~~~~~~

Show a confirmation view (e.g., related objects) before execution:

.. code-block:: python

    from django_webix.views.generic.base import WebixTemplateView

    class ConfirmDeleteView(WebixTemplateView):
        template_name = 'myapp/confirm_bulk_delete.js'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['queryset'] = kwargs.get('queryset')
            context['count'] = kwargs['queryset'].count()
            return context

    @action_config(
        action_key='bulk_delete',
        response_type='json',
        short_description='Delete selected',
        allowed_permissions=['delete'],
        template_view=ConfirmDeleteView,
    )
    def bulk_delete_action(self, request, qs):
        count = qs.count()
        qs.delete()
        return JsonResponse({
            'status': True,
            'message': f'{count} items deleted.',
            'redirect_url': self.get_url_list(),
        }, safe=False)


Registering Actions
-------------------

Add actions to a ``WebixListView`` via the ``actions`` attribute:

.. code-block:: python

    from django_webix.views import WebixListView
    from django_webix.views.generic.actions import multiple_delete_action
    from myapp.actions import mark_active_action, generate_report_action

    class ProductListView(WebixListView):
        model = Product
        actions = [multiple_delete_action, mark_active_action, generate_report_action]


Built-in Actions
----------------

``multiple_delete_action``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Bulk delete selected objects. Shows related objects before confirmation.

.. code-block:: python

    from django_webix.views.generic.actions import multiple_delete_action

    class ProductListView(WebixListView):
        model = Product
        actions = [multiple_delete_action]

- ``action_key``: ``'delete'``
- ``allowed_permissions``: ``['delete']``
- ``response_type``: ``'json'``
- Uses ``DeleteRelatedObjectsView`` as ``template_view`` to show cascading deletes

``multiple_download_attachments``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download all file/image field attachments from selected objects as a ZIP file.

.. code-block:: python

    from django_webix.views.generic.actions import multiple_download_attachments

    class DocumentListView(WebixListView):
        model = Document
        actions = [multiple_download_attachments]

- ``action_key``: ``'download_attachments'``
- ``allowed_permissions``: ``['view']``
- ``response_type``: ``'blank'``
- Automatically detects all ``FileField`` and ``ImageField`` on the model


Action Groups
-------------

Organize actions into submenus using ``ActionGroup``:

.. code-block:: python

    from django_webix.views.generic.actions_groups import ActionGroup

    export_group = ActionGroup(name='Export', icon='fas fa-file-export', order=10)

    @action_config(
        action_key='export_csv',
        response_type='blank',
        short_description='Export CSV',
        group=export_group,
        icon='fas fa-file-csv',
    )
    def export_csv_action(self, request, qs):
        # ... export logic ...
        pass

    @action_config(
        action_key='export_pdf',
        response_type='blank',
        short_description='Export PDF',
        group=export_group,
        icon='fas fa-file-pdf',
    )
    def export_pdf_action(self, request, qs):
        # ... export logic ...
        pass

Actions in the same group are displayed as a submenu in the actions dropdown.


JavaScript Custom Actions
-------------------------

For actions that require a custom JavaScript UI (beyond the built-in modal), override the
``toolbar_list_actions`` block in the list template:

.. code-block:: javascript

    {% block toolbar_list_actions %}
        {% if is_enable_actions %}

            var {{ view_prefix }}actions_list = [
                {% for action_key,action in actions.items %}
                    {id: '{{ action_key }}', value: '{{ action.short_description }}'}
                    {% if not forloop.last %}, {% endif %}
                {% endfor %}
            ];

            function {{ view_prefix }}actions_execute(action, ids, all) {
                {% for action_key, action in actions.items %}
                    if (action == '{{ action_key }}') {
                        _{{ view_prefix }}action_execute(
                            '{{ action_key }}', ids, all,
                            '{{ action.response_type }}',
                            '{{ action.short_description }}',
                            '{{ action.modal_title }}',
                            '{{ action.modal_ok }}',
                            '{{ action.modal_cancel }}'
                        )
                    }
                    {% if not forloop.last %} else {% endif %}
                {% endfor %}
            }
        {% else %}
            var {{ view_prefix }}actions_list = undefined;
            var {{ view_prefix }}actions_execute = undefined;
        {% endif %}
    {% endblock %}

The ``_{{ view_prefix }}action_execute`` function handles the standard confirm/submit flow.
For custom UIs, replace the ``if`` block for your action with a call to your custom JS function.

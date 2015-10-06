__author__ = 'daniel'

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset


class MetroAdminFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class='form-horizontal'
        self.form_method='post'
        self.label_class='col-lg-4'
        self.field_class='col-lg-8'
        self.primary_submit_button = Submit('submit', 'Zapisz', css_class='btn btn-primary')  # can modify in subclass
        self.add_input(self.primary_submit_button)
        self.add_input(Reset('reset', 'Czyść', css_class='btn btn-default'))

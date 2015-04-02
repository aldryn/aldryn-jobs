from aldryn_client import forms


class Form(forms.BaseForm):

    default_send_to = forms.CharField(
        "Default send to",
        help_text="E-mail in this field will be default e-mail to send "
                  "staff notifications."
    )

    def to_settings(self, data, settings):
        settings['ALDRYN_JOBS_DEFAULT_SEND_TO'] = data['default_send_to']
        return settings

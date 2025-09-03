from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Participant, Phone, Email


class ParticipantForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text="Leave empty to keep current password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Confirm Password"
    )

    class Meta:
        model = Participant
        fields = ['username', 'password', 'nickname', 'first_name', 'last_name', 'avatar', 'status', 'date_inactive',
                  'role', 'assigned_by']
        widgets = {
            'date_inactive': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_by choices to admins and moderators
        self.fields['assigned_by'].queryset = Participant.objects.filter(role__in=['admin', 'moderator'])

        # Make password not required for existing participants and clear the value
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
            # Clear the password field values for existing instances
            self.fields['password'].initial = ''
            self.fields['confirm_password'].initial = ''
        else:
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # If creating new participant or changing password
        if not self.instance.pk or password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        participant = super().save(commit=False)
        password = self.cleaned_data.get('password')

        # Only set password if it was provided
        if password:
            participant.set_password(password)

        if commit:
            participant.save()
            self.save_m2m()

        return participant


PhoneFormSet = inlineformset_factory(
    Participant, Phone, fields=('number',), extra=1, can_delete=True
)

EmailFormSet = inlineformset_factory(
    Participant, Email, fields=('email',), extra=1, can_delete=True
)

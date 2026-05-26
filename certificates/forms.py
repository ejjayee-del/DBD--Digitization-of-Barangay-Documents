from django import forms
from django.utils import timezone
from .models import CertificateDocument, CertificateTemplate, GeneratedCertificate


class CertificateGenerationForm(forms.ModelForm):
    """Dynamic form for generating certificates based on template"""
    
    class Meta:
        model = GeneratedCertificate
        fields = ['recipient_name', 'recipient_email', 'recipient_contact', 'include_signature', 'signature_official']
        widgets = {
            'recipient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'recipient_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (Optional)'}),
            'recipient_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number (Optional)'}),
            'include_signature': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_official': forms.Select(attrs={'class': 'form-control'}),
        }


class DynamicCertificateForm(forms.Form):
    """Dynamically generated form based on certificate template fields"""
    
    def __init__(self, template, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = template
        
        # Add fields based on template configuration
        all_fields = template.get_all_fields()
        
        for field_name, field_config in all_fields.items():
            field_type = field_config.get('type', 'text')
            field_label = field_config.get('label', field_name)
            is_required = field_config.get('required', False)
            help_text = field_config.get('help_text', '')
            placeholder = field_config.get('placeholder', '')

            # Normalize field name for common special-cases
            normalized_name = field_name.lower().replace(' ', '_').replace('-', '_')

            # Handle income/amount/salary fields as number-only
            if 'income' in normalized_name or 'salary' in normalized_name or 'amount' in normalized_name or 'wage' in normalized_name or 'earnings' in normalized_name:
                self.fields[field_name] = forms.DecimalField(
                    label=field_label,
                    required=is_required,
                    help_text=help_text,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label,
                        'step': '0.01',
                        'min': '0'
                    })
                )
                continue

            if normalized_name in ('civil_status', 'sex', 'gender'):
                if normalized_name == 'civil_status':
                    choices = [('', '-- Select --'), ('Single', 'Single'), ('Married', 'Married'), ('Widowed', 'Widowed'), ('Divorced', 'Divorced'), ('Separated', 'Separated')]
                else:
                    choices = [('', '-- Select --'), ('Female', 'Female'), ('Male', 'Male')]

                self.fields[field_name] = forms.ChoiceField(
                    label=field_label,
                    required=is_required,
                    choices=choices,
                    help_text=help_text,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
                continue

            if normalized_name == 'day':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=is_required,
                    initial=timezone.now().strftime('%d'),
                    help_text=help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label,
                        'readonly': 'readonly'
                    })
                )
                continue

            if normalized_name == 'month':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=is_required,
                    initial=timezone.now().strftime('%B'),
                    help_text=help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label,
                        'readonly': 'readonly'
                    })
                )
                continue

            if normalized_name == 'year':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=is_required,
                    initial=timezone.now().strftime('%Y'),
                    help_text=help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label,
                        'readonly': 'readonly'
                    })
                )
                continue

            if field_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=is_required,
                    help_text=help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label
                    })
                )
            elif field_type == 'textarea':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=is_required,
                    help_text=help_text,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 4,
                        'placeholder': placeholder or field_label
                    })
                )
            elif field_type == 'date':
                field_kwargs = {
                    'label': field_label,
                    'required': is_required,
                    'help_text': help_text,
                    'widget': forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    })
                }
                if normalized_name == 'date':
                    field_kwargs['initial'] = timezone.now().date()
                    field_kwargs['widget'].attrs['readonly'] = 'readonly'

                self.fields[field_name] = forms.DateField(**field_kwargs)
            elif field_type == 'email':
                self.fields[field_name] = forms.EmailField(
                    label=field_label,
                    required=is_required,
                    help_text=help_text,
                    widget=forms.EmailInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label
                    })
                )
            elif field_type == 'phone':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=is_required,
                    help_text=help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'type': 'tel',
                        'placeholder': placeholder or field_label
                    })
                )
            elif field_type == 'number':
                self.fields[field_name] = forms.DecimalField(
                    label=field_label,
                    required=is_required,
                    help_text=help_text,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'placeholder': placeholder or field_label
                    })
                )
            elif field_type == 'select':
                choices_str = field_config.get('choices', '')
                choices = [('', '-- Select --')] + [(c.strip(), c.strip()) for c in choices_str.split(',') if c.strip()]
                self.fields[field_name] = forms.ChoiceField(
                    label=field_label,
                    required=is_required,
                    choices=choices,
                    help_text=help_text,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            elif field_type == 'radio':
                choices_str = field_config.get('choices', '')
                choices = [(c.strip(), c.strip()) for c in choices_str.split(',') if c.strip()]
                self.fields[field_name] = forms.ChoiceField(
                    label=field_label,
                    required=is_required,
                    choices=choices,
                    help_text=help_text,
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )
                
class CertificateDocumentForm(forms.ModelForm):
    class Meta:
        model = CertificateDocument
        fields = ['title', 'content']
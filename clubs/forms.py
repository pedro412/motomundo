from django import forms
from .models import Member, Club, Chapter

class MemberRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter chapters to only show Alterados MC chapters
        try:
            alterados_club = Club.objects.get(name="Alterados MC")
            self.fields['chapter'].queryset = Chapter.objects.filter(club=alterados_club)
        except Club.DoesNotExist:
            # If Alterados MC doesn't exist, show all chapters
            self.fields['chapter'].queryset = Chapter.objects.all()
        
        # Update the chapter field placeholder
        self.fields['chapter'].empty_label = "Selecciona tu capítulo"
        
        # Make profile picture required for Alterados MC registration
        self.fields['profile_picture'].required = True
        
        # Make date of birth required for Alterados MC registration
        self.fields['date_of_birth'].required = True

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'nickname', 'chapter', 'role', 'national_role', 'member_type', 'date_of_birth', 'profile_picture']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tu nombre',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tus apellidos',
                'required': True
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tu apodo (opcional)'
            }),
            'chapter': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'data-placeholder': 'Selecciona tu capítulo'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'national_role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'member_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            })
        }
        
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'nickname': 'Apodo',
            'chapter': 'Capítulo',
            'role': 'Cargo',
            'national_role': 'Cargo Nacional',
            'member_type': 'Tipo de Miembro',
            'date_of_birth': 'Fecha de Nacimiento',
            'profile_picture': 'Foto de Perfil'
        }
        
        help_texts = {
            'nickname': 'Apodo opcional o nombre de carretera',
            'national_role': 'Cargo nacional opcional dentro del club',
            'date_of_birth': 'Requerido - Tu fecha de nacimiento',
            'profile_picture': 'Requerido - Sube una foto de perfil clara'
        }

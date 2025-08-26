from django import forms
from .models import Member, Club, Chapter

class MemberRegistrationForm(forms.ModelForm):
    # Add custom fields for copilot functionality
    is_vested = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_is_vested'
        }),
        label='Esta enchalecado?'
    )
    
    linked_to = forms.ModelChoiceField(
        queryset=Member.objects.none(),  # Will be populated in __init__
        required=False,
        empty_label="Selecciona un piloto",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_linked_to',
            'data-placeholder': 'Selecciona un piloto'
        }),
        label='Piloto asignado'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter chapters to only show Alterados MC chapters
        try:
            alterados_club = Club.objects.get(name="Alterados MC")
            self.fields['chapter'].queryset = Chapter.objects.filter(club=alterados_club)
            
            # Populate linked_to field with all active members from Alterados MC
            self.fields['linked_to'].queryset = Member.objects.filter(
                chapter__club=alterados_club,
                is_active=True,
                member_type='pilot'  # Only show pilots as options
            ).select_related('chapter').order_by('first_name', 'last_name')
            
        except Club.DoesNotExist:
            # If Alterados MC doesn't exist, show all chapters and members
            self.fields['chapter'].queryset = Chapter.objects.all()
            self.fields['linked_to'].queryset = Member.objects.filter(
                is_active=True,
                member_type='pilot'
            ).select_related('chapter').order_by('first_name', 'last_name')
        
        # Update the chapter field placeholder
        self.fields['chapter'].empty_label = "Selecciona tu capítulo"
        
        # Make profile picture required for Alterados MC registration
        self.fields['profile_picture'].required = True
        
        # Make date of birth required for Alterados MC registration
        self.fields['date_of_birth'].required = True
        
        # If this is an edit form and instance has metadata, populate custom fields
        if self.instance and self.instance.pk and hasattr(self.instance, 'metadata'):
            self.fields['is_vested'].initial = self.instance.metadata.get('is_vested', False)
            linked_to_id = self.instance.metadata.get('linked_to')
            if linked_to_id:
                try:
                    self.fields['linked_to'].initial = Member.objects.get(id=linked_to_id)
                except Member.DoesNotExist:
                    pass

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Initialize metadata if it doesn't exist
        if not hasattr(instance, 'metadata') or instance.metadata is None:
            instance.metadata = {}
        
        # Save custom fields to metadata if member_type is copilot
        if instance.member_type == 'copilot':
            instance.metadata['is_vested'] = self.cleaned_data.get('is_vested', False)
            linked_to = self.cleaned_data.get('linked_to')
            if linked_to:
                instance.metadata['linked_to'] = linked_to.id
            else:
                instance.metadata.pop('linked_to', None)
        else:
            # Clear copilot-specific metadata if not a copilot
            instance.metadata.pop('is_vested', None)
            instance.metadata.pop('linked_to', None)
        
        if commit:
            instance.save()
        return instance

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

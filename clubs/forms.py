from django import forms
from django.db.models import Q
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
            
            # Initially show no pilots - will be populated via JavaScript based on chapter selection
            self.fields['linked_to'].queryset = Member.objects.none()
            
        except Club.DoesNotExist:
            # If Alterados MC doesn't exist, show all chapters and no pilots initially
            self.fields['chapter'].queryset = Chapter.objects.all()
            self.fields['linked_to'].queryset = Member.objects.none()
        
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
                    linked_pilot = Member.objects.get(id=linked_to_id)
                    # Temporarily expand queryset to include the linked pilot for edit forms
                    self.fields['linked_to'].queryset = Member.objects.filter(
                        Q(id=linked_to_id) | 
                        Q(
                            chapter__club__name="Alterados MC",
                            is_active=True,
                            member_type='pilot'
                        )
                    ).distinct()
                    self.fields['linked_to'].initial = linked_pilot
                except Member.DoesNotExist:
                    pass

    def clean_linked_to(self):
        """
        Custom validation for the linked_to field
        """
        linked_to = self.cleaned_data.get('linked_to')
        member_type = self.cleaned_data.get('member_type')
        chapter = self.cleaned_data.get('chapter')
        
        # If not a copilot, linked_to should be None
        if member_type != 'copilot':
            return None
        
        # If copilot but no pilot selected, that's okay (optional field)
        if not linked_to:
            return None
        
        # Validate that the selected pilot exists and is from the same chapter
        if chapter:
            try:
                # Validate the pilot exists and is from the same chapter
                pilot = Member.objects.get(
                    id=linked_to.id,
                    chapter=chapter,
                    member_type='pilot',
                    is_active=True
                )
                return pilot
            except Member.DoesNotExist:
                raise forms.ValidationError(
                    'El piloto seleccionado no existe o no pertenece al capítulo seleccionado.'
                )
        
        return linked_to

    def clean(self):
        """
        Custom form validation
        """
        cleaned_data = super().clean()
        member_type = cleaned_data.get('member_type')
        linked_to = cleaned_data.get('linked_to')
        
        # Additional validation for copilots
        if member_type == 'copilot' and linked_to:
            chapter = cleaned_data.get('chapter')
            if chapter and linked_to.chapter != chapter:
                raise forms.ValidationError(
                    'El piloto seleccionado debe pertenecer al mismo capítulo.'
                )
        
        return cleaned_data

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

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Club, Chapter, Member
from .forms import MemberRegistrationForm
from django.conf import settings
import os


def club_list(request):
    return redirect('https://mundobiker-web.vercel.app/clubs')


def member_registration(request):
    """
    Public member registration form for Alterados MC
    """
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the member instance but don't save yet
            member = form.save(commit=False)
            
            # Set additional fields from the form
            member.member_type = form.cleaned_data['member_type']
            member.national_role = form.cleaned_data.get('national_role', '')
            
            # Handle profile picture
            if form.cleaned_data.get('profile_picture'):
                member.profile_picture = form.cleaned_data['profile_picture']
            
            # Save the member
            try:
                member.save()
                messages.success(
                    request,
                    f'¡Bienvenido a Alterados MC, {member.first_name}! Tu registro ha sido exitoso.'
                )
                return redirect('member_registration_success')
            except Exception as e:
                messages.error(
                    request,
                    f'Error al guardar tu registro. Por favor, intenta de nuevo.'
                )
        else:
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = MemberRegistrationForm()
    
    return render(request, 'clubs/member_registration.html', {
        'form': form,
        'club_name': 'Alterados MC'
    })


def member_registration_success(request):
    """
    Success page after member registration
    """
    return render(request, 'clubs/member_registration_success.html', {
        'club_name': 'Alterados MC'
    })

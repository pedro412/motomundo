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
            try:
                # Save the member - the form handles all the fields
                member = form.save()
                messages.success(
                    request,
                    f'¡Bienvenido a Alterados MC, {member.first_name}! Tu registro ha sido exitoso.'
                )
                return redirect('clubs:registration_success')
            except Exception as e:
                messages.error(
                    request,
                    f'Error al guardar tu registro: {str(e)}'
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

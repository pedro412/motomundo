from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Club, Chapter, Member
from .forms import MemberRegistrationForm
from django.conf import settings
import os
import json


def club_list(request):
    return redirect('https://mundobiker-web.vercel.app/clubs')


def media_debug(request):
    """
    Debug view to check media configuration and files on Railway
    """
    media_info = {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': str(settings.MEDIA_ROOT),
        'BASE_DIR': str(settings.BASE_DIR),
        'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
        'current_working_directory': os.getcwd(),
        'media_files': [],
        'directory_contents': {}
    }
    
    # Check current working directory contents
    try:
        media_info['cwd_contents'] = os.listdir('.')
    except Exception as e:
        media_info['cwd_error'] = str(e)
    
    # Check if media directory exists and list files
    if os.path.exists(settings.MEDIA_ROOT):
        try:
            for root, dirs, files in os.walk(str(settings.MEDIA_ROOT)):
                rel_path = os.path.relpath(root, str(settings.MEDIA_ROOT))
                media_info['directory_contents'][rel_path] = {
                    'dirs': dirs,
                    'files': files
                }
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(full_path, str(settings.MEDIA_ROOT))
                    media_info['media_files'].append({
                        'path': rel_file_path,
                        'full_path': full_path,
                        'exists': os.path.exists(full_path),
                        'size': os.path.getsize(full_path) if os.path.exists(full_path) else 0
                    })
        except Exception as e:
            media_info['walk_error'] = str(e)
    else:
        # Check if the media directory exists in other common locations
        possible_paths = [
            '/app/media',
            os.path.join(settings.BASE_DIR, 'media'),
            './media',
            '../media'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                media_info[f'found_alternative_path'] = {
                    'path': path,
                    'contents': os.listdir(path) if os.path.isdir(path) else 'not_a_directory'
                }
    
    return HttpResponse(json.dumps(media_info, indent=2, default=str), content_type='application/json')


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
                return redirect('clubs:registration_success')
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

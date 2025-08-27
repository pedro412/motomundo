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
        
        # Handle dynamic pilot selection for copilots
        linked_to_id = request.POST.get('linked_to')
        if linked_to_id:
            try:
                # Expand the queryset to include the selected pilot
                selected_pilot = Member.objects.get(
                    id=linked_to_id,
                    member_type='pilot',
                    is_active=True
                )
                # Get the chapter from the form to validate
                chapter_id = request.POST.get('chapter')
                if chapter_id and str(selected_pilot.chapter.id) == str(chapter_id):
                    form.fields['linked_to'].queryset = Member.objects.filter(id=linked_to_id)
                else:
                    # Pilot doesn't belong to selected chapter
                    messages.error(request, 'El piloto seleccionado no pertenece al capítulo seleccionado.')
                    form.fields['linked_to'].queryset = Member.objects.none()
            except (Member.DoesNotExist, ValueError):
                messages.error(request, 'El piloto seleccionado no es válido.')
                form.fields['linked_to'].queryset = Member.objects.none()
        
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


def get_pilots_by_chapter(request):
    """
    AJAX endpoint to get pilots from a specific chapter
    """
    chapter_id = request.GET.get('chapter_id')
    
    if not chapter_id:
        return JsonResponse({'pilots': []})
    
    try:
        chapter = Chapter.objects.get(id=chapter_id)
        pilots = Member.objects.filter(
            chapter=chapter,
            is_active=True,
            member_type='pilot'
        ).order_by('first_name', 'last_name')
        
        pilots_data = [
            {
                'id': pilot.id,
                'name': f"{pilot.first_name} {pilot.last_name}".strip(),
                'nickname': pilot.nickname or ''
            }
            for pilot in pilots
        ]
        
        return JsonResponse({'pilots': pilots_data})
        
    except Chapter.DoesNotExist:
        return JsonResponse({'pilots': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

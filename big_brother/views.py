from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Participant, Phone, Email, HistoricalRecord
from .forms import ParticipantForm, PhoneFormSet, EmailFormSet


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            try:
                participant = Participant.objects.get(username=username)

                # Check if participant can login
                if participant.role == 'simple':
                    messages.error(request, 'Your account does not have login permissions.')
                    return render(request, 'users/login.html')

                # Check password
                if participant.check_password(password):
                    # Use Django's auth system but with our participant
                    from django.contrib.auth.models import User

                    # Get or create a Django user for this participant
                    user, created = User.objects.get_or_create(
                        username=participant.username,
                        defaults={
                            'email': participant.emails.first().email if participant.emails.exists() else '',
                            'first_name': participant.first_name,
                            'last_name': participant.last_name
                        }
                    )

                    if created:
                        # Set an unusable password for the Django user
                        user.set_unusable_password()
                        user.save()

                    # Log in the Django user
                    from django.contrib.auth import login
                    login(request, user)

                    return redirect('users:dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')
            except Participant.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')

    return render(request, 'users/login.html')


def custom_logout(request):
    logout(request)
    return redirect('users:login')


def role_check(required_roles):
    def test_func(user):
        if user.is_authenticated:
            # Check if user has a participant profile with required role
            try:
                participant = Participant.objects.get(username=user.username)
                return participant.role in required_roles
            except Participant.DoesNotExist:
                return False
        return False

    return user_passes_test(test_func, login_url='users:login')


@login_required(login_url='users:login')
def dashboard(request):
    context = {
        'total_participants': Participant.objects.count(),
        'active_participants': Participant.objects.filter(status='active').count(),
        'inactive_participants': Participant.objects.filter(status='inactive').count(),
    }
    return render(request, 'users/dashboard.html', context)


def participant_list(request):
    # Get all participants
    participants = Participant.objects.all()

    # Get all users who can assign participants (for the assigned_by filter)
    assigners = Participant.objects.filter(role__in=['admin', 'moderator']).distinct()

    # Get search parameters from request
    search_query = request.GET.get('q', '')
    assigned_by = request.GET.get('assigned_by', '')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    nickname = request.GET.get('nickname', '')
    phone = request.GET.get('phone', '')
    email = request.GET.get('email', '')
    status = request.GET.get('status', '')
    activity = request.GET.get('activity', '')
    activity_address = request.GET.get('activity_address', '')
    job = request.GET.get('job', '')
    job_address = request.GET.get('job_address', '')
    address = request.GET.get('address', '')

    # Build filter conditions
    filters = Q()

    # Quick search across multiple fields
    if search_query:
        filters &= (
                Q(username__icontains=search_query) |
                Q(nickname__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phones__number__icontains=search_query) |
                Q(emails__email__icontains=search_query) |
                Q(history__value__icontains=search_query) |
                Q(history__record_type__icontains=search_query)
        )

    # Specific field filters
    if assigned_by:
        filters &= Q(assigned_by__id=assigned_by)

    if first_name:
        filters &= Q(first_name__icontains=first_name)

    if last_name:
        filters &= Q(last_name__icontains=last_name)

    if nickname:
        filters &= Q(nickname__icontains=nickname)

    if phone:
        filters &= Q(phones__number__icontains=phone)

    if email:
        filters &= Q(emails__email__icontains=email)

    if status:
        filters &= Q(status=status)

    # Historical record filters
    if activity:
        filters &= Q(history__record_type='activity', history__value__icontains=activity)

    if activity_address:
        filters &= Q(history__record_type='activity_address', history__value__icontains=activity_address)

    if job:
        filters &= Q(history__record_type='job', history__value__icontains=job)

    if job_address:
        filters &= Q(history__record_type='job_address', history__value__icontains=job_address)

    if address:
        filters &= Q(history__record_type='address', history__value__icontains=address)

    # Apply filters
    if filters:
        participants = participants.filter(filters).distinct()
        is_filtered = True
    else:
        is_filtered = False

    # Pagination
    paginator = Paginator(participants, 25)  # Show 25 participants per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/participant_list.html', {
        'participants': page_obj,
        'assigners': assigners,
        'is_filtered': is_filtered
    })



@login_required(login_url='users:login')
@role_check(['admin', 'moderator', 'viewer'])
def participant_detail(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)

    # Define record types for the template
    record_types = [
        {'name': 'Activity', 'value': 'activity'},
        {'name': 'Activity Address', 'value': 'activity_address'},
        {'name': 'Job', 'value': 'job'},
        {'name': 'Job Address', 'value': 'job_address'},
        {'name': 'Address', 'value': 'address'},
    ]

    return render(request, 'users/participant_detail.html', {
        'participant': participant,
        'record_types': record_types
    })


def participant_edit(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)

    if request.method == 'POST':
        form = ParticipantForm(request.POST, request.FILES, instance=participant)
        phone_formset = PhoneFormSet(request.POST, instance=participant)
        email_formset = EmailFormSet(request.POST, instance=participant)

        if form.is_valid() and phone_formset.is_valid() and email_formset.is_valid():
            participant = form.save()
            phone_formset.save()
            email_formset.save()

            # Save historical records
            historical_fields = {
                'activity': request.POST.get('activity'),
                'activity_address': request.POST.get('activity_address'),
                'job': request.POST.get('job'),
                'job_address': request.POST.get('job_address'),
                'address': request.POST.get('address'),
            }

            for record_type, value in historical_fields.items():
                if value:  # Only create record if value is provided and different from current
                    # Check if this is different from the current value
                    current_record = participant.history.filter(record_type=record_type).first()
                    if not current_record or current_record.value != value:
                        HistoricalRecord.objects.create(
                            participant=participant,
                            record_type=record_type,
                            value=value
                        )

            messages.success(request, f'Participant {participant.nickname} has been updated successfully!')
            return redirect('users:participant_detail', participant_id=participant_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParticipantForm(instance=participant)
        phone_formset = PhoneFormSet(instance=participant)
        email_formset = EmailFormSet(instance=participant)

    # Get current values for historical fields
    current_activity = participant.history.filter(record_type='activity').first()
    current_activity_address = participant.history.filter(record_type='activity_address').first()
    current_job = participant.history.filter(record_type='job').first()
    current_job_address = participant.history.filter(record_type='job_address').first()
    current_address = participant.history.filter(record_type='address').first()

    context = {
        'form': form,
        'phone_formset': phone_formset,
        'email_formset': email_formset,
        'participant': participant,
        'current_activity': current_activity.value if current_activity else '',
        'current_activity_address': current_activity_address.value if current_activity_address else '',
        'current_job': current_job.value if current_job else '',
        'current_job_address': current_job_address.value if current_job_address else '',
        'current_address': current_address.value if current_address else '',
    }

    return render(request, 'users/participant_form.html', context)


@login_required(login_url='users:login')
@role_check(['admin', 'moderator'])
def participant_create(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST, request.FILES)
        phone_formset = PhoneFormSet(request.POST)
        email_formset = EmailFormSet(request.POST)

        if form.is_valid() and phone_formset.is_valid() and email_formset.is_valid():
            participant = form.save()
            phone_formset.instance = participant
            phone_formset.save()
            email_formset.instance = participant
            email_formset.save()

            # Save historical records
            historical_fields = {
                'activity': request.POST.get('activity'),
                'activity_address': request.POST.get('activity_address'),
                'job': request.POST.get('job'),
                'job_address': request.POST.get('job_address'),
                'address': request.POST.get('address'),
            }

            for record_type, value in historical_fields.items():
                if value:  # Only create record if value is provided
                    HistoricalRecord.objects.create(
                        participant=participant,
                        record_type=record_type,
                        value=value
                    )

            messages.success(request, f'Participant {participant.nickname} has been created successfully!')
            return redirect('users:participant_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParticipantForm()
        phone_formset = PhoneFormSet()
        email_formset = EmailFormSet()

    context = {
        'form': form,
        'phone_formset': phone_formset,
        'email_formset': email_formset,
        'is_create': True,
        'current_activity': '',
        'current_activity_address': '',
        'current_job': '',
        'current_job_address': '',
        'current_address': '',
    }

    return render(request, 'users/participant_form.html', context)

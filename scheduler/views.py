from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from django_apscheduler.models import DjangoJobExecution
import sys
from .models import ScheduledMessage
import pywhatkit as pwk
from datetime import datetime, timedelta
import time

# Login view


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'auth/login.html')

# Logout view


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# Registration view


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

# Password Reset View


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'auth/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'

# Schedule message view

'''
@login_required
def index(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        send_hour = int(request.POST.get('send_hour'))
        send_minute = int(request.POST.get('send_minute'))

        try:
            current_time = datetime.now()
            send_time = current_time.replace(
                hour=send_hour, minute=send_minute, second=0, microsecond=0)

            if send_time < current_time:
                # If time is in the past, schedule for next day
                send_time += timedelta(days=1)

            ScheduledMessage.objects.create(
                user=request.user,
                phone_number=phone_number,
                message=message,
                send_hour=send_hour,
                send_minute=send_minute
            )

            pwk.sendwhatmsg(phone_number, message, send_hour, send_minute)

            messages.success(request, "Message scheduled successfully!")
        except Exception as e:
            messages.error(request, f"Error scheduling message: {e}")

    return render(request, 'scheduler/index.html')
'''


@login_required
def index(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        send_hour = int(request.POST.get('send_hour'))
        send_minute = int(request.POST.get('send_minute'))

        # Validate phone number format
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number

        # Validate hour and minute
        if not (0 <= send_hour <= 23 and 0 <= send_minute <= 59):
            messages.error(
                request, "Invalid time. Hour must be 0-23 and minute must be 0-59.")
            return render(request, 'scheduler/index.html')

        try:
            current_time = datetime.now()
            send_time = current_time.replace(
                hour=send_hour, minute=send_minute, second=0, microsecond=0)

            if send_time < current_time:
                # If time is in the past, schedule for next day
                send_time += timedelta(days=1)

            # Store the scheduled message in the database
            ScheduledMessage.objects.create(
                user=request.user,
                phone_number=phone_number,
                message=message,
                send_hour=send_hour,
                send_minute=send_minute
            )

            # Don't try to send message immediately - let the scheduler handle it
            messages.success(
                request, f"Message scheduled successfully for {send_hour}:{send_minute:02d}!")

        except Exception as e:
            messages.error(request, f"Error scheduling message: {e}")

    return render(request, 'scheduler/index.html')


# View scheduled messages   
@login_required
def view_scheduled(request):
    scheduled_messages = ScheduledMessage.objects.filter(user=request.user)
    return render(request, 'scheduler/view_scheduled.html', {'scheduled_messages': scheduled_messages})

# Update scheduled message


@login_required
def update_scheduled(request, id):
    message = ScheduledMessage.objects.get(id=id, user=request.user)
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        message_text = request.POST.get('message')
        send_hour = int(request.POST.get('send_hour'))
        send_minute = int(request.POST.get('send_minute'))

        try:
            message.phone_number = phone_number
            message.message = message_text
            message.send_hour = send_hour
            message.send_minute = send_minute
            message.sent = False
            message.save()

            messages.success(request, "Message updated successfully!")
            return redirect('view_scheduled')
        except Exception as e:
            messages.error(request, f"Error updating message: {e}")

    return render(request, 'scheduler/update_scheduled.html', {'message': message})

# Delete scheduled message


@login_required
def delete_scheduled(request, id):
    message = ScheduledMessage.objects.get(id=id, user=request.user)
    message.delete()
    messages.success(request, "Message deleted successfully!")
    return redirect('view_scheduled')

# Account page


@login_required
def account(request):
    stats = {
        'total_scheduled': ScheduledMessage.total_scheduled(request.user),
        'total_sent': ScheduledMessage.total_sent(request.user),
    }
    return render(request, 'account/account.html', {'stats' : stats})

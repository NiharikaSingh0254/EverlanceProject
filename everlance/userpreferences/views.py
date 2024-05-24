from django.shortcuts import render,redirect
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
    if request.method == 'GET':

        return render(request, 'preferences/index.html', {'currencies': currency_data,
                                                          'user_preferences': user_preferences})
    else:

        currency = request.POST['currency']
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved')
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})


def account(request):
    return render(request,'preferences/account.html')

@login_required(login_url='/authentication/login')
def reset_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentpassword')
        new_password1 = request.POST.get('newpassword1')
        new_password2 = request.POST.get('newpassword2')
        
        # Check if the current password is valid
        if not request.user.check_password(current_password):
            messages.error(request, 'Invalid current password.')
        else:
            # Check if the new passwords match
            if new_password1 == new_password2:
                # Change the user's password
                request.user.set_password(new_password1)
                request.user.save()
                messages.success(request, 'Your password has been successfully changed.')
            else:
                messages.error(request, 'New passwords do not match.')

    return render(request, 'preferences/account.html')


def delete_account(request):
    
    if request.method == 'POST':
    
        request.user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('register')  

    return render(request, 'preferences/account.html')
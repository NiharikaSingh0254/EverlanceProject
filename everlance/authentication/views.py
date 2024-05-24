from django.shortcuts import render, redirect
from django.views import View
import json
import threading
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'email in use,choose another one '}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            # First, check if the user exists
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials, try again')
                return render(request, 'authentication/login.html')
            
            # Check if the account is active
            if not user.is_active:
                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')

            # Authenticate the user
            user = auth.authenticate(username=username, password=password)
            
            if user:
                auth.login(request, user)
                messages.success(request, 'Welcome, ' + user.username + ' you are now logged in')
                return redirect('expenses')

            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')



class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short. Must be atleast 6 characters')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email_content = (f'Hi {user.username},\n\n'
            "Thank you for registering with Everlance! We're excited to have you on board. "
            'To complete your registration and activate your account, please verify your email address '
            f'by clicking the link below:\n\n{activate_url}\n\n'
            'If you did not create an account with Everlance, please disregard this email. '
            '\n\n'
            'Thank you,\nThe Everlance Team\n\n'
            'Note: This is an automated message. Please do not reply to this email.'
            )


                email = EmailMessage(
                    email_subject,
                    email_content,
                    'noreply@everlance.com',
                    [email],
                )
                EmailThread(email).start()
                messages.success(request, 'Account successfully created. Kindly check your mail to activate the account')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST.get('email')  # Use .get() to avoid KeyError
        context = {'values': request.POST}
       
        if not validate_email(email):
            messages.error(request, 'Please provide a valid email')
            return render(request, 'authentication/reset-password.html', context)
       
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)

        if user.exists():
            email_contents = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }

            link = reverse('reset-user-password', kwargs={
                'uidb64': email_contents['uid'], 'token': email_contents['token']
            })

            mail_subject = 'Password Reset Link'
            reset_url = 'http://' + current_site.domain + link

            email_content = (f'Hi {user[0].username},\n\n'
            "We received a request to reset your password for your account associated with this email address. "
            'To reset your password, please click on the link below:'
            f'\n\n{reset_url}\n\n'
            'If you did not request to reset your password, please ignore this email.'
            '\n\n'
            'Thank you,\nThe Everlance Team\n\n'
            'Note: This is an automated message. Please do not reply to this email.'
            )

            email_message = EmailMessage(
                mail_subject,
                email_content,
                'noreply@everlance.com',
                [email],
            )
            EmailThread(email_message).start()
            messages.success(request, 'Kindly check your mail for the password reset link')
        else:
            messages.error(request, 'No account found with this email')

        return render(request, 'authentication/reset-password.html', context)



class CompletePasswordReset(View):

    def get(self, request,uidb64,token):
       
       context= {
           'uidb64':uidb64,
           'token':token
       }

       try:
           user_id = force_text(urlsafe_base64_decode(uidb64))
           user = User.objects.get(pk=user_id)


           if not PasswordResetTokenGenerator().check_token(user,token):
              messages.success(request,'Password link has expired.Please request a new one')
              return render(request, 'authentication/reset-password.html', context)

       except Exception as identifier:
           pass
                
       return render(request,'authentication/set-new-password.html',context)
    
    
    def post(self, request,uidb64,token):
       
       context= {
           'uidb64':uidb64,
           'token':token
       }

       password = request.POST['password']
       password2 = request.POST['password2']

       if password != password2:
           
           messages.error(request,"Passwords do not match")
           return render(request,'authentication/set-new-password.html',context)
       
       if len(password)<6:
           
           messages.error(request,"Password too short")
           return render(request,'authentication/set-new-password.html',context)
       

       try:
           user_id = force_text(urlsafe_base64_decode(uidb64))

           user = User.objects.get(pk=user_id)
           user.set_password(password)
           user.save()
            
           messages.success(request,'Password reset successful')
           return redirect('login')
       except Exception as identifier:
           messages.info(request,'Something went wrong. Try again')
           return render(request,'authentication/set-new-password.html',context)


       

       

    
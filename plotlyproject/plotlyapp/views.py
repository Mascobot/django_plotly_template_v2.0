from django.shortcuts import render
from django.contrib import auth as authD
from django.conf import settings
#from django.http import HttpResponse
from django.shortcuts import redirect
from . import forms
import os
import firebase_admin
from firebase_admin import credentials
#from firebase_admin import db #If in use with a firebase database.
from firebase_admin import auth
import pyrebase

#################################################################
#Variables to change with custom data:
apiKey = ""
authDomain = "XXXX.firebaseapp.com"
projectId = "XXXX"
storageBucket = "XXXX.appspot.com"
messagingSenderId = "00000000"
appId = ""

databaseURL = projectId + ".firebaseio.com"#In example: "databaseURL": "https://databaseName.firebaseio.com",

path = ''#Path to json file folder 
json_file_path = os.path.join(path, "XXXXX.json")#This could be a global variable/file path given in CLI

################################################################## END of varibles to change.

config = {
  "apiKey": apiKey,
  "authDomain": authDomain,
  "databaseURL":databaseURL,
  "storageBucket": storageBucket,
  "serviceAccount": json_file_path,
}

cred = credentials.Certificate(json_file_path)
firebase_admin.initialize_app(cred, {'databaseURL': databaseURL})

pyrebase = pyrebase.initialize_app(config)

#db = firebase.database()#If firebase database is used for additional fields in user registration/authentication

#If only especific email domains are authorized to register in App, list domains here (example: "@tesla.com"). If empty, all domains are authorized.
authorized_email_domains = []#If empty, all domains are authorized.

#global variables:
post_register_message = False
post_top_message = False
full_name = ''

#Render views here:
def home(request):
    return redirect(login)#redirect now to login page, this can be replaced with genral home page. Change also URLs file in app folder.
    
def welcome(request):
    global post_top_message
    if request.session.has_key('uid') and full_name != '':
        return render(request, 'plotlyapp/welcome.html', {'username':full_name})
    else:
        post_top_message = 'Please login with your account'
        return redirect(login)

#register new users:
def register(request):
    global post_register_message
    authD.logout(request)
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            first_name = register_form.cleaned_data['first_name']
            last_name = register_form.cleaned_data['last_name']
            display_name = first_name + " " + last_name
            Company = register_form.cleaned_data['Company']
            Email = register_form.cleaned_data['Email']
            pwd = register_form.cleaned_data['pwd']
            verify_pwd = register_form.cleaned_data['verify_pwd']
    
            if pwd != verify_pwd:
                return_message = "Passwords don't match. Try again."
                return render(request, 'plotlyapp/register.html', {'message':return_message}) 
            else:
                pass

            if len(authorized_email_domains) == 0:
                try:
                    new_user = auth.create_user(email=Email, email_verified=False, password=pwd, display_name=display_name, disabled=False)
                    #new_user = auth.create_user(email='user@example.com', email_verified=False, phone_number='+15555550100',password='secretPassword',display_name='John Doe',photo_url='http://www.example.com/12345678/photo.png',disabled=False)
                    uid = new_user.uid
                    print('New user account has been created. ID: {0}'.format(uid))
                    additional_claims = {
                                        'First_name':first_name,
                                        'Last_name':last_name,
                                        'Company':Company,
                                        'PremiumAccount': False
                                    }
                    auth.set_custom_user_claims(uid, additional_claims)  
                    pyrebase_auth = pyrebase.auth()
                    login_user = pyrebase_auth.sign_in_with_email_and_password(Email, pwd)
                    # before the 1 hour expiry:
                    login_user = pyrebase_auth.refresh(login_user['refreshToken'])
                    # now we have a fresh token  
                    pyrebase_auth.send_email_verification(login_user['idToken'])#We need iDToken to send email verification. I couln't get the ID token from the Firebase official python API, just from pyrebase (which the only reason it's here)
                    post_register_message = 'Account has been succcesfully created. Please verify your email address.'  
                    authD.logout(request)
                    return redirect(login)

                except Exception as e: 
                    if 'The user with the provided email already exists' in str(e):
                        return_message = 'The user with the provided email already exists in our system.'
                    else:
                        return_message = str(e)           
                    return render(request, 'plotlyapp/register.html', {'message':return_message}) 
            else:
                for domain in authorized_email_domains:
                    if domain in Email:
                        try:
                            new_user = auth.create_user(email=Email, email_verified=False, password=pwd, display_name=display_name, disabled=False)
                            #new_user = auth.create_user(email='user@example.com', email_verified=False, phone_number='+15555550100',password='secretPassword',display_name='John Doe',photo_url='http://www.example.com/12345678/photo.png',disabled=False)
                            uid = new_user.uid
                            additional_claims = {
                                        'First_name':first_name,
                                        'Last_name':last_name,
                                        'Company':Company,
                                        'PremiumAccount': False
                                    }
                            auth.set_custom_user_claims(uid, additional_claims)  
                            pyrebase_auth = pyrebase.auth()
                            login_user = pyrebase_auth.sign_in_with_email_and_password(Email, pwd)
                            # before the 1 hour expiry:
                            login_user = pyrebase_auth.refresh(login_user['refreshToken'])
                            # now we have a fresh token  
                            pyrebase_auth.send_email_verification(login_user['idToken'])#We need iDToken to send email verification. I couln't get the ID token from the Firebase official python API, just from pyrebase (which the only reason it's here)
                            post_register_message = 'Account has been succcesfully created. Please verify your email address.'  
                            authD.logout(request)
                            return redirect(login)

                        except Exception as e: 
                            if 'The user with the provided email already exists' in str(e):
                                return_message = 'An account associated with this email address already exists.'
                            else:
                                return_message = str(e)           
                            return render(request, 'plotlyapp/register.html', {'message':return_message})  
                        
                    else: pass
                return_message = 'This organization has not been approved to create an account. Please contact support.'
                return render(request, 'plotlyapp/register.html', {'message':return_message})
    
    else:
        return render(request, 'plotlyapp/register.html')

def login(request):
    global post_register_message, post_top_message, full_name
    authD.logout(request)    
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            Email = form.cleaned_data['Email']#the "Email" string needs to match to the name of the variable in the forms.py file (it gets the data from that file)
            pwd = form.cleaned_data['pwd']#the "pwd" string needs to match to the name of the variable in the forms.py file (it gets the data from that file)
            try:
                pyrebase_auth = pyrebase.auth()
                user = pyrebase_auth.sign_in_with_email_and_password(Email, pwd)
                usuario = auth.get_user_by_email(Email)
                full_name = usuario.custom_claims.get('First_name') + ' ' + usuario.custom_claims.get('Last_name')

            except:
                return_message = 'Invalid login credentials. Try again.'
                return render(request, 'plotlyapp/login.html', {'message':return_message})

            user_for_uid = auth.get_user_by_email(Email)
            account = firebase_admin.auth.get_user(user_for_uid.uid)
            if account.email_verified == True:             
                session_id = user['idToken']
                request.session['uid'] = str(session_id)#Request session key for authentication in all pages   
                if request.session.has_key('uid'):#If it has key, send to main page
                    return redirect(welcome)
                else:
                    return render(request, 'plotlyapp/login.html')                
            else:
                return_message = 'Please verify your email account address first'
                return render(request, 'plotlyapp/login.html', {'message':return_message})
        else:
            print('Not a valid form')
    else:
        form = forms.LoginForm()
    if post_register_message == False and post_top_message == False:
        return render(request, 'plotlyapp/login.html') 
    elif post_register_message != False and post_top_message== False:
        message = {'post_register_message':post_register_message}
        post_register_message = False
        return render(request, 'plotlyapp/login.html', message)   
    elif post_register_message == False and post_top_message != False:
        message = {'post_register_message':post_top_message}
        post_top_message = False
        return render(request, 'plotlyapp/login.html', message) 
    else:
        return render(request, 'plotlyapp/login.html')                

def recovery(request):
    global post_top_message
    authD.logout(request)
    if request.method == 'POST':
        recovery_form = forms.RecoveryForm(request.POST)
        if recovery_form.is_valid():
            Email = recovery_form.cleaned_data['Email']
            pyrebase_auth = pyrebase.auth()
            try:
                pyrebase_auth.send_password_reset_email(Email)
                post_top_message = 'If we find your Email in our system, you should receive shorlty an email with password reset instructions. Please check your spam folder!'
                return redirect(login)
            except Exception as e: 
                    if 'EMAIL_NOT_FOUND' in str(e):
                        print('Email was not found in Firebase')
                        post_top_message = "There is no account associated with this email address"
                        return redirect(login)
                    else:
                        return redirect(login)

        else:
            print ('Recovery form is not valid')
    else:        
        pass
    return render(request, 'plotlyapp/recovery.html')

def logout(request):
    global post_top_message
    authD.logout(request)
    post_top_message = 'You have been logged out.'
    return redirect(login)
    

    





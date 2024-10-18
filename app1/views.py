from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .models import *
# Create your views here.



def HomePage(request):
    if request.method == 'POST':
        return redirect('signup')
    return render(request,'home.html')

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirmpass = request.POST.get('password2')

        # Check if all fields are provided
        if not uname or not email or not password or not confirmpass:
            return HttpResponse("All fields are required")

        # Check if passwords match
        if password != confirmpass:
            return HttpResponse("Passwords do not match")

        # Check if username already exists
        if User.objects.filter(username=uname).exists():
            return HttpResponse("Username already taken")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already in use")

        try:
            # Create the user
            my_user = User.objects.create_user(username=uname, email=email, password=password)
            my_user.save()
            return redirect('login')
        except Exception as e:
            return HttpResponse(f"Error creating user: {e}")

    return render(request, 'signup.html')



def LoginPage(request):

    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('pass')

        # Check if username is provided
        if not uname or not password:
            print('Username and Password are required')
            return redirect('login')

        # Check if user exists
        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            print(request, 'Incorrect Username or Password')
            return redirect('login')

        # Authenticate the user
        user = authenticate(request, username=uname, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            return redirect('menu')  # Ensure 'home' matches a valid URL pattern name
        else:
            # Incorrect password
            print(request, 'Incorrect Username or Password')
            return redirect('login')

    return render(request, 'login.html')

def MenuPage(request):
    username = "Player_X"
    if request.user.is_authenticated:
        username = request.user.username  
    
    show_modal = False  # Flag to indicate if modal should be shown
    error_message = None  # Variable to hold error message

    if request.method == "POST":
        option = request.POST.get('roomOption')
        room_code = request.POST.get('roomCode')

        if option == 'join':
            game = Game.objects.filter(room_code=room_code).first()

            if game is None:
                error_message = "Room code not found"  # Set error message
                show_modal = True  # Set flag to show modal
            
            elif game.is_over:
                error_message = "Game is Over"  # Set error message for game over
                show_modal = True  # Set flag to show modal

            else:
                game.game_opponent = username
                game.save()
                return redirect('/play/' + room_code + '?username=' + username)  # Redirect if successful

        elif option == 'create':
            game = Game(game_creator=username, room_code=room_code)  # Fixed typo: 'roonm_code' to 'room_code'
            game.save()
            return redirect('/play/' + room_code + '?username=' + username)  # Redirect if successful

    return render(request, 'menu.html', {'show_modal': show_modal, 'error_message': error_message})


def HelpPage(request):
    return render(request,'help.html')

def HighscoresPage(request):
    return render(request,'highscores.html')

def PlaywithCompPage(request):
    return render(request,'gamewithpc.html')

def play(request, room_code):
    username = "Player_X"
    if request.user.is_authenticated:
        username = request.user.username

    context = {'room_code': room_code , 'username' : username}
    return render(request, 'game.html', context) 
    

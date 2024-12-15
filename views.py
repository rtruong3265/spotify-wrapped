from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Wrapped, DuoWrapped
from django.contrib.auth import login as auth_login
from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseRedirect
from .config import CLIENT_ID
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .retrieval import SpotifyAPI
import random
from datetime import datetime
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

       # Validation logic...
        if User.objects.filter(username=username).exists():
           messages.error(request, 'Username is already taken. Try again!')
           return redirect('register')
        if User.objects.filter(email=email).exists():
           messages.error(request, 'Email is already in use. Try again!')
           return redirect('register')


       # Create the User object
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

       # Log the user in
        user = authenticate(request, username=username, password=password)  # Authenticate the user
        if user is not None:
            auth_login(request, user)  # Log the user in
        profile = user.profile  # Access the Profile through the reverse relation
        profile.save()
        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('linkSpotify')

    return render(request, 'TechWrapper/register.html')

def login(request):
  if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']

      user = authenticate(request, username=username, password=password)
      if user is not None:
          auth_login(request, user)
          profiles = Profile.objects.get(user=user)
          return redirect('start')  # placeholder for now
      else:
          messages.error(request, 'Invalid username or password')

  return render(request, 'TechWrapper/login.html')

def home(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return render(request, 'TechWrapper/homePage.html')


def start(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    return render(request, 'TechWrapper/start.html', {'profile': profile})


def profile(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        invites = profile.duoInvites.all()  # Fetch invites related to the profile
        return render(request, 'TechWrapper/profile.html', {'profile': profile, 'invites': invites})
    else:
        return redirect('login')


def topArtists(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        top_artists = request.session.get('top_artists', None)
        artistOne = top_artists[0]["name"] if top_artists and len(top_artists) > 0 else "Placeholder"
        artistTwo = top_artists[1]["name"] if top_artists and len(top_artists) > 1 else "Placeholder"
        artistThree = top_artists[2]["name"] if top_artists and len(top_artists) > 2 else "Placeholder"
        return render(request, 'TechWrapper/TopArtists.html', {'profile': profile, 'artistOne': artistOne, 'artistTwo': artistTwo, 'artistThree': artistThree})
    return render(request, 'TechWrapper/TopArtists.html')


def topGenres(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        top_genres = request.session.get('top_genres', None)
        genreOne = top_genres[0] if top_genres and len(top_genres) > 0 else "Placeholder"
        genreTwo = top_genres[1] if top_genres and len(top_genres) > 1 else "Placeholder"
        genreThree = top_genres[2] if top_genres and len(top_genres) > 2 else "Placeholder"
        print(genreOne, genreTwo, genreThree)
        return render(request, 'TechWrapper/TopGenres.html', {'profile': profile, 'genreOne' : genreOne, 'genreTwo' : genreTwo, 'genreThree' : genreThree})
    return render(request, 'TechWrapper/TopGenres.html')


def topSongs(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        top_songs = request.session.get('top_songs', None)
        songOne, artistOne = (top_songs[0]["name"], top_songs[0]["artist"]) if top_songs and len(top_songs) > 0 else (
        "Placeholder", "Placeholder")
        songTwo, artistTwo = (top_songs[1]["name"], top_songs[1]["artist"]) if top_songs and len(top_songs) > 1 else (
        "Placeholder", "Placeholder")
        songThree, artistThree = (top_songs[2]["name"], top_songs[2]["artist"]) if top_songs and len(top_songs) > 2 else (
        "Placeholder", "Placeholder")
        songFour, artistFour = (top_songs[3]["name"], top_songs[3]["artist"]) if top_songs and len(top_songs) > 3 else (
        "Placeholder", "Placeholder")
        songFive, artistFive = (top_songs[4]["name"], top_songs[4]["artist"]) if top_songs and len(top_songs) > 4 else (
        "Placeholder", "Placeholder")
        return render(request, 'TechWrapper/TopSongs.html', {'profile': profile, 'artistOne' : artistOne, 'artistTwo' : artistTwo, 'artistThree' : artistThree, 'artistFour' : artistFour, 'artistFive' : artistFive, 'songOne' : songOne, 'songTwo' : songTwo, 'songThree' : songThree, 'songFour' : songFour, 'songFive' : songFive})
    return render(request, 'TechWrapper/TopSongs.html')


def totalTime(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        total_time = request.session.get('total_time', None)
        hours = total_time[0] if total_time and len(total_time) > 0 else "p"
        minutes = total_time[1] if total_time and len(total_time) > 1 else "p"
        return render(request, 'TechWrapper/TotalTime.html', {'profile': profile, 'hours': hours, 'minutes': minutes})
    return render(request, 'TechWrapper/TotalTime.html')



def deleteProf(request):
   profile = Profile.objects.get(user=request.user)
   profile.user.delete()
   return redirect('home')

def artistsTransition(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/artistsTransition.html', {'profile': profile})
    return render(request, 'TechWrapper/artistsTransition.html')

def endPage(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/endPage.html', {'profile': profile})
    return render(request, 'TechWrapper/endPage.html')

def genreTransition(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/genreTransition.html', {'profile': profile})
    return render(request, 'TechWrapper/genreTransition.html')

def songsTransition(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/songsTransition.html', {'profile': profile})
    return render(request, 'TechWrapper/songsTransition.html')

def introPage(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        spotify = SpotifyAPI()

        # Attempt to get a valid access token
        user_token = spotify.get_access_token(profile.spotifyCode)

        if not user_token or spotify.is_token_expired():
            # Token is invalid or expired, refresh the token
            new_token = spotify.refresh_access_token()
            if new_token:
                profile.spotifyToken = new_token  # Save the new token
                profile.save()
                user_token = new_token

        term = request.session.get('term', 'short')
        print(term)
        term_key = f"{term}_term"

        if user_token:
            top_songs = spotify.get_top_items("tracks", term_key, 5)
            top_artists = spotify.get_top_items("artists", term_key, 3)
            total_time = spotify.get_total_time_listened(term_key)
            top_genres = spotify.get_favorite_genres(term_key)
            lastPage = 'endPage'
            request.session['top_songs'] = top_songs
            request.session['top_artists'] = top_artists
            request.session['total_time'] = total_time
            request.session['top_genres'] = top_genres
            request.session['lastPage'] = lastPage
            print(top_songs)
            print(top_artists)
            print(top_songs)
            print(top_genres)
        print(user_token)
        return render(request, 'TechWrapper/introPage.html', {'profile': profile})
    return render(request, 'TechWrapper/introPage.html')

def timeTransition(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/timeTransition.html', {'profile': profile})
    return render(request, 'TechWrapper/timeTransition.html')

def toggleDarkMode(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        profile.darkMode = not profile.darkMode
        profile.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))

def artistsTranDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/artistsTranDuo.html', {'profile': profile})
    return render(request, 'TechWrapper/artistsTranDuo.html')

def genreTranDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/genreTranDuo.html', {'profile': profile})
    return render(request, 'TechWrapper/genreTranDuo.html')

def timeDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p1_time = request.session.get('p1_time', None)
        p2_time = request.session.get('p2_time', None)
        p2User = request.session.get('p2User', None)
        p1User = request.session.get('p1User', None)
        p1hours = p1_time[0] if p1_time and len(p1_time) > 0 else "p"
        p1minutes = p1_time[1] if p1_time and len(p1_time) > 1 else "p"
        p2hours = p2_time[0] if p2_time and len(p2_time) > 0 else "p"
        p2minutes = p2_time[1] if p2_time and len(p2_time) > 1 else "p"

        hours = p1hours + p2hours
        minutes = p1minutes + p2minutes

        # Check if minutes exceed 60
        if minutes >= 60:
            hours += minutes // 60  # Add the number of hours to 'hours'
            minutes = minutes % 60  # Set minutes to the remainder (less than 60)

        return render(request, 'TechWrapper/timeDuo.html', {'profile': profile, 'p2User' : p2User, 'p1User' : p1User, 'hours': hours, 'minutes': minutes})
    return render(request, 'TechWrapper/timeDuo.html')

def timeTranDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p1User = request.session.get('p1User', None)
        p2User = request.session.get('p2User', None)
        return render(request, 'TechWrapper/timeTranDuo.html', {'profile': profile, 'p1User' : p1User, 'p2User' : p2User})
    return render(request, 'TechWrapper/timeTranDuo.html')

def topArtistsDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p1artists = request.session.get('p1_artists', None)
        p2artists = request.session.get('p2_artists', None)
        p2User = request.session.get('p2User', None)
        p1User = request.session.get('p1User', None)
        p1artistOne = p1artists[0]["name"] if p1artists and len(p1artists) > 0 else "Placeholder"
        p1artistTwo = p1artists[1]["name"] if p1artists and len(p1artists) > 1 else "Placeholder"
        p1artistThree = p1artists[2]["name"] if p1artists and len(p1artists) > 2 else "Placeholder"
        p2artistOne = p2artists[0]["name"] if p2artists and len(p2artists) > 0 else "Placeholder"
        p2artistTwo = p2artists[1]["name"] if p2artists and len(p2artists) > 1 else "Placeholder"
        p2artistThree = p2artists[2]["name"] if p2artists and len(p2artists) > 2 else "Placeholder"
        return render(request, 'TechWrapper/topArtistsDuo.html',
                      {'profile': profile, 'p2User' : p2User, 'p1User' : p1User, 'p1artistOne': p1artistOne, 'p1artistTwo': p1artistTwo, 'p1artistThree': p1artistThree,
                       'p2artistOne': p2artistOne, 'p2artistTwo': p2artistTwo, 'p2artistThree': p2artistThree})
    return render(request, 'TechWrapper/topArtistsDuo.html')

def topGenresDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p1_genres = request.session.get('p1_genres', None)
        p2_genres = request.session.get('p2_genres', None)
        p2User = request.session.get('p2User', None)
        p1User = request.session.get('p1User', None)
        p1genreOne = p1_genres[0] if p1_genres and len(p1_genres) > 0 else "Placeholder"
        p1genreTwo = p1_genres[1] if p1_genres and len(p1_genres) > 1 else "Placeholder"
        p1genreThree = p1_genres[2] if p1_genres and len(p1_genres) > 2 else "Placeholder"
        p2genreOne = p2_genres[0] if p2_genres and len(p2_genres) > 0 else "Placeholder"
        p2genreTwo = p2_genres[1] if p2_genres and len(p2_genres) > 1 else "Placeholder"
        p2genreThree = p2_genres[2] if p2_genres and len(p2_genres) > 2 else "Placeholder"

        return render(request, 'TechWrapper/genreDuo.html',
                      {'profile': profile, 'p2User' : p2User, 'p1User' : p1User, 'p1genreOne': p1genreOne, 'p1genreTwo': p1genreTwo, 'p1genreThree': p1genreThree,
                       'p2genreOne': p2genreOne, 'p2genreTwo': p2genreTwo, 'p2genreThree': p2genreThree})
    return render(request, 'TechWrapper/genreDuo.html')

def topSongsDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p2User = request.session.get('p2User', None)
        p1User = request.session.get('p1User', None)
        p1_songs = request.session.get('p1_songs', None)
        p2_songs = request.session.get('p2_songs', None)
        p1songOne, p1artistOne = (p1_songs[0]["name"], p1_songs[0]["artist"]) if p1_songs and len(p1_songs) > 0 else (
            "Placeholder", "Placeholder")
        p1songTwo, p1artistTwo = (p1_songs[1]["name"], p1_songs[1]["artist"]) if p1_songs and len(p1_songs) > 1 else (
            "Placeholder", "Placeholder")
        p1songThree, p1artistThree = (p1_songs[2]["name"], p1_songs[2]["artist"]) if p1_songs and len(p1_songs) > 2 else (
            "Placeholder", "Placeholder")
        p1songFour, p1artistFour = (p1_songs[3]["name"], p1_songs[3]["artist"]) if p1_songs and len(p1_songs) > 3 else (
            "Placeholder", "Placeholder")
        p1songFive, p1artistFive = (p1_songs[4]["name"], p1_songs[4]["artist"]) if p1_songs and len(p1_songs) > 4 else (
            "Placeholder", "Placeholder")
        p2songOne, p2artistOne = (p2_songs[0]["name"], p2_songs[0]["artist"]) if p2_songs and len(p2_songs) > 0 else (
            "Placeholder", "Placeholder")
        p2songTwo, p2artistTwo = (p2_songs[1]["name"], p2_songs[1]["artist"]) if p2_songs and len(p2_songs) > 1 else (
            "Placeholder", "Placeholder")
        p2songThree, p2artistThree = (p2_songs[2]["name"], p2_songs[2]["artist"]) if p2_songs and len(p2_songs) > 2 else (
            "Placeholder", "Placeholder")
        p2songFour, p2artistFour = (p2_songs[3]["name"], p2_songs[3]["artist"]) if p2_songs and len(p2_songs) > 3 else (
            "Placeholder", "Placeholder")
        p2songFive, p2artistFive = (p2_songs[4]["name"], p2_songs[4]["artist"]) if p2_songs and len(p2_songs) > 4 else (
            "Placeholder", "Placeholder")


        return render(request, 'TechWrapper/topSongsDuo.html',
                      {'profile': profile, 'p2User' : p2User, 'p1User' : p1User, 'p1artistOne': p1artistOne, 'p1artistTwo': p1artistTwo, 'p1artistThree': p1artistThree,
                       'p1artistFour': p1artistFour, 'p1artistFive': p1artistFive, 'p1songOne': p1songOne, 'p1songTwo': p1songTwo,
                       'p1songThree': p1songThree, 'p1songFour': p1songFour, 'p1songFive': p1songFive, 'p2artistOne': p2artistOne,
                       'p2artistTwo': p2artistTwo, 'p2artistThree': p2artistThree, 'p2artistFour': p2artistFour, 'p2artistFive': p2artistFive,
                       'p2songOne': p2songOne, 'p2songTwo': p2songTwo, 'p2songThree': p2songThree, 'p2songFour': p2songFour, 'p2songFive': p2songFive})
    return render(request, 'TechWrapper/topSongsDuo.html')

def topSongsTranDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/topSongsTranDuo.html', {'profile': profile})
    return render(request, 'TechWrapper/topSongsTranDuo.html')

def welcomeDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        request.session['profileUser'] = profile.user.username
        invProf = request.session.get('invProf', None)
        request.session['p1User'] = profile.user.username
        request.session['p2User'] = invProf
        request.session['lastPage'] = 'endDuo'
        return render(request, 'TechWrapper/welcomeDuo.html', {'profile': profile, 'invProf': invProf})
    return render(request, 'TechWrapper/welcomeDuo.html')

def endDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/endDuo.html', {'profile': profile})
    return render(request, 'TechWrapper/endDuo.html')

def genreDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p1_genres = request.session.get('p1_genres', None)
        p2_genres = request.session.get('p2_genres', None)
        p1User = request.session.get('p1User', None)
        p2User = request.session.get('p2User', None)
        p1genreOne = p1_genres[0] if p1_genres and len(p1_genres) > 0 else "Placeholder"
        p1genreTwo = p1_genres[1] if p1_genres and len(p1_genres) > 1 else "Placeholder"
        p1genreThree = p1_genres[2] if p1_genres and len(p1_genres) > 2 else "Placeholder"
        p2genreOne = p2_genres[0] if p2_genres and len(p2_genres) > 0 else "Placeholder"
        p2genreTwo = p2_genres[1] if p2_genres and len(p2_genres) > 1 else "Placeholder"
        p2genreThree = p2_genres[2] if p2_genres and len(p2_genres) > 2 else "Placeholder"

        return render(request, 'TechWrapper/genreDuo.html',
                      {'profile': profile, 'p2User' : p2User, 'p1User' : p1User, 'p1genreOne': p1genreOne, 'p1genreTwo': p1genreTwo,
                       'p1genreThree': p1genreThree,
                       'p2genreOne': p2genreOne, 'p2genreTwo': p2genreTwo, 'p2genreThree': p2genreThree})
    return render(request, 'TechWrapper/genreDuo.html')

def spotifyLogin(request):
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/userauth",
        "scope": "user-library-read playlist-read-private user-top-read playlist-read-collaborative user-read-playback-position user-read-recently-played"
    }
    base_url = "https://accounts.spotify.com/authorize"
    url = f"{base_url}?{urlencode(params)}"
    return redirect(url)


def userauth(request):
    if not request.user.is_authenticated:
        # Redirect to the login page with a custom error message
        messages.error(request,"Login failed due to connectivity, please login and connect account manually through profile.")
        return redirect('login')
    # Extract the `code` parameter from the query string
    code = request.GET.get('code', None)

    if not code:
        return HttpResponse("Authorization failed or code not provided.", status=400)

    # Store code in the user's data (if a user is logged in and you have a Profile model)
    profile = request.user.profile
    profile.spotifyCode = code
    profile.save()
    print(f"Debug: Stored Spotify authorization code for user {request.user.username}: {profile.spotifyCode}")

    # Check if there is a `next` parameter in the URL
    next_url = request.session.get('next', None)
    print(f"Debug: Next URL is: {next_url}")

    # If 'next' is provided, redirect to that URL, otherwise redirect to the default 'start' page
    if next_url:
        return redirect(next_url)
    else:
        return redirect('start')

def contact(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/contact.html', {'profile': profile})
    return render(request, 'TechWrapper/contact.html')
def linkSpotify(request):
    return render(request, 'TechWrapper/linkSpotify.html')

def savedWraps(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        wraps = profile.spotifyWrapped.all()
        duoWraps = profile.duoWraps.all()
        return render(request, 'TechWrapper/savedWrapps.html', {'profile': profile, 'wraps': wraps, 'duoWraps': duoWraps})
    return render(request, 'TechWrapper/savedWrapps.html')
def gamePage(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    spotify_api = SpotifyAPI()
    if not spotify_api.access_token:
        return render(request, "TechWrapper/gamePage.html", {"profile": profile, "error_message": "Please log in to Spotify to play the game."})
    try:
        top_tracks = spotify_api.get_top_items("tracks", "short_term", limit=50)  # Fetch more tracks to increase chances
    except Exception as e:
        return render(request, "TechWrapper/gamePage.html", {"profile": profile, "error_message": f"Error fetching top tracks: {str(e)}"})

    # make sure the tracks have a url
    valid_tracks = [track for track in top_tracks if track.get("preview_url")]
    if not valid_tracks:
        print(profile.darkMode)
        return render(request, "TechWrapper/gamePage.html", {"profile": profile, "error_message": "No tracks with a preview are available."})

    # at least have 4 tracks
    if len(valid_tracks) < 4:
        return render(request, "TechWrapper/gamePage.html", {"profile": profile, "error_message": "Not enough tracks to play the game."})

    # pick a song that will be the answer and get url
    correct_song = random.choice(valid_tracks)
    preview_url = correct_song["preview_url"]
    correct_song_name = correct_song["name"]
    all_song_names = [track["name"] for track in valid_tracks]

    # get random choices
    wrong_answers = random.sample(
        [name for name in all_song_names if name != correct_song_name], 3
    )
    options = wrong_answers + [correct_song_name]
    random.shuffle(options)
    context = {
        "preview_url": preview_url,
        "options": options,
        "correct_answer": correct_song_name,
        "error_message": None,  # No errors
        "profile": profile,
    }
    return render(request, "TechWrapper/gamePage.html", context)
def check_answer(request):
    if request.method == "POST":
        user_guess = request.POST.get("guess")
        correct_answer = request.POST.get("correct_answer")
        is_correct = user_guess == correct_answer
        return JsonResponse({"is_correct": is_correct})
    return JsonResponse({"error": "Invalid request"}, status=400)
def search_users(request):
    query = request.GET.get('q', '')  # Get the search query from the URL
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id).values_list('username', flat=True)[:10]  # Limit to 10 results
    else:
        users = User.objects.none()
    return JsonResponse(list(users), safe=False)

def wrapSum(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        if request.method == 'POST':
            wrap_id = request.POST.get('wrap_id')
            if wrap_id:
                wrap = Wrapped.objects.get(id=wrap_id)
                top_artists = wrap.artists
                top_songs = wrap.songs
                top_genres = wrap.genres
                total_time = wrap.time
                artistOne = top_artists[0]["name"] if top_artists and len(top_artists) > 0 else "Placeholder"
                artistTwo = top_artists[1]["name"] if top_artists and len(top_artists) > 1 else "Placeholder"
                artistThree = top_artists[2]["name"] if top_artists and len(top_artists) > 2 else "Placeholder"
                songOne = (top_songs[0]["name"]) if top_songs and len(top_songs) > 0 else ("Placeholder")
                songTwo = (top_songs[1]["name"]) if top_songs and len(top_songs) > 1 else ("Placeholder")
                songThree = (top_songs[2]["name"]) if top_songs and len(top_songs) > 2 else ("Placeholder")
                songFour = (top_songs[3]["name"]) if top_songs and len(top_songs) > 3 else ("Placeholder")
                songFive = (top_songs[4]["name"]) if top_songs and len(top_songs) > 4 else ("Placeholder")
                hours = total_time[0] if total_time and len(total_time) > 0 else "p"
                minutes = total_time[1] if total_time and len(total_time) > 1 else "p"
                genreOne = top_genres[0] if top_genres and len(top_genres) > 0 else "Placeholder"
                genreTwo = top_genres[1] if top_genres and len(top_genres) > 1 else "Placeholder"
                genreThree = top_genres[2] if top_genres and len(top_genres) > 2 else "Placeholder"

        return render(request, 'TechWrapper/wrapSum.html', {'profile' : profile, 'artistOne' : artistOne, 'artistTwo' : artistTwo, 'artistThree' : artistThree,
                                                         'songOne' : songOne, 'songTwo' : songTwo, 'songThree' : songThree, 'songFour' : songFour, 'songFive' : songFive,
                                                          'hours' : hours, 'minutes' : minutes, 'genreOne' : genreOne, 'genreTwo' : genreTwo, 'genreThree' : genreThree })
    return render(request, 'TechWrapper/wrapSum.html')

def wrapSumDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        if request.method == 'POST':
            wrap_id = request.POST.get('wrap_id')
            if wrap_id:
                wrap = DuoWrapped.objects.get(id=wrap_id)
                p1_artists = wrap.p1Artists
                p2_artists = wrap.p2Artists
                p1_songs = wrap.p1Songs
                p2_songs = wrap.p2Songs
                p1_genres = wrap.p1Genres
                p2_genres = wrap.p2Genres
                p1_time = wrap.p1Time
                p2_time = wrap.p2Time
                p2User = wrap.p2User
                p1User = wrap.p1User
                p1songOne = (p1_songs[0]["name"]) if p1_songs and len(p1_songs) > 0 else ("Placeholder")
                p1songTwo = (p1_songs[1]["name"]) if p1_songs and len(p1_songs) > 1 else ("Placeholder")
                p1songThree = (p1_songs[2]["name"]) if p1_songs and len(p1_songs) > 2 else ("Placeholder")
                p1songFour = (p1_songs[3]["name"]) if p1_songs and len(p1_songs) > 3 else ("Placeholder")
                p1songFive = (p1_songs[4]["name"]) if p1_songs and len(p1_songs) > 4 else ("Placeholder")
                p2songOne = (p2_songs[0]["name"]) if p2_songs and len(p2_songs) > 0 else ("Placeholder")
                p2songTwo = (p2_songs[1]["name"]) if p2_songs and len(p2_songs) > 1 else ("Placeholder")
                p2songThree = (p2_songs[2]["name"]) if p2_songs and len(p2_songs) > 2 else ("Placeholder")
                p2songFour = (p2_songs[3]["name"]) if p2_songs and len(p2_songs) > 3 else ("Placeholder")
                p2songFive = (p2_songs[4]["name"]) if p2_songs and len(p2_songs) > 4 else ("Placeholder")
                p1artistOne = p1_artists[0]["name"] if p1_artists and len(p1_artists) > 0 else "Placeholder"
                p1artistTwo = p1_artists[1]["name"] if p1_artists and len(p1_artists) > 1 else "Placeholder"
                p1artistThree = p1_artists[2]["name"] if p1_artists and len(p1_artists) > 2 else "Placeholder"
                p2artistOne = p2_artists[0]["name"] if p2_artists and len(p2_artists) > 0 else "Placeholder"
                p2artistTwo = p2_artists[1]["name"] if p2_artists and len(p2_artists) > 1 else "Placeholder"
                p2artistThree = p2_artists[2]["name"] if p2_artists and len(p2_artists) > 2 else "Placeholder"
                p1genreOne = p1_genres[0] if p1_genres and len(p1_genres) > 0 else "Placeholder"
                p1genreTwo = p1_genres[1] if p1_genres and len(p1_genres) > 1 else "Placeholder"
                p1genreThree = p1_genres[2] if p1_genres and len(p1_genres) > 2 else "Placeholder"
                p2genreOne = p2_genres[0] if p2_genres and len(p2_genres) > 0 else "Placeholder"
                p2genreTwo = p2_genres[1] if p2_genres and len(p2_genres) > 1 else "Placeholder"
                p2genreThree = p2_genres[2] if p2_genres and len(p2_genres) > 2 else "Placeholder"
                p1hours = p1_time[0] if p1_time and len(p1_time) > 0 else "p"
                p1minutes = p1_time[1] if p1_time and len(p1_time) > 1 else "p"
                p2hours = p2_time[0] if p2_time and len(p2_time) > 0 else "p"
                p2minutes = p2_time[1] if p2_time and len(p2_time) > 1 else "p"
                hours = p1hours + p2hours
                minutes = p1minutes + p2minutes
                if minutes >= 60:
                    hours += minutes // 60  # Add the number of hours to 'hours'
                    minutes = minutes % 60
        return render(request, 'TechWrapper/wrapSumDuo.html', {'profile' : profile, 'p1User' : p1User, 'p2User' : p2User, 'hours' : hours, 'minutes' : minutes,
                                                               'p1songOne' : p1songOne, 'p1songTwo' : p1songTwo, 'p1songThree' : p1songThree, 'p1songFour' : p1songFour, 'p1songFive' : p1songFive,
                                                               'p2songOne' : p2songOne, 'p2songTwo' : p2songTwo, 'p2songThree' : p2songThree, 'p2songFour' : p2songFour, 'p2songFive' : p2songFive,
                                                               'p1artistOne' : p1artistOne, 'p1artistTwo' : p1artistTwo, 'p1artistThree' : p1artistThree, 'p2artistOne' : p2artistOne, 'p2artistTwo' : p2artistTwo, 'p2artistThree' : p2artistThree,
                                                               'p1genreOne' : p1genreOne, 'p1genreTwo' : p1genreTwo, 'p1genreThree' : p1genreThree, 'p2genreOne' : p2genreOne, 'p2genreTwo' : p2genreTwo, 'p2genreThree' : p2genreThree})
    return render(request, 'TechWrapper/wrapSumDuo.html')

def invite_friend(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            print(profile)
            username = request.POST.get('username', '')
            # Perform actions with the selected username
            invitedUser = User.objects.get(username=username)
            print(invitedUser)
            invProfile = Profile.objects.get(user=invitedUser)
            print(invProfile)
            invProfile.duoInvites.add(profile)
            invProfile.save()
            print(invProfile.duoInvites.all())
            print(f"Invited: {username}")
            return redirect('refreshAuthDuoInv')  # Or render a template
    return HttpResponse("Invalid request", status=400)

def refreshAuth(request):
    # Extract 'term' and 'next' parameters from the request
    term = request.GET.get('term', None)  # This is the term parameter, e.g., 'short', 'medium', 'long'
    next_url = request.GET.get('next', None)  # This is the next page to redirect after authorization, e.g., '/intro/'
    request.session['term'] = term
    request.session['next'] = next_url
    print(term, next_url)

    # Spotify OAuth parameters
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/userauth",
        # This should match the redirect URI you've registered with Spotify
        "scope": "user-library-read playlist-read-private user-top-read playlist-read-collaborative user-read-playback-position user-read-recently-played",
    }

    # Add 'term' and 'next' parameters to the URL if they exist
    if term:
        params["term"] = term
    if next_url:
        params["next"] = next_url

    # Construct the Spotify authorization URL
    base_url = "https://accounts.spotify.com/authorize"
    url = f"{base_url}?{urlencode(params)}"

    # Print the URL for debugging purposes
    print(url)

    # Redirect the user to the Spotify authorization URL
    return redirect(url)

def save(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        top_artists = request.session.get('top_artists')
        top_songs = request.session.get('top_songs')
        top_genres = request.session.get('top_genres')
        total_time = request.session.get('total_time')
        term = request.session.get('term')
        date = datetime.now().strftime("%m/%d/%Y")  # Example: 11/27/2024
        print(top_artists, top_songs, top_genres, total_time, term, date)
        wrapped = Wrapped(songs=top_songs, artists=top_artists, genres=top_genres, time=total_time, title=term, date=date)
        wrapped.save()
        profile.spotifyWrapped.add(wrapped)
        profile.save()
    return redirect('savedWraps')

def duoSave(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        invProf_id = request.session.get('invProf_id', None)
        invProfile = Profile.objects.get(user=invProf_id)
        invProf = request.session.get('invProf', None)
        p1_artists = request.session.get('p1_artists')
        p2_artists = request.session.get('p2_artists')
        p1_songs = request.session.get('p1_songs')
        p2_songs = request.session.get('p2_songs')
        p1_genres = request.session.get('p1_genres')
        p2_genres = request.session.get('p2_genres')
        p1_time = request.session.get('p1_time')
        p2_time = request.session.get('p2_time')
        date = datetime.now().strftime("%m/%d/%Y")
        duoWrapped = DuoWrapped(p1Songs=p1_songs, p2Songs = p2_songs, p1Artists=p1_artists, p2Artists=p2_artists, p1Genres=p1_genres, p2Genres=p2_genres, date=date, p1Time=p1_time, p2Time=p2_time, p2User=invProf, p1User=profile.user.username)
        duoWrapped.save()
        profile.duoWraps.add(duoWrapped)
        profile.save()
        invProfile.duoWraps.add(duoWrapped)
    return redirect('savedWraps')

def viewWrapped(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user.profile

    if request.method == 'POST':
        wrap_id = request.POST.get('wrap_id')

        if wrap_id:
            wrap = Wrapped.objects.get(id=wrap_id)
            top_artists = wrap.artists
            top_songs = wrap.songs
            top_genres = wrap.genres
            total_time = wrap.time
            lastPage = 'endPageTwo'
            request.session['total_time'] = total_time
            request.session['top_artists'] = top_artists
            request.session['top_songs'] = top_songs
            request.session['top_genres'] = top_genres
            request.session['lastPage'] = lastPage

    return redirect('introPageTwo')

def viewDuoWrapped(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user.profile

    if request.method == 'POST':
        wrap_id = request.POST.get('wrap_id')

        if wrap_id:
            wrap = DuoWrapped.objects.get(id=wrap_id)
            p1_artists = wrap.p1Artists
            p2_artists = wrap.p2Artists
            p1_songs = wrap.p1Songs
            p2_songs = wrap.p2Songs
            p1_genres = wrap.p1Genres
            p2_genres = wrap.p2Genres
            p1_time = wrap.p1Time
            p2_time = wrap.p2Time
            p2User = wrap.p2User
            p1User = wrap.p1User
            lastPage = 'endDuoTwo'
            request.session['p1_artists'] = p1_artists
            request.session['p2_artists'] = p2_artists
            request.session['p1_songs'] = p1_songs
            request.session['p2_songs'] = p2_songs
            request.session['p1_genres'] = p1_genres
            request.session['p2_genres'] = p2_genres
            request.session['p1_time'] = p1_time
            request.session['p2_time'] = p2_time
            request.session['p2User'] = p2User
            request.session['p1User'] = p1User
            request.session['lastPage'] = lastPage

    return redirect('welcomeDuoTwo')

def introPageTwo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/introPageTwo.html', {"profile": profile})
    return render(request, 'TechWrapper/introPageTwo.html')

def welcomeDuoTwo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        p1User = request.session.get('p1User')
        p2User = request.session.get('p2User')
        return render(request, 'TechWrapper/welcomeDuoTwo.html', {'profile': profile, 'p1User': p1User, 'p2User': p2User})
    return render(request, 'TechWrapper/welcomeDuoTwo.html')

def deleteInv(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        user_id = request.POST.get('user_id')
        invProf = Profile.objects.get(user_id=user_id)
        profile.duoInvites.remove(invProf)
        profile.save()
    return redirect('profile')

def acceptInv(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        user_id = request.session.get('userID', None)
        print(user_id)
        invProf = Profile.objects.get(user_id=user_id)
        profile.duoInvites.remove(invProf)
        profile.save()
        spotify = SpotifyAPI()
        user_token = spotify.get_access_token(invProf.spotifyCode)

        print(invProf.spotifyCode)

        request.session['invProf_id'] = user_id
        request.session['invProf'] = invProf.user.username

        if user_token:
            p2_songs = spotify.get_top_items("tracks", "medium_term", 5)
            p2_artists = spotify.get_top_items("artists", "medium_term", 3)
            p2_time = spotify.get_total_time_listened("medium_term")
            p2_genres = spotify.get_favorite_genres("medium_term")
            request.session['p2_songs'] = p2_songs
            request.session['p2_artists'] = p2_artists
            request.session['p2_time'] = p2_time
            request.session['p2_genres'] = p2_genres

        spotify = SpotifyAPI()
        user_token = spotify.get_access_token(profile.spotifyCode)
        if user_token:
            p1_songs = spotify.get_top_items("tracks", "medium_term", 5)
            p1_artists = spotify.get_top_items("artists", "medium_term", 3)
            p1_time = spotify.get_total_time_listened("medium_term")
            p1_genres = spotify.get_favorite_genres("medium_term")
            request.session['p1_songs'] = p1_songs
            request.session['p1_artists'] = p1_artists
            request.session['p1_time'] = p1_time
            request.session['p1_genres'] = p1_genres
    return redirect('welcomeDuo')

def delete_wrap(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        wrap_id = request.POST.get('wrap_id')
        wrap = profile.spotifyWrapped.get(id=wrap_id)
        profile.spotifyWrapped.remove(wrap)
        profile.save()
    return redirect('savedWraps')

def deleteWrapDuo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        wrap_id = request.POST.get('wrap_id')
        wrap = profile.duoWraps.get(id=wrap_id)
        profile.duoWraps.remove(wrap)
        profile.save()
    return redirect('savedWraps')

def refreshAuthDuo(request):
    next_url = request.GET.get('next', None)  # This is the next page to redirect after authorization, e.g., '/intro/'
    userID = request.GET.get('userID', None)
    request.session['next'] = next_url
    request.session['userID'] = userID
    print(next_url)
    print(userID)

    # Spotify OAuth parameters
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/userauth",
        # This should match the redirect URI you've registered with Spotify
        "scope": "user-library-read playlist-read-private user-top-read playlist-read-collaborative user-read-playback-position user-read-recently-played",
    }

    # Add 'next' parameter to the URL if they exist
    if next_url:
        params["next"] = next_url

    # Construct the Spotify authorization URL
    base_url = "https://accounts.spotify.com/authorize"
    url = f"{base_url}?{urlencode(params)}"

    # Print the URL for debugging purposes
    print(url)

    # Redirect the user to the Spotify authorization URL
    return redirect(url)

def refreshAuthDuoInv(request):
    request.session['next'] = '/start/'
    next_url = request.GET.get('next', None)
    print(next_url)

    # Spotify OAuth parameters
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/userauth",
        # This should match the redirect URI you've registered with Spotify
        "scope": "user-library-read playlist-read-private user-top-read playlist-read-collaborative user-read-playback-position user-read-recently-played",
    }

    # Add 'next' parameter to the URL if they exist
    if next_url:
        params["next"] = next_url

    # Construct the Spotify authorization URL
    base_url = "https://accounts.spotify.com/authorize"
    url = f"{base_url}?{urlencode(params)}"

    # Print the URL for debugging purposes
    print(url)

    # Redirect the user to the Spotify authorization URL
    return redirect(url)

def wrap_sum(request):
    return render(request, 'TechWrapper/wrapSum.html')

def endPageTwo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/endPageTwo.html', {'profile' : profile})
    return render(request, 'TechWrapper/endPageTwo.html')

def endDuoTwo(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'TechWrapper/endDuoTwo.html', {'profile' : profile})
    return render(request, 'TechWrapper/endDuoTwo.html')

def redirectPage(request):
    nextPage = request.session.get('lastPage')
    return redirect(nextPage)
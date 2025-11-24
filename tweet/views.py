from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm

from .models import Tweet, Like, Comment
from .forms import (
    TweetForm,
    UserRegistrationForm,
    ProfilePicForm,
    UsernameForm
)




def index(request):
    return render(request, 'index.html')

def tweet_list(request):
    query = (request.GET.get("q", "")).strip()

    if query:
        tweets = Tweet.objects.filter(Q(text__icontains=query)|Q(user__username__icontains=query)).order_by('-created_at')
    else:
        tweets = Tweet.objects.all().order_by('-created_at')

    # PAGINATION
    paginator = Paginator(tweets, 8)  # 8 ads per page
    page_number = request.GET.get("page")
    tweets = paginator.get_page(page_number)
 
    # --- Likes work ---
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    liked_tweets = Like.objects.filter(session_id=session_id).values_list('tweet_id', flat=True)

    return render(request, 'tweet_list.html', {
        'tweets': tweets,
        'liked_tweets': liked_tweets,
        'query': query,
    })


def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    like = Like.objects.filter(tweet=tweet, session_id=session_id).first()
    
    if like:
        like.delete()  # DISLIKE
    else:
        Like.objects.create(tweet=tweet, session_id=session_id)  # LIKE

    return redirect('tweet_list')


def comment_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    text = request.POST.get("comment")

    if text.strip():
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        if request.user.is_authenticated:
            Comment.objects.create(tweet=tweet, user=request.user, text=text)
        else:
            Comment.objects.create(tweet=tweet, session_id=session_id, text=text)

    return redirect('tweet_list')

def view_comments(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comments = tweet.comments.all().order_by('-created_at')

    return render(request, "view_comments.html", { "tweet": tweet, "comments": comments})


@login_required
def tweet_create(request):
    if request.method=='POST':
        form=TweetForm(request.POST,request.FILES)
        if form.is_valid():
            tweet=form.save(commit=False)
            tweet.user=request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form=TweetForm()
    return render(request,'tweet_form.html',{'form':form})

@login_required
def tweet_edit(request,tweet_id):
    tweet=get_object_or_404(Tweet,pk=tweet_id,user=request.user)
    if request.method=='POST':
        form=TweetForm(request.POST,request.FILES,instance=tweet)
        if form.is_valid():
            tweet=form.save(commit=False)
            tweet.user=request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form=TweetForm(instance=tweet)
    return render(request,'tweet_form.html',{'form':form})

@login_required
def tweet_delete(request,tweet_id):
    tweet=get_object_or_404(Tweet,pk=tweet_id,user=request.user)
    if request.method=='POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request,'tweet_confirm_delete.html',{'tweet':tweet})

def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request,user)
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request,'registration/register.html',{'form':form})


@login_required
def your_profile(request):
    tweets = Tweet.objects.filter(user=request.user).order_by('-id')
    return render(request, 'your_profile.html', {'tweets': tweets})

@login_required
def edit_profile_pic(request):
    profile = request.user.userprofile  # correct instance
    form = ProfilePicForm(instance=profile)

    if request.method == "POST":
        form = ProfilePicForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('your_profile')

    return render(request, 'edit_profile_pic.html', {'form': form})

@login_required
def edit_username(request):
    if request.method == "POST":
        form = UsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('your_profile')
    else:
        form = UsernameForm(instance=request.user)

    return render(request, 'edit_username.html', {'form': form})


@login_required
def edit_password(request):
    form = PasswordChangeForm(request.user)

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    return render(request, 'edit_password.html', {'form': form})

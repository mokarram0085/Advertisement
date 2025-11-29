from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from .models import Tweet, Like, Comment,Order
from .forms import TweetForm,UserRegistrationForm,ProfilePicForm,UsernameForm,OrderForm

from django.http import HttpResponseForbidden
from django.contrib import messages


def About_Us(request):
    return render(request,'About_Us.html')

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

# 🔥 Redirect back to the same page(url)
    return redirect(request.META.get('HTTP_REFERER', 'tweet_list'))


def comment_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    if request.method == "POST":
        text = request.POST.get("comment", "").strip()

        if text:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key

            if request.user.is_authenticated:
                Comment.objects.create(tweet=tweet, user=request.user, text=text)
            # else:
            #     Comment.objects.create(tweet=tweet, session_id=session_id, text=text)

        return redirect('view_comments', tweet_id=tweet_id)

    return redirect('view_comments', tweet_id=tweet_id)


def view_comments(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comments = tweet.comments.all().order_by('-created_at')

    # Session-based likes
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    liked = Like.objects.filter(tweet=tweet, session_id=session_id).exists()

    return render(request, "view_comments.html", { 
        "tweet": tweet, 
        "comments": comments,
        "liked": liked  
    })

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Only owner can edit
    if comment.user != request.user:
        return HttpResponseForbidden("You cannot edit this comment.")

    if request.method == "POST":
        new_text = request.POST.get("comment")
        comment.text = new_text
        comment.save()
        return redirect("view_comments", tweet_id=comment.tweet.id)
    return render(request, "edit_comment.html", {"comment": comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return HttpResponseForbidden("You cannot delete this comment.")

    tweet_id = comment.tweet.id
    comment.delete()
    return redirect("view_comments", tweet_id=tweet_id)

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
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # triggers post_save signal
            messages.success(request, "Account successfully created! You can now login.")
            return redirect('login')  # send user to login page
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



@login_required
def your_profile(request):
    tweets = Tweet.objects.filter(user=request.user).order_by('-id')

    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    # List of tweet IDs liked by this session
    liked_tweets = Like.objects.filter(session_id=session_id).values_list('tweet_id', flat=True)

    return render(request, 'your_profile.html', {
        'tweets': tweets,
        'liked_tweets': liked_tweets
    })


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

def view_user_profile(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    tweets = Tweet.objects.filter(user=user_obj).order_by('-created_at')

    # --- Likes Work ---
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    liked_tweets = Like.objects.filter(session_id=session_id).values_list("tweet_id", flat=True)

    return render(request, 'view_user_profile.html', {
        'profile_user': user_obj,
        'tweets': tweets,
        'liked_tweets': liked_tweets,
    })

# Open one tweet
def tweet_detail(request, id):
    tweet = get_object_or_404(Tweet, id=id)
    return render(request, 'tweet_detail.html', {'tweet': tweet})

#order_now
@login_required
def order_now(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        pin = request.POST.get("pin")
        address = request.POST.get("address")

        order = Order.objects.create(
            user=request.user,
            tweet=tweet,
            name=name,
            phone=phone,
            pin=pin,
            address=address
        )

        return redirect("order_success", order_id=order.id)

    return render(request, "order_now.html", {"order": tweet})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {"order": order})



@login_required
def all_orders(request):
    orders = Order.objects.select_related('user', 'tweet').order_by('-created_at')
    return render(request, 'all_orders.html', {'orders': orders})
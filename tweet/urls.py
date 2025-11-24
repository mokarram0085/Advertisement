from django.urls import path
from .import views
urlpatterns = [
    path('',views.tweet_list,name='tweet_list'),
    path('create/',views.tweet_create,name='tweet_create'),
    path('<int:tweet_id>/edit/',views.tweet_edit,name='tweet_edit'),
    path('<int:tweet_id>/delete/',views.tweet_delete,name='tweet_delete'),
    path('register/',views.register,name='register'),

    path('<int:tweet_id>/like/', views.like_tweet, name='like_tweet'),
    path('<int:tweet_id>/comment/', views.comment_tweet, name='comment_tweet'),
    path('<int:tweet_id>/comments/', views.view_comments, name='view_comments'),

    path('your_profile/', views.your_profile, name='your_profile'),
    path('edit-profile-pic/', views.edit_profile_pic, name='edit_profile_pic'),
    path('edit-username/', views.edit_username, name='edit_username'),
    path('edit-password/', views.edit_password, name='edit_password'),

]
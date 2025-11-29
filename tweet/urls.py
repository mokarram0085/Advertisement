from django.urls import path
from .import views
urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('about/', views.About_Us, name='About_Us'),

    # Tweet edit/delete
    path('<int:tweet_id>/edit/', views.tweet_edit, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),

    # Auth & registration
    path('register/', views.register, name='register'),

    # Tweet interaction
    path('<int:tweet_id>/like/', views.like_tweet, name='like_tweet'),
    path('<int:tweet_id>/comment/', views.comment_tweet, name='comment_tweet'),
    path('<int:tweet_id>/comments/', views.view_comments, name='view_comments'),

    # User profile
    path('your_profile/', views.your_profile, name='your_profile'),
    path('edit-profile-pic/', views.edit_profile_pic, name='edit_profile_pic'),
    path('edit-username/', views.edit_username, name='edit_username'),
    path('edit-password/', views.edit_password, name='edit_password'),

    path('profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),

    # COMMENT EDIT/DELETE 
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Open one card
    path('tweet_detail/<int:id>/', views.tweet_detail, name='tweet_detail'),

    # order URLs
    path('order_now/<int:tweet_id>/', views.order_now, name='order_now'),
    path("order_success/<int:order_id>/", views.order_success, name="order_success"),
    path('all_orders/', views.all_orders, name='all_orders'),


]
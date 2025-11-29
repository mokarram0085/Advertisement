from django.contrib import admin
from .models import Tweet,Like,Comment,UserProfile,Order

admin.site.register(Tweet)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Order) 
# Register your models here.

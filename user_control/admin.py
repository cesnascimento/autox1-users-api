from django.contrib import admin
from .models import CustomUser, UserActivities, TokenWPP, WPPGroup

admin.site.register((CustomUser, UserActivities, TokenWPP, WPPGroup))

from django.contrib import admin
from homepage.models import UserProfileInfo, User, Job, Applicant
# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(Job)
admin.site.register(Applicant)

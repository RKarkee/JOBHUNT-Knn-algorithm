from django.contrib import admin
from .models import User, Job, Profile, Applicant

# Register your models here.

admin.site.register(User)
admin.site.register(Job)
admin.site.register(Applicant)
admin.site.register(Profile)
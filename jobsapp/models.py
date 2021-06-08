from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'))

JOB_TYPE = (
    ('1', "Full time"),
    ('2', "Part time"),
    ('3', "Internship"),
)


class User(AbstractUser):
    username = None
    role = models.CharField(max_length=12, error_messages={
        'required': "Role must be provided"
    })
    gender = models.CharField(max_length=10, blank=True, null=True, default="")
    email = models.EmailField(unique=True, blank=False,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              })

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __unicode__(self):
        return self.email

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    location = models.CharField(max_length=150)
    type = models.CharField(choices=JOB_TYPE, max_length=10)
    work_experience = models.IntegerField(default=0)
    category = models.CharField(max_length=100)
    emailContact = models.CharField(max_length=100, default="")
    skill1 = models.CharField(max_length=100)
    skill2 = models.CharField(max_length=100)
    skill3 = models.CharField(max_length=100, blank=True)
    skill4 = models.CharField(max_length=100, blank=True)
    about_me = models.TextField()
    images = models.ImageField(upload_to='employeeProfiles', default='default.jpg')

    def __str__(self):
        return f'{self.user.first_name} Profile'

    def save(self, *args, **kwargs):
        if not 'force_insert' in kwargs:
            kwargs['force_insert'] = False
        if not 'force_update' in kwargs:
            kwargs['force_update'] = False
        super().save()

        img = Image.open(self.images.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.images.path)


def create_profile(sender, **kwargs):
    if kwargs['created']:
        Profile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)


def save_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(save_profile, sender=User)


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300, default='')
    description = models.TextField()
    location = models.CharField(max_length=150)
    type = models.CharField(choices=JOB_TYPE, max_length=10)
    category = models.CharField(max_length=100, default='')
    last_date = models.DateTimeField()
    skillRequired1 = models.CharField(max_length=100, default="")
    skillRequired2 = models.CharField(max_length=100, default="")
    skillRequired3 = models.CharField(max_length=100, blank=True, null=True)
    skillRequired4 = models.CharField(max_length=100, blank=True, null=True)
    work_experience = models.IntegerField(default=0)
    company_name = models.CharField(max_length=100)
    company_description = models.CharField(max_length=300)
    website = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(default=timezone.now)
    filled = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applicants')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.get_full_name()

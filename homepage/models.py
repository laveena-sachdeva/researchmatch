# dappx/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# from accounts.models import User

roles = (  
('Professor', 'Professor'),
('Student', 'Student'),
)

class UserProfileInfo(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name ="myuser")
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
    role = models.CharField(max_length=9, choices=roles, default = "Student")
    resume = models.FileField(upload_to='resume', blank=True)
    def __str__(self):
          return self.user.username


JOB_TYPE = (
    ('1', "Full time"),
    ('2', "Part time"),
    ('3', "Internship"),
)


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField()
    location = models.CharField(max_length=150)
    type = models.CharField(choices=JOB_TYPE, max_length=10)
    category = models.CharField(max_length=100)
    last_date = models.DateTimeField()
    company_name = models.CharField(max_length=100)
    company_description = models.CharField(max_length=300)
    website = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(default=timezone.now)
    filled = models.BooleanField(default=False)
    salary = models.IntegerField(default=0, null=True, blank=True)

    def set_user(self, user):
    	self.user  = user
    def __str__(self):
        return self.title

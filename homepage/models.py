# dappx/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# from accounts.models import User
import os
import mimetypes
from django.core.exceptions import ValidationError

def validate_is_pdf(file):
    valid_mime_types = ['application/pdf']
    # file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    file_mime_type = mimetypes.guess_type(file.name)
    print("mime type")
    print(file.name)
    print(file_mime_type)
    if file_mime_type[0] not in valid_mime_types:
        raise ValidationError('Unsupported file type.')
    valid_file_extensions = ['.pdf']
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_file_extensions:
        raise ValidationError('Unacceptable file extension.')


roles = (
('Professor', 'Professor'),
('Student', 'Student'),
)

class Universities(models.Model):
    num = models.CharField(max_length = 10, default = "")
    name = models.CharField(max_length = 100, default = "")

    def __str__(self):
        return self.name

def validate_file_extension(value):
    if value.file.content_type != 'application/pdf':
        raise ValidationError(u'Error message')

all_universities = Universities.objects.all()
all_universities = tuple((u.name,u.name) for u in all_universities)
# print(all_universities)

class UserProfileInfo(models.Model):
    full_name = models.CharField(max_length=300, blank = False)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name ="myuser")
    linkedin_url = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics')
    role = models.CharField(max_length=9, choices=roles, default = "Student")
    resume = models.FileField(upload_to='resume', validators=(validate_is_pdf,))
    skill_description = models.TextField(default="")
    university = models.CharField(max_length = 100, choices = all_universities, default = 'Arizona State University--Tempe' )
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
    workplace_name = models.CharField(max_length=100, blank = True)
    workplace_description = models.CharField(max_length=300, blank = True)
    website = models.CharField(max_length=100, default="", blank = True)
    created_at = models.DateTimeField(default=timezone.now)
    filled = models.BooleanField(default=False)
    salary = models.IntegerField(default=0, null=True, blank=True)

    def set_user(self, user):
    	self.user  = user
    def __str__(self):
        return self.title

APPLICATION_STATUS = (
    ('1', "Accept"),
    ('2', "Reject"),
    ('3', "In Process"),
)

class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applicants')
    status = models.CharField(choices=APPLICATION_STATUS,max_length=10,default="In Process")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

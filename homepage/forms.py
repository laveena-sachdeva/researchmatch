# dappx/forms.py
from django import forms
from homepage.models import UserProfileInfo, Job, Applicant
from django.contrib.auth.models import User

roles = (
('Professor', 'Professor'),
('Student', 'Student'),
)


class UserForm(forms.ModelForm):
        password = forms.CharField(widget=forms.PasswordInput())
        email = forms.CharField(required = True)

        class Meta():
            model = User
            fields = ('username','password','email')

class UserProfileInfoForm(forms.ModelForm):
    role = forms.ChoiceField(choices=roles, required=True )
    profile_pic = forms.ImageField(required = True)
    resume = forms.FileField(required=True, widget=forms.FileInput(attrs={'accept':'application/pdf'}))

    class Meta():
	    model = UserProfileInfo
	    fields = ('full_name','linkedin_url','profile_pic','role','resume','skill_description','university')



class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ('user', 'created_at',)
        # fields = ('user','title','description','location','type','category','last_date','workplace_name','workplace_description','website','created_at','filled','salary')
        labels = {
            "last_date": "Last Date",
            "workplace_name": "Workplace Name",
            "workplace_description": "Workplace Description"
        }

    def is_valid(self):
        valid = super(CreateJobForm, self).is_valid()

        # if already valid, then return True
        if valid:
            return valid
        return valid

    def save(self, commit=True):
        job = super(CreateJobForm, self).save(commit=False)
        if commit:
            job.save()
        return job


class ApplyJobForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('job',)

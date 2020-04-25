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
        class Meta():
            model = User
            fields = ('username','password','email')

class UserProfileInfoForm(forms.ModelForm):
    role = forms.ChoiceField(choices=roles, required=True )
    class Meta():
	    model = UserProfileInfo
	    fields = ('portfolio_site','profile_pic','role','resume','university')


# from jobsapp.models import Job, Applicant


class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ('user', 'created_at',)
        # fields = ('user','title','description','location','type','category','last_date','company_name','company_description','website','created_at','filled','salary')
        labels = {
            "last_date": "Last Date",
            "company_name": "Company Name",
            "company_description": "Company Description"
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


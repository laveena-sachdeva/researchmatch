#from django.views.generic import TemplateView
#class HomePageView(TemplateView):
#        template_name = 'home.html'
from django.shortcuts import render
from homepage.forms import UserForm,UserProfileInfoForm, CreateJobForm 
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse,Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from homepage.models import Job
from django.views.generic import ListView, DetailView, CreateView
import os

if os.getenv('GAE_APPLICATION', None):
    from google.cloud import storage


def upload_blob(bucket_name, source_file, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file)

    print(
        "File {} uploaded to {}.".format(
            source_file, destination_blob_name
        )
    )


class JobDetailsView(DetailView):
    model = Job
    template_name = 'details.html'
    context_object_name = 'job'
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super(JobDetailsView, self).get_object(queryset=queryset)
        if obj is None:
            raise Http404("Job doesn't exists")
        return obj

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # redirect here
            raise Http404("Job doesn't exists")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


def index(request):
        return render(request,'./index.html')

def index_student(request):
        return render(request,'./index.html')

@login_required
def post_a_job(request):
        return render(request,'./jobpost.html')

def index_professor(request):
        return render(request,'./index.html')

def jobs_list_view(request):
    alljobs= Job.objects.all()
    context= {'alljobs': alljobs}
    return render(request, './all_jobs.html', context)

def job_details(request,job_id):
    job = request.job
    return render(request,'./details.html')


@login_required
def save_job(request):
    # print(request)
    # return render(request,'./index.html')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        salary  = request.POST.get('salary')
        location = request.POST.get('location')
        type = request.POST.get('type')
        category = request.POST.get('category')
        apply_url = request.POST.get('apply_url')
        last_date = request.POST.get('last_date')
        company_name = request.POST.get('company_name')
        company_description = request.POST.get('company_description')
        website = request.POST.get('website')
        print(title)
        print(salary)
        print(type)
        print(website)

        create_job_form = CreateJobForm(data = request.POST)
        if create_job_form.is_valid():
            print("The form is valid")
            print("The user ")
            print(request.user)
            print("Saw that?")
            job = create_job_form.save(commit = False)
            job.user = request.user
            job.save()
        else:
            print("The form is invalid")
    return HttpResponseRedirect(reverse('index'))

# registered = False
#     if request.method == 'POST':
#         # print("Checkpoint 1")
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileInfoForm(data=request.POST)
#         if user_form.is_valid() and profile_form.is_valid():
#             # print("Checkpoint 2")

#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             if 'profile_pic' in request.FILES:
#                 # print("Checkpoint 3")

#                 print('found it')
#                 profile.profile_pic = request.FILES['profile_pic']
#             profile.save()
#             registered = True
#         else:
#             # print("Checkpoint 4")

#             print(user_form.errors,profile_form.errors)
#     else:
#         # print("Checkpoint 5")

#         user_form = UserForm()
#         profile_form = UserProfileInfoForm()
#     return render(request,'./registration.html', {'user_form':user_form, 'profile_form':profile_form,'registered':registered})
#     # print("Checkpoint 6")


@login_required
def special(request):
        return HttpResponse("You are logged in !")

@login_required
def user_logout(request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))

@login_required
def display_image(request, img):
    context = {
        'image': img
    }
    return render(request, 'image.html', context)
# # shows image in a new tab?
# def show_image(request, img):
    

def register(request):
    registered = False
    if request.method == 'POST':
        # print("Checkpoint 1")
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # print("Checkpoint 2")

            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                # print('found it')
                if os.getenv('GAE_APPLICATION', None):
                    file_obj = request.FILES['profile_pic']
                    # print(file_obj)
                    destination_blob_name= "profile_pics/" + user.username + "_profile_pic.jpg"
                    bucket_name = os.environ.get("BUCKET_NAME")
                    upload_blob(bucket_name,file_obj, destination_blob_name)
                else:
                    profile.profile_pic = request.FILES['profile_pic']
            if 'resume' in request.FILES:
                if os.getenv('GAE_APPLICATION', None):
                    file_obj = request.FILES['resume']
                    # print(file_obj)
                    destination_blob_name= "resume/" + user.username + "_resume.pdf"
                    bucket_name = os.environ.get("BUCKET_NAME")
                    upload_blob(bucket_name,file_obj, destination_blob_name)
                else:
                    print("Saving locally")
                    profile.resume = request.FILES['resume'] 
            profile.save()
            registered = True
        else:
            # print("Checkpoint 4")

            print(user_form.errors,profile_form.errors)
    else:
        # print("Checkpoint 5")

        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'./registration.html', {'user_form':user_form, 'profile_form':profile_form,'registered':registered})
    # print("Checkpoint 6")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # profile_pic = request.POST.get('profile_pic')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                form1 = UserProfileInfoForm(request.POST)
                if form1.is_valid():
                    portfolio_site = form1.cleaned_data['portfolio_site']
                    role = form1.cleaned_data['role']
                    if role == 'Student':
                        return HttpResponseRedirect(reverse('index_student'))
                    elif role == 'Professor':
                        return HttpResponseRedirect(reverse('index_professor'))

                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, './login.html', {})                                

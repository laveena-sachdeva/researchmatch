#from django.views.generic import TemplateView
#class HomePageView(TemplateView):
#        template_name = 'home.html'
from django.shortcuts import render
from homepage.content_classification import query, categorize
from homepage.forms import UserForm,UserProfileInfoForm, CreateJobForm, ApplyJobForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse,Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from homepage.models import Job, Applicant, UserProfileInfo, Universities
from django.views.generic import ListView, DetailView, CreateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from conversation.models import Conversation, Message
from django.contrib.auth.models import User
from datetime import date
# from homepage import generate_signed_url as gen
import time
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
        if request.user.myuser.role == "Professor":
            all_students = Applicant.objects.filter(job_id=kwargs['id']).values('user_id', 'status')
            user_data = list()
            for i in range(len(all_students)):
                user_info = UserProfileInfo.objects.get(user_id=all_students[i]['user_id'])
                user_data.append((user_info, all_students[i]['status'],0))
            try:
                print("Categorizing data")
                result = categorize(user_data)
                user_data = query(result, self.object.description)
                context['applied_data'] = user_data
            except:
                context['applied_data'] = user_data
        else:
            status = Applicant.objects.filter(job_id=kwargs['id'], user_id=request.user.id).values('status')
            if status:
                context['status'] = status[0]['status']
        context['role'] = UserProfileInfo.objects.get(user_id=request.user.id).role
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy('job_details', kwargs={'id': self.kwargs['job_id']})

    def post(self, request, *args, **kwargs):
        to_update = Applicant.objects.filter(user_id=kwargs['user_id'],job_id=kwargs['job_id'])
        to_update.update(status=request.POST.get("acceptance"))
        # return HttpResponse("Status updated")
        return HttpResponseRedirect(self.get_success_url())


class ApplyJobView(CreateView):
    model = Applicant
    form_class = ApplyJobForm
    slug_field = 'job_id'
    slug_url_kwarg = 'job_id'

    @method_decorator(login_required(login_url=reverse_lazy('user_login')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.info(self.request, 'Successfully applied for the job!')
            return self.form_valid(form)
        else:
            return HttpResponseRedirect(reverse_lazy('index'))

    def get_success_url(self):
        return reverse_lazy('job_details', kwargs={'id': self.kwargs['job_id']})

    # def get_form_kwargs(self):
    #     kwargs = super(ApplyJobView, self).get_form_kwargs()
    #     print(kwargs)
    #     kwargs['job'] = 1
    #     return kwargs

    def form_valid(self, form):
        # check if user already applied
        applicant = Applicant.objects.filter(user_id=self.request.user.id, job_id=self.kwargs['job_id'])
        if applicant:
            messages.info(self.request, 'You already applied for this job')
            return HttpResponseRedirect(self.get_success_url())
        # save applicant
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

@login_required
def delete_job(request, job_id):
    to_update = Job.objects.filter(id=job_id)
    to_update.delete()
    return HttpResponseRedirect(reverse('jobs_list_view'))

def index(request):
    try:
        role = UserProfileInfo.objects.get(user_id=request.user.id).role
        if role == "Student":
            alljobs= Job.objects.all()
            context= {'alljobs': alljobs}
            return render(request, './index.html', context)
        elif role == "Professor":
            alljobs = Job.objects.filter(user_id=request.user.id)
            context = {'alljobs': alljobs}
            return render(request, './index.html', context)
    except:
        return render(request, './index.html')


def index_student(request):
        return HttpResponseRedirect(reverse(index))

@login_required
def post_a_job(request):
        university_list = Universities.objects.all()
        return render(request,'./jobpost.html',{'university_list': university_list})

def index_professor(request):
        return HttpResponseRedirect(reverse(index))

def jobs_list_view(request):
    role = UserProfileInfo.objects.get(user_id=request.user.id).role
    if role == "Student":
        alljobs= Job.objects.all()
        context= {'alljobs': alljobs}
        return render(request, './all_jobs.html', context)
    elif role == "Professor":
        alljobs = Job.objects.filter(user_id=request.user.id)
        context = {'alljobs': alljobs}
        return render(request, './all_jobs.html', context)

def job_details(request,job_id):
    job = request.job
    return render(request,'./details.html')

def applied_jobs_view(request):
    allapplications = Applicant.objects.filter(user_id=request.user.id)
    context = {}
    if allapplications:
        context = {'alljobs': allapplications, 'applied':True}
    return render(request, './all_applied_jobs.html', context)

def filter_jobs_view(request):
    filter = request.GET.get("filter")
    prof = request.GET.get("prof")
    university = request.GET.get("university")
    print(filter,prof)
    print(request.user.id)
    if filter == "All":
        alljobs = Job.objects.all()
        print(alljobs)
        context = {'alljobs': alljobs}
        # return HttpResponseRedirect(self.get_success_url())
        return render(request, './all_applied_jobs.html', context)
    elif filter == "Applied":
        allapplications = Applicant.objects.filter(user_id=request.user.id)
        context = {}
        result = []
        for entry in allapplications:
            result.append({'id':entry.job.id,'title':entry.job.title,'location':entry.job.location,'type':entry.job.type,'description':entry.job.description,'status':entry.status})

        if allapplications:
            context = {'alljobs': result, 'applied': True}
        return render(request, './all_applied_jobs.html', context)
    elif filter == "Professor":
        prof_list = UserProfileInfo.objects.filter(role="Professor")
        if prof_list:
            return render(request, './all_applied_jobs.html', {'prof_list':prof_list})
    elif prof:
        alljobs = Job.objects.filter(user_id=prof)
        if alljobs:
            prof_name = UserProfileInfo.objects.get(user_id=prof).full_name
            context = {'alljobs': alljobs,'prof_name':prof_name}
            return render(request, './all_applied_jobs.html', context)
    elif filter == "University":
        university_list = Universities.objects.all()
        return render(request, './all_applied_jobs.html', {'university_list': university_list})
    elif university:
        alljobs = Job.objects.filter(workplace_name=university)
        if alljobs:
            context = {'alljobs': alljobs,'university':university}
            return render(request, './all_applied_jobs.html', context)
    else:
        return render(request, './all_applied_jobs.html', {})


def delete_invalid_jobs(request):
    to_update = Job.objects.filter(last_date__date__lt=date.today())
    print(to_update)
    to_update.delete()
    return HttpResponse(status=204)

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
    if request.user:
        if request.user.is_authenticated:
            user_logout(request)
    registered = False
    if request.method == 'POST':
        # print("Checkpoint 1")
        user_form = UserForm(request.POST, request.FILES)
        profile_form = UserProfileInfoForm(request.POST,request.FILES)
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
                    profile.resume = None
                    profile.profile_pic= None
                    profile.save()
                else:
                    print("Saving locally")
                    profile.resume = request.FILES['resume'] 
                    profile.save()
            registered = True
        else:
            print("Checkpoint 4")

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
                    linkedin_url = form1.cleaned_data['linkedin_url']
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

@login_required
def see_conversations(request,my_id):
    allusers = User.objects.get(id=my_id)
    context = {}
    if allusers:
        c = allusers.conversations.all()
        if c:
            context = {'conversations':c}

    return render(request,'./conversation_list.html',context)

@login_required
def all_people(request):
    allpeople= User.objects.all()
    context= {'allusers': allpeople}
    return render(request, './people.html', context)


# def sign_url(obj, expires_after_seconds=60):

#     client = storage.Client()
#     default_bucket = os.environ.get("BUCKET_NAME")
#     bucket = client.get_bucket(default_bucket)
#     blob = storage.Blob(obj, bucket)

#     expiration_time = int(time.time() + expires_after_seconds)

#     url = blob.generate_signed_url(expiration_time)

#     return url


def sign_url(filename):
    import os, google.auth
    from google.auth.transport import requests
    from google.auth import compute_engine
    from datetime import datetime, timedelta
    from google.cloud import storage

    auth_request = requests.Request()
    credentials, project = google.auth.default()
    storage_client = storage.Client(project, credentials)
    data_bucket = storage_client.lookup_bucket(os.getenv("BUCKET_NAME"))
    signed_blob_path = data_bucket.blob(filename)
    expires_at_ms = datetime.now() + timedelta(minutes=60)
    signing_credentials = compute_engine.IDTokenCredentials(auth_request, "", service_account_email=storage_client._credentials.service_account_email,)
    signed_url = signed_blob_path.generate_signed_url(expires_at_ms, credentials=signing_credentials, version="v4")
    return signed_url

@login_required
def view_profile(request, user_id):

    allinfo = User.objects.get(id = user_id)
    ctx = {'allinfo':allinfo}

    if os.getenv('GAE_APPLICATION', None):
        bucket_name = os.environ.get("BUCKET_NAME")
        resume_link = sign_url("resume/" + allinfo.username + "_resume.pdf")
        profile_link = sign_url("profile_pics/" + allinfo.username + "_profile_pic.jpg")
        ctx['resume_link'] = resume_link
        ctx['profile_link'] = profile_link

    return render(request, './profile.html', ctx)


@login_required
def update_profile(request, user_id):
    allinfo = User.objects.get(id = user_id)
    univs = Universities.objects.all()
    ctx = {"allinfo": allinfo, 'univs':univs}
    # return HttpResponse("updating profile")
    if os.getenv('GAE_APPLICATION', None):
        bucket_name = os.environ.get("BUCKET_NAME")
        resume_link = sign_url("resume/" + allinfo.username + "_resume.pdf")
        profile_link = sign_url("profile_pics/" + allinfo.username + "_profile_pic.jpg")
        ctx['resume_link'] = resume_link
        ctx['profile_link'] = profile_link
    return render(request, './update_profile.html', ctx)

@login_required

def update_profile_in_db(request):
    if request.method == 'POST':
        linkedin = request.POST.get('linkedin')
        print("linkedin")
        print(linkedin)
        description = request.POST.get('description')
        print(description)
        univ = request.POST.get('university')
        print(univ)

        updatedUser = UserProfileInfo.objects.get(user_id = request.user.id)
        updatedUser.linkedin_url = linkedin
        updatedUser.skill_description = description
        updatedUser.university = univ
        if 'profile_pic' in request.FILES:
            if os.getenv('GAE_APPLICATION', None):
                file_obj = request.FILES['profile_pic']
                # print(file_obj)
                destination_blob_name= "profile_pics/" + request.user.username + "_profile_pic.jpg"
                bucket_name = os.environ.get("BUCKET_NAME")
                upload_blob(bucket_name,file_obj, destination_blob_name)
            else:
                updatedUser.profile_pic = request.FILES['profile_pic']
        if 'resume' in request.FILES:
            if os.getenv('GAE_APPLICATION', None):
                file_obj = request.FILES['resume']
                # print(file_obj)
                destination_blob_name= "resume/" + request.user.username + "_resume.pdf"
                bucket_name = os.environ.get("BUCKET_NAME")
                upload_blob(bucket_name,file_obj, destination_blob_name)
            else:
                updatedUser.resume = request.FILES['resume'] 
        updatedUser.save()
    return HttpResponse("updated")

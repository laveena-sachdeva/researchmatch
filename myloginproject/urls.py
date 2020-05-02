"""myloginproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from homepage import views
from homepage.views import *
from myloginproject import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('', include('homepage.urls')),
#    path('accounts/', include('django.contrib.auth.urls')),
#]
urlpatterns = [
            path('admin/', admin.site.urls),
                url(r'^$',views.index,name='index'),
                url(r'^student$',views.index_student,name='index_student'),
                url(r'^professor$',views.index_student,name='index_professor'),
                    url(r'^special/',views.special,name='special'),
                        url(r'^homepage/',include('homepage.urls')),
                            url(r'^logout/$', views.user_logout, name='logout'),
                            url(r'^jobpost/$', views.post_a_job, name='job_form'),
                            url(r'^save_job/$', views.save_job, name='save_job'),
                            url(r'^alljobs/$', views.jobs_list_view, name='jobs_list_view'),
                            url(r'^appliedjobs/$', views.applied_jobs_view, name='applied_jobs_view'),
                            url(r'^delete-jobs/$', views.delete_invalid_jobs, name='delete_invalid_jobs'),
                            path(r'^job_details/<int:id>$',JobDetailsView.as_view(),name='job_details'),
                            path(r'^job_details/<int:user_id>/<int:job_id>$',JobDetailsView.as_view(),name='app_status'),
                            path('apply-job/<int:job_id>', ApplyJobView.as_view(), name='apply-job'),
                            path('delete-job/<int:job_id>', views.delete_job, name='delete-job'),
                             # url(r'^media/profile_pics/(.*.jpeg)$', views.display_image, name='display_image'),
                            url(r'conversation/', include('conversation.urls')),
                            url(r'^see_conversations/(\d+)/$', views.see_conversations, name='see_conversations'),
                            # url(r'^conversation_form/$', views.conversation_form, name='conversation_form'),
                            url(r'^all_people/$', views.all_people, name='all_people'),
                            path(r'view_profile/<int:user_id>', views.view_profile, name='view_profile'),
                            url(r'^jobs/$', views.filter_jobs_view, name='jobs'),
                            path(r'update/<int:user_id>/', views.update_profile, name='update_profile'),
                            url(r'^update_profile/$', views.update_profile_in_db, name='update_profile_in_db'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
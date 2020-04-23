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
                            url(r'^job_details/([0-9]*)/$',views.job_details,name='job_details'),

                             # url(r'^media/profile_pics/(.*.jpeg)$', views.display_image, name='display_image'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
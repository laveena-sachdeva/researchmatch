from django.urls import path
# from .views import HomePageView
from homepage import views
from django.conf.urls import url

# SET THE NAMESPACE!
app_name = 'homepage'
#urlpatterns = [
#            path('', HomePageView.as_view(), name='home'),
#            ]
# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
            url(r'^register/$',views.register,name='register'),
                url(r'^user_login/$',views.user_login,name='user_login'),
                ]

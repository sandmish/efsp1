from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path

from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeDoneView, PasswordChangeView

from portfolio import views

urlpatterns = [
    path('admin/', admin.site.urls, ),
    path('', include('portfolio.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_change/', PasswordChangeView.as_view(),
         name='password_change'),
    path('password_change/done/', PasswordChangeView.as_view(),
         name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    url('^accounts/', include('django.contrib.auth.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
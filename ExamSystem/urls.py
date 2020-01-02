from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


from accounts import views


urlpatterns = [
    path('', views.login_redirect, name='redirect_login'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('home/', include('general_pages.urls')),
    path('teams/', include('teams.urls')),
    path('exam_papers/', include('exam_paper.urls')),
    path('details/', include('details.urls'))
]

# For dev purposes to control file upload/retrieval on dev server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
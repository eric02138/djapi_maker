from django.urls import path, include
from api import views

from db_to_apize import urls as db_to_apize_urls


urlpatterns = [
    path('', views.AppList.as_view(), name='app_list_view'),

    path('db_to_apize/', include(db_to_apize_urls)),

]

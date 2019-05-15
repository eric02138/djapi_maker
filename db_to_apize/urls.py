from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from db_to_apize import views

urlpatterns = [
    path('', views.ModelList.as_view(), name='model_list_view'),
    path('authors', views.AuthorsList.as_view(), name='authors_list_view'),
    path('authors/<int:pk>/', views.AuthorsDetail.as_view(), name='authors_detail_view'),
    path('posts', views.PostsList.as_view(), name='posts_list_view'),
    path('posts/<int:pk>/', views.PostsDetail.as_view(), name='posts_detail_view'),
]

urlpatterns = format_suffix_patterns(urlpatterns)


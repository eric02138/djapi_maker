from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from db_to_apize.serializers import AuthorsSerializer
from db_to_apize.models import Authors

from db_to_apize.serializers import PostsSerializer
from db_to_apize.models import Posts



class AuthorsList(generics.ListCreateAPIView):
    queryset = Authors.objects.all()
    serializer_class = AuthorsSerializer

class AuthorsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Authors.objects.all()
    serializer_class = AuthorsSerializer

class PostsList(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

class PostsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer


class ModelList(APIView):
    def get(self, request, format=None):
        model_list = []

        model = {
            'model': 'authors',
            'url': reverse('authors_list_view', request=request)
        }
        model_list.append(model)

        model = {
            'model': 'posts',
            'url': reverse('posts_list_view', request=request)
        }
        model_list.append(model)

        return Response(model_list)
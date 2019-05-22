from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

class AppList(APIView):
    def get(self, request, format=None):
        app_list = []

        app = {
            'app_name': 'db_to_apize',
            #'url': '/api/db_to_apize'   #reverse url this when I'm not so tired and dumb
            'url': reverse('db_to_apize_list_view',  request=request)
        }
        app_list.append(app)

        return Response(app_list)

from django.views import View
from django.http import JsonResponse

class HelloWord(View):
    def get(self, request):
        v1=request.GET.get('v1')
        v2=request.GET.get('v2')
        return JsonResponse({"ok":True,"message": "Buildings. Helloworld. By get", "data":[v1,v2]})
    def post(self, request):
        v1=request.POST.get('v1')
        v2=request.POST.get('v2')
        return JsonResponse({"ok":True,"message": "Buildings. Helloworld. By post", "data":[v1, v2]})


# Create your views here.

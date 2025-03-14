# Create your views here.
#Django imports
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.forms.models import model_to_dict

#Geoss
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import SnapToGrid


#rest_framework imports
from rest_framework import viewsets
from rest_framework import permissions

#My imports
from core.myLib.geometryChecks import GeometryChecks
from .models import Buildings
from .serializers import BuildingsSerializer
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION

def custom_logout_view(request):
    logout(request)
    return redirect("/accounts/login/")  # O a donde desees redirigir después del logout

class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Buildings. Hello world", "data":[]})

class BuildigsView(View):
    """
    DJANGO CLASS BASED VIEW

    This class is a class based view that will handle the insert, 
    update, delete and select operations over the Buildings model.

    The class has the following methods:
        -get() -> Handles the select operation. It will return the record with the id.
        -post() -> Handles the insert, update, and delete operations.

    To get a record, the URL must be like:
        GET /buildings_view/selectone/<id>/
    To get all the records, the URL must be like:
        GET /buildings_view/selectall/
    To insert a record, the URL must be like:
        POST /buildings_view/insert/ --> The data must be sent in the body of the request.
    To update a record, the URL must be like:
        POST /buildings_view/update/<id>/ --> The data must be sent in the body of the request.
    To delete a record, the URL must be like:
        POST /buildings_view/delete/<id>/
    """
    def get(self, request, *args, **kwargs):
        """Handles the 'select' method with a GET request."""
        action=kwargs.get('action')
        if action == 'selectone':
            id = kwargs.get('id')
            return self.selectone(id)
        elif action == 'selectall':
            return self.selectall()
        else:            
            return JsonResponse({"message": "Invalid operation option"}, status=400)

    def post(self, request, *args, **kwargs):
        """Handles insert, update, and delete depending on the URL parameter."""
        action = kwargs.get('action')
        
        if action == 'insert':
            return self.insert(request)
        elif action == 'update':
            id = kwargs.get('id')
            return self.update(request, id)
        elif action == 'delete':
            id = kwargs.get('id')
            return self.delete(id)
        else:
            JsonResponse({"message": "Invalid operation option"}, status=400)
    
    #GET OPERATIONS
    def selectone(self, id):
        return JsonResponse({"message": "Select one method called"}, status=200)

    def selectall(self):
        return JsonResponse({"message": "Select all method called"}, status=200)

    #POST OPERATIONS
    def insert(self, request):
        """
        Inserts the polygon. Latter snap it to the grid. This must be done
        in the database. So we need to insert before.
        After the building has been inserted:
            - snap it to grid
            - Check if the geometry is valid
            - Check if the interior intersects with other geometry
            - If any check fails, remove the row.
            - The only inconvenient is the id counter sums one more
        """

        #Creates the geometry
        g=GEOSGeometry(request.POST.get('geom',''), srid=EPSG_FOR_GEOMETRIES)
        #print the representation of the object
        print(f"Original geometry: {g}")

        description = request.POST.get('description','') 
        b=Buildings(description=description, area=g.area, geom=g)
        b.save()
        print(f"Geometry inserted id: {b.id}")

        #Update the geometry to an snaped one yo the grid
        Buildings.objects.filter(id=b.id).update(geom=SnapToGrid('geom', ST_SNAP_PRECISION))

        #Now we get a new object with the new geometry to perform the checks
        b=Buildings.objects.get(id=b.id)
        print('Snapped geometry',b.geom.wkt)
        bGeos=GEOSGeometry(b.geom.wkt, srid=25830)
        valid=bGeos.valid
        print(f'Valid: {valid}')
        if not valid:
            print(f"Deleting invalid geometry {b.id}")
            b.delete()
            return JsonResponse({'ok':False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data':[]}, status=400)   

        #create a filter to get all the geometries which interiors intersects,
        #but excluding the one just created
        filt=Buildings.objects.filter(geom__relate=(g.wkt,'T********')).exclude(id=b.id)
        print(f"Query:{filt.query}")
        exist=filt.exists()
        print(f"Exists {exist}") 
        n=filt.count() 
        print(f"Count: {n}")
        print(f"Values: {list(filt)}")
        
        if exist:
            print(f"Deleting de building id {b.id}, as it intersects with others")
            b.delete()
            return JsonResponse({'ok':False, 'message': f'The building intersects with {n} building/s'}, status=400)
        
        #create a building object, from the model Buildings
        d=model_to_dict(b)
        d['geom']=bGeos.wkt
        return JsonResponse({'ok':True, 'message': 'Data inserted', 'data': [d]}, status=201)

    def update(self, request, id):
        """
        On update you shoud also check the new geometry: snap it, check if it is valid,
            check if it intersects with others except itself.
        
        The problem here is, if after having updated the geometry, if it is not valid, 
            or interesects with others, you must restore the original geometry.
            This is perfectry possible but we are not going to do it, istead
            we are going to use a psycop connection and a raw sql query to
            get the snapped geometry as wkb. This demonstrates
            some times it is better to know raw sql.

        """
        l=list(Buildings.objects.filter(id=id))
        if len(l)==0:
            return JsonResponse({'ok':False, "message": f"The building id {id} does not exist", "data":[]}, status=200)
        originalWkt=request.POST.get('geom', None)
        
        if originalWkt is not None:
            gc=GeometryChecks(originalWkt)
            newWkt=gc.get_as_wkt()
            geojson=gc.get_as_geojson()
            isValid=gc.is_geometry_valid()
            interesectionIds=gc.check_st_relate('buildings_buildings','T********')

            print(f"Snaped wkt: {newWkt}")
            print(f"Snaped geojson: {geojson}")
            print(f"Snaped is valid: {isValid}")
            print(f"Snaped intersection ids: {interesectionIds}")
            print(f"There are intersection ids: {gc.there_are_stRelatedIds()}")
            if not(isValid):
                return JsonResponse({'ok':False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data':[]}, status=400)   
            if gc.there_are_stRelatedIds():
                return JsonResponse({'ok':False, 'message': gc.get_st_relate_message(), 'data':[]}, status=400)   

        return JsonResponse({'ok':True, 'message': "Building updated", 'data':[]}, status=200)   


    def delete(self, id):
        return JsonResponse({"message": "Delete method called"}, status=200)

    
class BuildingsModelViewSet(viewsets.ModelViewSet):
    """
    DJANGO REST FRAMEWORK VIEWSET.

    The ModelViewSet class is a special view that Django Rest Framework 
        provides to handle the CRUD operations of a model
    
    The actions provided by the ModelViewSet class are:
        -list()  -> GET operation over /buildings/buildings/. It will return all reccords
        -retrieve() ->GET operation over /buildings/buildings/<id>/. 
                    It will return the record with the id.
        -create() -> POST operation over /buildings/buildings/. It will insert a new record
        -update() -> PUT operation over /buildings/buildings/<id>/. 
                    It will update the record with the id.
        -partial_update() -> PATCH operation over /buildings/buildings/<id>/. 
                It will update partially the record with the id.
                The difference between update and partial_update is that the first one
                will update all the fields of the record, while the second one will update
                only the fields that are present in the request.
        -destroy() -> DELETE operation over /buildings/buildings/<id>/. 
                It will delete the record with the id.
    """
    queryset = Buildings.objects.all()#The opeartions will be done over all the records of the Buildings model
    serializer_class = BuildingsSerializer#The serializer that will be used to serialize 
                            #the data. and check the data that is sent in the request.
    permission_classes = [permissions.AllowAny]#Any can use it.
                                # Use https://rsinger86.github.io/drf-access-policy/
                                # to more advanced permissions management

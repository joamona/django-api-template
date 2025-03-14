from django.db import connection
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION

class GeometryChecks:
    def __init__(self, geom_text, 
                 is_wkt=True, 
                 epsg_for_geometries=EPSG_FOR_GEOMETRIES,
                 st_snap_precision=ST_SNAP_PRECISION):
        
        self.geom_text=geom_text
        self.is_wkt=is_wkt
        self.epsg_for_geometries=epsg_for_geometries
        self.st_snap_precision=st_snap_precision
        self.__geom_binary=None
        self.__stRelatedIds=None
        self.__stRelateMessage=None

        if self.is_wkt:
            self.__geom_binary = self.__convert_wkt_to_wkb()
        else:
            self.__geom_binary = self.__convert_geojson_to_wkb()

    def get_as_binary(self):
        """
        Returns the snaped geometry in wkb
        """
        return self.__geom_binary

    def get_as_geojson(self):
        """
        Returns the snaped geometry in geojson
        """
        query="SELECT ST_AsGeojson(%s)"
        cursor=connection.cursor()
        cursor.execute(query,[self.get_as_binary()])
        row = cursor.fetchone()
        return row[0] if row else None  #Devuelve la geometría en formato geojson o None
    
    def get_as_wkt(self):
        """
        Returns the snaped geometry in wkt
        """
        query="SELECT ST_AsText(%s)"
        cursor=connection.cursor()
        cursor.execute(query, [self.get_as_binary()])
        row = cursor.fetchone()
        return row[0] if row else None  #Devuelve la geometría en formato geojson o None

    def is_geometry_valid(self):
        """Checks if a geometry in geojson is valid."""
        print('is_geometry_valid')
        cursor=connection.cursor()
        q="""SELECT ST_IsValid(%s)"""
        cursor.execute(q, [self.get_as_binary()])
        row = cursor.fetchone()
        #row is true or false
        return row[0]

    def there_are_stRelatedIds(self)->bool:
        """
        First must call check_st_relate, or raise exception
        If there hare related ids returns true
        """
        if self.__stRelatedIds is None:
            raise Exception("You first have to call check_st_relate")
        else:
            if len(self.__stRelatedIds)==0:
                return False
            else:
                return True
            
    def check_st_relate(self, layerName: str, matrix9IM: str)->list:
        """Checks whether or not exists a geometry wih the relation of the geom with all the geometries in the layer
            layername using the matrix 9IM. The geom is in geojson format.
        """
        self.__matrix9IM=matrix9IM
        cursor=connection.cursor()
        q=f"""SELECT id FROM {layerName} WHERE ST_relate(geom,%s,%s)"""
        cursor.execute(q, [self.get_as_binary(), matrix9IM])
        self.__stRelatedIds = cursor.fetchall()
        if self.there_are_stRelatedIds():
            self.__stRelateMessage=f"The following ids of the table {layerName} have the relation {matrix9IM} with the geometry: {self.__stRelatedIds}"
        else:
            self.__stRelateMessage=f"There are not geometries of the table {layerName} with the relation {matrix9IM} with the geometry"

        return self.__stRelatedIds  # Devuelve los ids de las geometrías que cumplen la relación

    def get_st_relate_message(self)->str:
        if self.__stRelatedIds is None:
            raise Exception("You first have to call check_st_relate")
        return self.__stRelateMessage
            
    def __convert_geojson_to_wkb(self):
        with connection.cursor() as cursor:
            #Ejecuta la función PostGIS ST_GeomFromText para convertir WKT a WKB
            print('convert_geojson_to_wkb')
            q="""SELECT 
                    ST_SNAPTOGRID(
                        st_setsrid(
                            ST_GeomFromGeoJSON(%s)
                            ,%s
                        ),
                        %s
                    )
                """
            cursor.execute(q, [self.geom_text, self.epsg_for_geometries, self.st_snap_precision])
            row = cursor.fetchone()
            return row[0]  # Esto será el WKB

    def __convert_wkt_to_wkb(self):
        with connection.cursor() as cursor:
            #Ejecuta la función PostGIS ST_GeomFromText para convertir WKT a WKB
            print('convert_wkt_to_wkb')
            q="""SELECT 
                    ST_SNAPTOGRID(
                        st_setsrid(
                            ST_GeomFromText(%s)
                            ,%s
                        ),
                        %s
                    )
                """
            cursor.execute(q, [self.geom_text, self.epsg_for_geometries, self.st_snap_precision])
            row = cursor.fetchone()
            return row[0]  # Esto será el WKB



# Create your views here.
#Django imports
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_out

#rest framework imports
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView

from knox.views import LoginView as KnoxLoginView
from knox.models import AuthToken # Necesario para eliminar todos los tokens
from knox.auth import TokenAuthentication

#mis módulos
from core import serializers
#from core.commonLibs import knox, managePermissions
from core.myLib import manageUsers, knoxSessions
from djangoapi.settings import REST_KNOX, DJANGO_KNOX_AUTOMATICALLY_REMOVE_TOKENS

def notLoggedIn(request: HttpRequest):
    return JsonResponse({"ok":False,"message": "You are not logged in", "data":[]})

class IsValidToken(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.EmptySerializer
    def post(self, request, format=None):
        token = request.META.get('HTTP_AUTHORIZATION', False)
        if token:
            try:
                # 1. Decodificar el token del header
                # La cabecera es 'Token <el_token>', así que separamos y codificamos.
                token_key = str(token).split()[1].encode("utf-8")
            except IndexError:
                # El formato del token es incorrecto (ej: falta la palabra 'Token')
                return Response({"messages": {"error_solicitud":"Formato de token de autorización incorrecto. Ej: falta la palabra 'Token'"}, "politica_acceso":{"acceso":"Permiso denegado."}, "data":None}, status=status.HTTP_401_UNAUTHORIZED)

            knoxAuth = TokenAuthentication()
            try:
                # 2. Intentamos autenticar. Si falla, se lanza AuthenticationFailed.
                user, auth_token = knoxAuth.authenticate_credentials(token_key)   

            except AuthenticationFailed as e:
                return Response({
                        "messages": {
                            "detail": e.detail,
                            "error_solicitud": "Token no válido o expirado."
                        },
                        "politica_acceso":{"acceso":"Permiso denegado."},
                        'data':None
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED)

            # Si llegamos aquí, el token es válido.
            groups = manageUsers.getUserGroupsAsDict(user.username)
            os=knoxSessions.getOpenedKnoxSessions(user.username)
                
            return Response({
                'messages':{'exito':'Identificación realizada con éxito'},
                "politica_acceso":{"acceso":"Acceso permitido."},
                'data': [{"detail": "Token Válido.", "username": user.username, "user": user.id,
                        "groups":groups, "opened_sessions":os}]})
        else: 
            return Response({'messages':{'error_solicitud':'Token no encontrado'},"politica_acceso":{"acceso":"Acceso permitido a todos."}, 'data':None}, status=status.HTTP_401_UNAUTHORIZED)

class KnoxLogin(KnoxLoginView):
    """
    Login con usuario y contraseña.
    """
    permission_classes = (AllowAny, )
    authentication_classes = [] # Esto sustituye al decorador
    serializer_class = serializers.LoginViewWithKnoxSerializer

    def post(self, request, format=None):
        """
        Login de usuario:
        
        Este endpoint permite la autenticación de usuarios. Debes enviar 
        las credenciales en el cuerpo de la petición (form-data o json).
        """
        serializer = self.serializer_class(data=request.data)
        valid= serializer.is_valid(raise_exception=False)#así, si no es válido, no lanza excepción, 
                #y se ejecuta el else:
        messages={}
        sesiones_borradas=False
        if valid:
            user:User = serializer.validated_data['user']
            os=knoxSessions.getOpenedKnoxSessions(request.data['username'])
            if DJANGO_KNOX_AUTOMATICALLY_REMOVE_TOKENS:
                TOKEN_LIMIT_PER_USER=REST_KNOX['TOKEN_LIMIT_PER_USER']
                if os == TOKEN_LIMIT_PER_USER-1:
                    #Borra todos los tokens anteriores
                    AuthToken.objects.filter(user=user).delete() 
                    messages['sesiones_borradas']=f'Habría alcanzado el número máximo de sesiones abiertas {TOKEN_LIMIT_PER_USER}. Se han cerrado todas y abierto una nueva'
                    sesiones_borradas=True
            login(request, user)
            #Crea el nuevo token
            response = super().post(request, format=None)
            if sesiones_borradas:
                os=1
            else:
                os=os+1
        else:
            return Response({"messages": serializer.errors, "politica_acceso": {"acceso":"Acceso denegado"},"data":None }, status=status.HTTP_401_UNAUTHORIZED)
        #print('Validated data') 
        #print(serializer.validated_data)
        v=response.data #the response with the authentication token
        groups = manageUsers.getUserGroupsAsDict(request.data['username'])
        v['groups'] = groups #la lista de grupos a los que pertenece el usuario
        v['username'] = request.data['username']

        v['opened_sessions']= os
        v["user"]= user.id
        messages['exito']='Identificación realizada con éxito'
        return Response({'messages':messages,"politica_acceso": {"acceso":"Permitido"},'data':[v]}, status=status.HTTP_200_OK)

class KnoxLogout(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.EmptySerializer
    def post(self, request, format=None):
        token = request.META.get('HTTP_AUTHORIZATION', False)
        if token:
            try:
                token_key = str(token).split()[1].encode("utf-8")
            except IndexError:
                # ... manejo de error de formato ...
                return Response({"messages": {"error_solicitud":"Formato de token de autorización incorrecto. Ej: falta la palabra 'Token'"}, "politica_acceso":{"acceso":"Acceso denegado."}, "data":None}, status=status.HTTP_401_UNAUTHORIZED)
            
            knoxAuth = TokenAuthentication()
            
            try:
                # 2. Intentamos autenticar. auth_token es la instancia del modelo AuthToken.
                user, auth_token = knoxAuth.authenticate_credentials(token_key)
                
            except AuthenticationFailed as e:
                # ... manejo de token inválido/expirado ...
                return Response({
                        "messages": {
                            "detail": e.detail,
                            "error_solicitud": "Token no válido o expirado."
                        },
                        "politica_acceso":{"acceso":"Acceso denegado."},
                        'data':None
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED)
        else:
            # ... manejo de token no encontrado ...
            return Response({'messages':{'error_solicitud':'Token no encontrado'},"politica_acceso":{"acceso":"Acceso denegado."}, 'data':None}, status=status.HTTP_401_UNAUTHORIZED)

        # ----------------------------------------------------
        # LÓGICA DE CIERRE DE SESIÓN:
        # ----------------------------------------------------
        
        # 1. Elimina el token de la base de datos (invalida la sesión)
        #    Usamos el objeto AuthToken devuelto por authenticate_credentials
        auth_token.delete() # <--- ¡SOLUCIÓN!

        # Si existe una sesión de Django activa (gestionada por cookies/middleware)
        if hasattr(request, 'session') and request.session.session_key:
            request.session.flush() # Esto elimina la fila de public.django_session

        # 2. Envía la señal (usa 'user' y 'request' que ya tienes)
        user_logged_out.send(
            sender=user.__class__, # Usamos la clase del objeto user
            request=request, 
            user=user # Usamos el objeto user autenticado
        )
        
        # 3. Respuesta de éxito
        return Response({
            "messages": {
                "exito": "Sesión cerrada."
            },
            "politica_acceso":{"acceso":"Acceso permitido."},
            'data':None
        }, status=status.HTTP_200_OK)

class LogoutAllUserSessionsView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.LogoutAllUserSessionsSerializer
    def post(self, request, format=None):
        """
        Cierra todas las sesiones (tokens) de un usuario específico.
        Requiere el token actual en el header y el username en el cuerpo.
            - El token debe corresponder al usuario cuyo username se envía.
            - Si lo anterior no pasa, si el usuario pertenece a un grupo con permisos especiales,
                ["admin"],
                se le permite cerrar las sesiones de otros usuarios.
        """
        
        # ----------------------------------------------------
        # 1. Extracción de Datos y Validaciones Iniciales
        # ----------------------------------------------------
        
        # Obtener el token del header
        header_token = request.META.get('HTTP_AUTHORIZATION', False)
        
        # Obtener el username del cuerpo de la petición (POST data)
        posted_username = request.data.get('username')
        
        # Validar si falta el username
        if not posted_username:
            return Response({
                "messages": {"error_solicitud": "El campo 'username' es obligatorio en el cuerpo de la petición."},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Validar si el usuario solicitado existe
        l=list(User.objects.all().filter(username=posted_username))
        if len(l)==0:
            return Response(
                {
                "messages": {"error_solicitud": f"No se encontró el usuario {posted_username}"},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            user_to_remove_sessions:User=l[0]
        
        if not header_token:
            return Response({
                "messages": {"error_solicitud": "Token de autorización no encontrado en el header."},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            # Decodificar el token
            token_key = str(header_token).split()[1].encode("utf-8")
        except IndexError:
            return Response({
                "messages": {"error_solicitud": "Formato de token de autorización incorrecto (debe ser 'Token <valor>')."},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        # ----------------------------------------------------
        # 2. Autenticación y Verificación de Usuario
        # ----------------------------------------------------
        
        knoxAuth = TokenAuthentication()
        
        try:
            # Intenta autenticar el token enviado
            user, auth_token = knoxAuth.authenticate_credentials(token_key)
            
        except AuthenticationFailed as e:
            # El token es inválido o expirado
            return Response({
                "messages": {
                    "detail": str(e.detail),
                    "error_solicitud": "El token de la sesión actual no es válido o está expirado."
                },
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        
        # Verificar que el usuario del token coincida con el usuario solicitado
        if user.username.lower() != posted_username.lower():
            men1="El token proporcionado no corresponde al usuario solicitado."
            if not user.groups.filter(name='admin').exists():
                men2="El usuario no pertenece a un grupo con permisos para cerrar las sesiones de otros."
                return Response({
                    "messages": {"error_solicitud": men1, "error_solicitud_2": men2},
                    "politica_acceso": {"acceso": "Acceso denegado."},
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN) # 403 FORBIDDEN es más apropiado aquí
            else:
                men2="El usuario dueño del token pertenece a un grupo con permisos para cerrar las sesiones de otros."
        else:
            men1="El token proporcionado corresponde al usuario solicitado."  
            if not user.groups.filter(name='admin').exists():
                men2="El usuario no pertenece a un grupo con permisos para cerrar las sesiones de otros."
            else:
                men2="El usuario pertenece a un grupo con permisos para cerrar las sesiones de otros."
        # ----------------------------------------------------
        # 3. Cierre de Sesiones (Lógica Principal)
        # ----------------------------------------------------
        
        # 1. Eliminar TODOS los tokens de ese usuario
        # Esto elimina todas las filas de knox_authtoken para el usuario autenticado


        os=knoxSessions.getOpenedKnoxSessions(user_to_remove_sessions.username)

        AuthToken.objects.filter(user=user_to_remove_sessions).delete() 

        # 2. Eliminar TODAS las sesiones de Django para este usuario (¡CORRECCIÓN!)
        # Esto busca todas las sesiones cuyo contenido serializado contiene el user_id
        # Nota: SessionDataSerializer es una clase interna de Django para este propósito
        all_sessions = Session.objects.all()
        
        for session in all_sessions:
            try:
                # Obtener el objeto de sesión (que contiene 'user_id' si el usuario se autenticó por sesión)
                session_data = session.get_decoded()
                
                # Comprobar si esta sesión pertenece al usuario actual
                if str(session_data.get('_auth_user_id')) == str(user_to_remove_sessions.pk):
                    session.delete()
            except:
                # Ignorar sesiones mal formadas
                continue

        # 3. Enviar la señal user_logged_out
        user_logged_out.send(
            sender=user_to_remove_sessions.__class__, 
            request=request, 
            user=user_to_remove_sessions 
        )

        # 4. Respuesta de éxito
        return Response({
            "messages": {
                "exito": f"Todas las sesiones ({os}) del usuario {posted_username} han sido cerradas con éxito.",
                "detalle_1": men1,
                "detalle_2": men2
            },
            "politica_acceso": {"acceso": "Acceso concedido."},
            "data": [{"username": posted_username, "closed_sessions": os}]
        }, status=status.HTTP_200_OK)


class LogoutAllUsersSessionsView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.EmptySerializer
    def post(self, request, format=None):
        """
        Cierra todas las sesiones (tokens) de todos los usuarios, incluida la sesión actual.
        Requiere el token actual en el header y debe pertener a un grupo con permisos especiales (admin),
                ["admin"],
        @param username: string en el body de la petición
        @return: Response
        """

        header_token = request.META.get('HTTP_AUTHORIZATION', False)
        if not header_token:
            return Response({
                "messages": {"error_solicitud": "Token de autorización no encontrado en el header."},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            # Decodificar el token
            token_key = str(header_token).split()[1].encode("utf-8")
        except IndexError:
            return Response({
                "messages": {"error_solicitud": "Formato de token de autorización incorrecto (debe ser 'Token <valor>')."},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        knoxAuth = TokenAuthentication()
        
        try:
            # Intenta autenticar el token enviado
            user, auth_token = knoxAuth.authenticate_credentials(token_key)
            
        except AuthenticationFailed as e:
            # El token es inválido o expirado
            return Response({
                "messages": {
                    "detail": str(e.detail),
                    "error_solicitud": "El token de la sesión actual no es válido o está expirado."
                },
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        
        # Verificar que el usuario del token coincida con el usuario solicitado

        if not user.groups.filter(name="admin").exists():
            men1="El usuario no pertenece al grupo admin."
            return Response({
                "messages": {"error_solicitud": men1},
                "politica_acceso": {"acceso": "Acceso denegado."},
                "data": None
            }, status=status.HTTP_403_FORBIDDEN) # 403 FORBIDDEN es más apropiado aquí
        os=AuthToken.objects.all().count()

        AuthToken.objects.all().delete() 

        # 2. Eliminar TODAS las sesiones de Django para este usuario (¡CORRECCIÓN!)
        # Esto busca todas las sesiones cuyo contenido serializado contiene el user_id
        # Nota: SessionDataSerializer es una clase interna de Django para este propósito
        all_sessions = Session.objects.all().delete()

        # 3. Enviar la señal user_logged_out
        user_logged_out.send(
            sender=user.__class__, 
            request=request, 
            user=user 
        )

        # 4. Respuesta de éxito
        return Response({
            "messages": {
                "exito": f"Todas las sesiones de todos los usuarios ({os}) han sido cerradas.",
                "detalle_1": "El usuario pertenece al grupo admin."
            },
            "politica_acceso": {"permitido": "Acceso concedido."},
            "data": [{"username": user.username, "closed_sessions": os}]
        }, status=status.HTTP_200_OK)
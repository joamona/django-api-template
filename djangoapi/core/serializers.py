
from rest_framework import serializers
from core.myLib import knoxSessions
from djangoapi.settings import REST_KNOX
from django.contrib.auth import authenticate

class LoginViewWithKnoxSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate_username(self,value):
        #validate_propiedad permite hacer validaciones adicionales sobre los campos
        #if len(value) > 10:
        #    raise serializers.ValidationError('Username mayor que 10')
        return value#hay que devolver un valor
    
    def validate(self, attrs): #se ejecuta con serializer.is_valid(raise_exception=True)
                    #e inicializa validated_data, con los datos validados, que es un dict
        username = attrs.get('username')

        os=knoxSessions.getOpenedKnoxSessions(username)
        if os>=REST_KNOX['TOKEN_LIMIT_PER_USER']:
            raise serializers.ValidationError({"error_solicitud":f"El número máximo de sesiones abiertas ({REST_KNOX['TOKEN_LIMIT_PER_USER']}) ha sido alcanzado. Cierre alguna sesión antes de iniciar una nueva."})
        
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'), username=username,
                            password=password)
        #print(user)
        if not user:
            #raise es lo que coloca los errores en serializer.errors
            #y hace que is_valid devuelva False
            #no se genera una execpción si se ha llamado a is_valid con exception=False
            raise serializers.ValidationError({"error_solicitud":"Usuario o contraseña erróneos."})

        attrs['user'] = user
        return attrs


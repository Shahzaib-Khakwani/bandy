from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import ValidationError



class CustomUserSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(required = True)
    user_name = serializers.CharField(required = True)
    password = serializers.CharField(min_length = 8, write_only=True)
    friends = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'user_name', 'password', 'first_name', 'last_name','image', 'gender', 'department', 'about','friends']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        email = validated_data.get('email', None)
        if email is not None:
            check = email.split('@')[1]
            if check != 'ISBSTUDENT.COMSATS.EDU.PK':
                raise ValidationError('Email must be from ISBSTUDENT.COMSATS.EDU.PK')
        else:
            raise ValidationError('Email Required')



        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)       
        instance.save()
        return instance
    

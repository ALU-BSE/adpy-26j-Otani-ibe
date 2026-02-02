from rest_framework import serializers
from .models import User
from .validators import validate_rwanda_nid, validate_rwanda_phone

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'nid_number', 'user_type']

    def create(self, validated_data):
        p_num = validated_data.get('phone_number')
        nid_num = validated_data.get('nid_number') 

        if validate_rwanda_phone(p_num) == False:
             raise serializers.ValidationError("That phone number looks wrong!")
        
        if nid_num and validate_rwanda_nid(nid_num) == False:
             raise serializers.ValidationError("That NID looks wrong!")

        u = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            nid_number=nid_num, 
            user_type=validated_data['user_type']
        )
        
        return u
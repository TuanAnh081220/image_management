from rest_framework import serializers


class MultiplIDsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )

from rest_framework import serializers
from items.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        # fields = ('id', 'song', 'singer', 'last_modify_date', 'created', 'days_since_created')

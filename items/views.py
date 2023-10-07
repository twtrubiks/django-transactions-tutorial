from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from items.serializers import ItemSerializer
from items.models import Item, create_items_with_transaction, create_items_no_transaction, \
    data_no_consistency, data_consistency


# Create your views here.
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    # [POST] /api/items/create_no_transaction/
    @action(detail=False, methods=['POST'], url_path='create_no_transaction')
    def create_no_transaction(self, request):
        count = request.data.get('count', None)
        result = create_items_no_transaction(count=count)
        if result == 200:
            result_status = status.HTTP_200_OK
        else:
            result_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result, status=result_status)

    # [POST] /api/items/create_with_transaction/
    @action(detail=False, methods=['POST'], url_path='create_with_transaction')
    def create_with_transaction(self, request):
        count = request.data.get('count', None)
        result = create_items_with_transaction(count=count)
        if result == 200:
            result_status = status.HTTP_200_OK
        else:
            result_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result, status=result_status)

    # [PUT] /api/items/no_consistency/
    @action(detail=False, methods=['PUT'], url_path='no_consistency')
    def no_consistency(self, request):
        result = data_no_consistency()
        return Response(result, status=status.HTTP_200_OK)

    # [PUT] /api/items/consistency/
    @action(detail=False, methods=['PUT'], url_path='consistency')
    def consistency(self, request):
        result = data_consistency()
        return Response(result, status=status.HTTP_200_OK)
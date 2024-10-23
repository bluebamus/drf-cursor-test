from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response

class CustomAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'

    def __init__(self, detail=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    if isinstance(exc, CustomAPIException):
        response = Response({
            "error": exc.detail,
            "status_code": exc.status_code
        }, status=exc.status_code)

    return response

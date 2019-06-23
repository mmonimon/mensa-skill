# coding: utf-8

#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#

import sys
import os
import re
import six
import typing

from ask_sdk_model.services.base_service_client import BaseServiceClient
from ask_sdk_model.services.api_configuration import ApiConfiguration
from ask_sdk_model.services.service_client_response import ServiceClientResponse


if typing.TYPE_CHECKING:
    from typing import Dict, List, Union, Any
    from datetime import datetime
    from ask_sdk_model.services.list_management.forbidden_error import ForbiddenError
    from ask_sdk_model.services.list_management.alexa_lists_metadata import AlexaListsMetadata
    from ask_sdk_model.services.list_management.alexa_list_item import AlexaListItem
    from ask_sdk_model.services.list_management.update_list_request import UpdateListRequest
    from ask_sdk_model.services.list_management.alexa_list_metadata import AlexaListMetadata
    from ask_sdk_model.services.list_management.alexa_list import AlexaList
    from ask_sdk_model.services.list_management.error import Error
    from ask_sdk_model.services.list_management.create_list_item_request import CreateListItemRequest
    from ask_sdk_model.services.list_management.update_list_item_request import UpdateListItemRequest
    from ask_sdk_model.services.list_management.create_list_request import CreateListRequest


class ListManagementServiceClient(BaseServiceClient):
    """ServiceClient for calling the ListManagementService APIs.

    :param api_configuration: Instance of :py:class:`ask_sdk_model.services.api_configuration.ApiConfiguration`
    :type api_configuration: ask_sdk_model.services.api_configuration.ApiConfiguration
    """
    def __init__(self, api_configuration):
        # type: (ApiConfiguration) -> None
        """
        :param api_configuration: Instance of :py:class:`ask_sdk_model.services.api_configuration.ApiConfiguration`
        :type api_configuration: ask_sdk_model.services.api_configuration.ApiConfiguration
        """
        super(ListManagementServiceClient, self).__init__(api_configuration)

    def get_lists_metadata(self, **kwargs):
        # type: (**Any) -> Union[ForbiddenError, Error, AlexaListsMetadata]
        """
        Retrieves the metadata for all customer lists, including the customer’s default lists. 

        :rtype: Union[ForbiddenError, Error, AlexaListsMetadata]
        """
        operation_name = "get_lists_metadata"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']

        resource_path = '/v2/householdlists/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_lists_metadata.AlexaListsMetadata", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.forbidden_error.ForbiddenError", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))

        return self.invoke(
            method="GET",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_lists_metadata.AlexaListsMetadata")

    def delete_list(self, list_id, **kwargs):
        # type: (str, **Any) -> Union[Error]
        """
        This API deletes a customer custom list.

        :param list_id: (required) Value of the customer’s listId retrieved from a getListsMetadata call
        :type list_id: str
        :rtype: None
        """
        operation_name = "delete_list"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="Not Found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        self.invoke(
            method="DELETE",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type=None)

    def delete_list_item(self, list_id, item_id, **kwargs):
        # type: (str, str, **Any) -> Union[Error]
        """
        This API deletes an item in the specified list.

        :param list_id: (required) The customer’s listId is retrieved from a getListsMetadata call.
        :type list_id: str
        :param item_id: (required) The customer’s itemId is retrieved from a GetList call.
        :type item_id: str
        :rtype: None
        """
        operation_name = "delete_list_item"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")
        # verify the required parameter 'item_id' is set
        if ('item_id' not in params) or (params['item_id'] is None):
            raise ValueError(
                "Missing the required parameter `item_id` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/items/{itemId}/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']
        if 'item_id' in params:
            path_params['itemId'] = params['item_id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="Not Found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        self.invoke(
            method="DELETE",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type=None)

    def get_list_item(self, list_id, item_id, **kwargs):
        # type: (str, str, **Any) -> Union[AlexaListItem, Error]
        """
        This API can be used to retrieve single item with in any list by listId and itemId. This API can read list items from an archived list. Attempting to read list items from a deleted list return an ObjectNotFound 404 error. 

        :param list_id: (required) Retrieved from a call to getListsMetadata
        :type list_id: str
        :param item_id: (required) itemId within a list is retrieved from a getList call
        :type item_id: str
        :rtype: Union[AlexaListItem, Error]
        """
        operation_name = "get_list_item"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")
        # verify the required parameter 'item_id' is set
        if ('item_id' not in params) or (params['item_id'] is None):
            raise ValueError(
                "Missing the required parameter `item_id` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/items/{itemId}/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']
        if 'item_id' in params:
            path_params['itemId'] = params['item_id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_list_item.AlexaListItem", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="Not Found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        return self.invoke(
            method="GET",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_list_item.AlexaListItem")

    def update_list_item(self, list_id, item_id, update_list_item_request, **kwargs):
        # type: (str, str, UpdateListItemRequest, **Any) -> Union[AlexaListItem, Error]
        """
        API used to update an item value or item status.

        :param list_id: (required) Customer’s listId
        :type list_id: str
        :param item_id: (required) itemId to be updated in the list
        :type item_id: str
        :param update_list_item_request: (required) 
        :type update_list_item_request: ask_sdk_model.services.list_management.update_list_item_request.UpdateListItemRequest
        :rtype: Union[AlexaListItem, Error]
        """
        operation_name = "update_list_item"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")
        # verify the required parameter 'item_id' is set
        if ('item_id' not in params) or (params['item_id'] is None):
            raise ValueError(
                "Missing the required parameter `item_id` when calling `" + operation_name + "`")
        # verify the required parameter 'update_list_item_request' is set
        if ('update_list_item_request' not in params) or (params['update_list_item_request'] is None):
            raise ValueError(
                "Missing the required parameter `update_list_item_request` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/items/{itemId}/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']
        if 'item_id' in params:
            path_params['itemId'] = params['item_id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        if 'update_list_item_request' in params:
            body_params = params['update_list_item_request']
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_list_item.AlexaListItem", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="Not Found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=409, message="Conflict"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        return self.invoke(
            method="PUT",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_list_item.AlexaListItem")

    def create_list_item(self, list_id, create_list_item_request, **kwargs):
        # type: (str, CreateListItemRequest, **Any) -> Union[AlexaListItem, Error]
        """
        This API creates an item in an active list or in a default list.

        :param list_id: (required) The customer’s listId retrieved from a getListsMetadata call.
        :type list_id: str
        :param create_list_item_request: (required) 
        :type create_list_item_request: ask_sdk_model.services.list_management.create_list_item_request.CreateListItemRequest
        :rtype: Union[AlexaListItem, Error]
        """
        operation_name = "create_list_item"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")
        # verify the required parameter 'create_list_item_request' is set
        if ('create_list_item_request' not in params) or (params['create_list_item_request'] is None):
            raise ValueError(
                "Missing the required parameter `create_list_item_request` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/items/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        if 'create_list_item_request' in params:
            body_params = params['create_list_item_request']
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_list_item.AlexaListItem", status_code=201, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="Not found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        return self.invoke(
            method="POST",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_list_item.AlexaListItem")

    def update_list(self, list_id, update_list_request, **kwargs):
        # type: (str, UpdateListRequest, **Any) -> Union[Error, AlexaListMetadata]
        """
        This API updates a custom list. Only the list name or state can be updated. An Alexa customer can turn an archived list into an active one. 

        :param list_id: (required) Value of the customer’s listId retrieved from a getListsMetadata call. 
        :type list_id: str
        :param update_list_request: (required) 
        :type update_list_request: ask_sdk_model.services.list_management.update_list_request.UpdateListRequest
        :rtype: Union[Error, AlexaListMetadata]
        """
        operation_name = "update_list"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")
        # verify the required parameter 'update_list_request' is set
        if ('update_list_request' not in params) or (params['update_list_request'] is None):
            raise ValueError(
                "Missing the required parameter `update_list_request` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        if 'update_list_request' in params:
            body_params = params['update_list_request']
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_list_metadata.AlexaListMetadata", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="List not found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=409, message="Conflict"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        return self.invoke(
            method="PUT",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_list_metadata.AlexaListMetadata")

    def get_list(self, list_id, status, **kwargs):
        # type: (str, str, **Any) -> Union[AlexaList, Error]
        """
        Retrieves the list metadata including the items in the list with requested status. 

        :param list_id: (required) Retrieved from a call to GetListsMetadata to specify the listId in the request path. 
        :type list_id: str
        :param status: (required) Specify the status of the list. 
        :type status: str
        :rtype: Union[AlexaList, Error]
        """
        operation_name = "get_list"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'list_id' is set
        if ('list_id' not in params) or (params['list_id'] is None):
            raise ValueError(
                "Missing the required parameter `list_id` when calling `" + operation_name + "`")
        # verify the required parameter 'status' is set
        if ('status' not in params) or (params['status'] is None):
            raise ValueError(
                "Missing the required parameter `status` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/{listId}/{status}/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'list_id' in params:
            path_params['listId'] = params['list_id']
        if 'status' in params:
            path_params['status'] = params['status']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_list.AlexaList", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=404, message="Not Found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        return self.invoke(
            method="GET",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_list.AlexaList")

    def create_list(self, create_list_request, **kwargs):
        # type: (CreateListRequest, **Any) -> Union[Error, AlexaListMetadata]
        """
        This API creates a custom list. The new list name must be different than any existing list name. 

        :param create_list_request: (required) 
        :type create_list_request: ask_sdk_model.services.list_management.create_list_request.CreateListRequest
        :rtype: Union[Error, AlexaListMetadata]
        """
        operation_name = "create_list"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'create_list_request' is set
        if ('create_list_request' not in params) or (params['create_list_request'] is None):
            raise ValueError(
                "Missing the required parameter `create_list_request` when calling `" + operation_name + "`")

        resource_path = '/v2/householdlists/'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        if 'create_list_request' in params:
            body_params = params['create_list_request']
        header_params.append(('Content-type', 'application/json'))

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.alexa_list_metadata.AlexaListMetadata", status_code=201, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=409, message="Conflict"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.list_management.error.Error", status_code=0, message="Internal Server Error"))

        return self.invoke(
            method="POST",
            endpoint="https://api.amazonalexa.com/",
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.list_management.alexa_list_metadata.AlexaListMetadata")

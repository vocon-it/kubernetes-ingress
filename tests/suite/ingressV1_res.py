"""Describe methods to utilize the kubernetes-client."""
import re
import os
import time
import yaml
import json
import pytest
import requests
import six

from kubernetes.client.rest import ApiException
from kubernetes.client.api_client import ApiClient
from kubernetes.client.exceptions import ( 
    ApiTypeError,
    ApiValueError
)
from kubernetes.stream import stream
from kubernetes import client
from more_itertools import first

from settings import TEST_DATA, RECONFIGURATION_DELAY, DEPLOYMENTS, PROJECT_ROOT

def create_ingress_v1(namespace, body, **kwargs) -> str:
    """
    Create an ingress based on a dict.

    :param extensions_v1_beta1: ExtensionsV1Api
    :param namespace: namespace name
    :param body: a dict
    :return: str
    """
    api_client = ApiClient()
    print("Create an ingress:")
    local_var_params = locals()

    all_params = [
        'namespace',
        'body',
        'pretty',
        'dry_run',
        'field_manager'
    ]
    all_params.extend(
        [
            'async_req',
            '_return_http_data_only',
            '_preload_content',
            '_request_timeout'
        ]
    )

    for key, val in six.iteritems(local_var_params['kwargs']):
        if key not in all_params:
            raise ApiTypeError(
                "Got an unexpected keyword argument '%s'"
                " to method create_namespaced_ingress" % key
            )
        local_var_params[key] = val
    del local_var_params['kwargs']
    # verify the required parameter 'namespace' is set
    if api_client.client_side_validation and ('namespace' not in local_var_params or  # noqa: E501
                                                    local_var_params['namespace'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `namespace` when calling `create_namespaced_ingress`")  # noqa: E501
    # verify the required parameter 'body' is set
    if api_client.client_side_validation and ('body' not in local_var_params or  # noqa: E501
                                                    local_var_params['body'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `body` when calling `create_namespaced_ingress`")  # noqa: E501

    collection_formats = {}

    path_params = {}
    if 'namespace' in local_var_params:
        path_params['namespace'] = local_var_params['namespace']  # noqa: E501

    query_params = []
    if 'pretty' in local_var_params and local_var_params['pretty'] is not None:  # noqa: E501
        query_params.append(('pretty', local_var_params['pretty']))  # noqa: E501
    if 'dry_run' in local_var_params and local_var_params['dry_run'] is not None:  # noqa: E501
        query_params.append(('dryRun', local_var_params['dry_run']))  # noqa: E501
    if 'field_manager' in local_var_params and local_var_params['field_manager'] is not None:  # noqa: E501
        query_params.append(('fieldManager', local_var_params['field_manager']))  # noqa: E501

    header_params = {}

    form_params = []
    local_var_files = {}

    body_params = None
    if 'body' in local_var_params:
        body_params = local_var_params['body']
    # HTTP header `Accept`
    header_params['Accept'] = api_client.select_header_accept(
        ['application/json', 'application/yaml', 'application/vnd.kubernetes.protobuf'])  # noqa: E501

    # Authentication setting
    auth_settings = ['BearerToken']  # noqa: E501

    resp = api_client.call_api(
        f"/apis/networking.k8s.io/v1/namespaces/{namespace}/ingresses", 'POST',
        path_params,
        query_params,
        header_params,
        body=body_params,
        post_params=form_params,
        files=local_var_files,
        response_type='NetworkingV1Ingress',  # noqa: E501
        auth_settings=auth_settings,
        async_req=local_var_params.get('async_req'),
        _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
        _preload_content=local_var_params.get('_preload_content', True),
        _request_timeout=local_var_params.get('_request_timeout'),
        collection_formats=collection_formats)

    return resp


def delete_ingress_v1(name, namespace, **kwargs) -> None:
    """
    Delete an ingress.

    :param extensions_v1_beta1: ExtensionsV1Api
    :param namespace: namespace
    :param name:
    :return:
    """
    api_client = ApiClient()
    print(f"Delete an ingress: {name}")
    local_var_params = locals()

    all_params = [
        'name',
        'namespace',
        'pretty',
        'dry_run',
        'grace_period_seconds',
        'orphan_dependents',
        'propagation_policy',
        'body'
    ]
    all_params.extend(
        [
            'async_req',
            '_return_http_data_only',
            '_preload_content',
            '_request_timeout'
        ]
    )

    for key, val in six.iteritems(local_var_params['kwargs']):
        if key not in all_params:
            raise ApiTypeError(
                "Got an unexpected keyword argument '%s'"
                " to method delete_namespaced_ingress" % key
            )
        local_var_params[key] = val
    del local_var_params['kwargs']
    # verify the required parameter 'name' is set
    if api_client.client_side_validation and ('name' not in local_var_params or  # noqa: E501
                                                    local_var_params['name'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `name` when calling `delete_namespaced_ingress`")  # noqa: E501
    # verify the required parameter 'namespace' is set
    if api_client.client_side_validation and ('namespace' not in local_var_params or  # noqa: E501
                                                    local_var_params['namespace'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `namespace` when calling `delete_namespaced_ingress`")  # noqa: E501

    collection_formats = {}

    path_params = {}
    if 'name' in local_var_params:
        path_params['name'] = local_var_params['name']  # noqa: E501
    if 'namespace' in local_var_params:
        path_params['namespace'] = local_var_params['namespace']  # noqa: E501

    query_params = []
    if 'pretty' in local_var_params and local_var_params['pretty'] is not None:  # noqa: E501
        query_params.append(('pretty', local_var_params['pretty']))  # noqa: E501
    if 'dry_run' in local_var_params and local_var_params['dry_run'] is not None:  # noqa: E501
        query_params.append(('dryRun', local_var_params['dry_run']))  # noqa: E501
    if 'grace_period_seconds' in local_var_params and local_var_params['grace_period_seconds'] is not None:  # noqa: E501
        query_params.append(('gracePeriodSeconds', local_var_params['grace_period_seconds']))  # noqa: E501
    if 'orphan_dependents' in local_var_params and local_var_params['orphan_dependents'] is not None:  # noqa: E501
        query_params.append(('orphanDependents', local_var_params['orphan_dependents']))  # noqa: E501
    if 'propagation_policy' in local_var_params and local_var_params['propagation_policy'] is not None:  # noqa: E501
        query_params.append(('propagationPolicy', local_var_params['propagation_policy']))  # noqa: E501

    header_params = {}

    form_params = []
    local_var_files = {}

    body_params = None
    if 'body' in local_var_params:
        body_params = local_var_params['body']
    # HTTP header `Accept`
    header_params['Accept'] = api_client.select_header_accept(
        ['application/json', 'application/yaml', 'application/vnd.kubernetes.protobuf'])  # noqa: E501

    # Authentication setting
    auth_settings = ['BearerToken']  # noqa: E501

    body = api_client.call_api(
        f"/apis/networking.k8s.io/v1/namespaces/{namespace}/ingresses/{name}", 'DELETE',
        path_params,
        query_params,
        header_params,
        body=body_params,
        post_params=form_params,
        files=local_var_files,
        response_type='V1Status',  # noqa: E501
        auth_settings=auth_settings,
        async_req=local_var_params.get('async_req'),
        _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
        _preload_content=local_var_params.get('_preload_content', True),
        _request_timeout=local_var_params.get('_request_timeout'),
        collection_formats=collection_formats)


    print(f"Ingress was removed with name '{name}'")

def replace_ingress_v1(name, namespace, body, **kwargs) -> str:
    """
    Replace an Ingress based on a dict.

    :param extensions_v1_beta1: ExtensionsV1Api
    :param name:
    :param namespace: namespace
    :param body: dict
    :return: str
    """
    api_client = ApiClient()
    print(f"Replace a Ingress: {name}")
    
    local_var_params = locals()

    all_params = [
        'name',
        'namespace',
        'body',
        'pretty',
        'dry_run',
        'field_manager'
    ]
    all_params.extend(
        [
            'async_req',
            '_return_http_data_only',
            '_preload_content',
            '_request_timeout'
        ]
    )

    for key, val in six.iteritems(local_var_params['kwargs']):
        if key not in all_params:
            raise ApiTypeError(
                "Got an unexpected keyword argument '%s'"
                " to method replace_namespaced_ingress" % key
            )
        local_var_params[key] = val
    del local_var_params['kwargs']
    # verify the required parameter 'name' is set
    if api_client.client_side_validation and ('name' not in local_var_params or  # noqa: E501
                                                    local_var_params['name'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `name` when calling `replace_namespaced_ingress`")  # noqa: E501
    # verify the required parameter 'namespace' is set
    if api_client.client_side_validation and ('namespace' not in local_var_params or  # noqa: E501
                                                    local_var_params['namespace'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `namespace` when calling `replace_namespaced_ingress`")  # noqa: E501
    # verify the required parameter 'body' is set
    if api_client.client_side_validation and ('body' not in local_var_params or  # noqa: E501
                                                    local_var_params['body'] is None):  # noqa: E501
        raise ApiValueError("Missing the required parameter `body` when calling `replace_namespaced_ingress`")  # noqa: E501

    collection_formats = {}

    path_params = {}
    if 'name' in local_var_params:
        path_params['name'] = local_var_params['name']  # noqa: E501
    if 'namespace' in local_var_params:
        path_params['namespace'] = local_var_params['namespace']  # noqa: E501

    query_params = []
    if 'pretty' in local_var_params and local_var_params['pretty'] is not None:  # noqa: E501
        query_params.append(('pretty', local_var_params['pretty']))  # noqa: E501
    if 'dry_run' in local_var_params and local_var_params['dry_run'] is not None:  # noqa: E501
        query_params.append(('dryRun', local_var_params['dry_run']))  # noqa: E501
    if 'field_manager' in local_var_params and local_var_params['field_manager'] is not None:  # noqa: E501
        query_params.append(('fieldManager', local_var_params['field_manager']))  # noqa: E501

    header_params = {}

    form_params = []
    local_var_files = {}

    body_params = None
    if 'body' in local_var_params:
        body_params = local_var_params['body']
    # HTTP header `Accept`
    header_params['Accept'] = api_client.select_header_accept(
        ['application/json', 'application/yaml', 'application/vnd.kubernetes.protobuf'])  # noqa: E501

    # Authentication setting
    auth_settings = ['BearerToken']  # noqa: E501

    resp = api_client.call_api(
        '/apis/networking.k8s.io/v1/namespaces/{namespace}/ingresses/{name}', 'PUT',
        path_params,
        query_params,
        header_params,
        body=body_params,
        post_params=form_params,
        files=local_var_files,
        response_type='NetworkingV1Ingress',  # noqa: E501
        auth_settings=auth_settings,
        async_req=local_var_params.get('async_req'),
        _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
        _preload_content=local_var_params.get('_preload_content', True),
        _request_timeout=local_var_params.get('_request_timeout'),
        collection_formats=collection_formats)
    print(f"Ingress replaced with name '{name}'")
    return resp

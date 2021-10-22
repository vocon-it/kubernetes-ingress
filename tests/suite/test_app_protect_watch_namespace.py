import requests
import random
import string
import pytest, json
import time

from settings import TEST_DATA, DEPLOYMENTS
from suite.ap_resources_utils import (
    create_ap_logconf_from_yaml,
    create_ap_policy_from_yaml,
    delete_ap_policy,
    delete_ap_logconf,
)
from suite.resources_utils import (
    wait_before_test,
    create_example_app,
    wait_until_all_pods_are_ready,
    create_items_from_yaml,
    delete_items_from_yaml,
    delete_common_app,
    delete_namespace,
    ensure_connection_to_public_endpoint,
    create_ingress_with_ap_annotations,
    create_namespace_with_name_from_yaml,
    ensure_response_from_backend,
    wait_before_test,
    get_last_reload_time,
    get_test_file_name,
    write_to_json,
)
from suite.yaml_utils import get_first_ingress_host_from_yaml

timestamp = round(time.time() * 1000)
test_namespace = f"test-namespace-{str(timestamp)}"
policy_namespace = f"policy-test-namespace-{str(timestamp)}"
valid_resp_body = "Server name:"
invalid_resp_body = "The requested URL was rejected. Please consult with your administrator."
reload_times = {}


class BackendSetup:
    """
    Encapsulate the example details.

    Attributes:
        req_url (str):
        ingress_host (str):
    """

    def __init__(self, req_url, req_url_2, metrics_url, ingress_host):
        self.req_url = req_url
        self.req_url_2 = req_url_2
        self.metrics_url = metrics_url
        self.ingress_host = ingress_host


@pytest.fixture(scope="class")
def backend_setup(request, kube_apis, ingress_controller_endpoint) -> BackendSetup:
    """
    Deploy a simple application and AppProtect manifests.

    :param request: pytest fixture
    :param kube_apis: client apis
    :param ingress_controller_endpoint: public endpoint
    :param test_namespace:
    :return: BackendSetup
    """
    policy = "dataguard-alarm-transparent"
    
    create_namespace_with_name_from_yaml(kube_apis.v1, test_namespace, f"{TEST_DATA}/common/ns.yaml")
    print("------------------------- Deploy backend application -------------------------")
    
    create_example_app(kube_apis, "simple", test_namespace)
    req_url = f"https://{ingress_controller_endpoint.public_ip}:{ingress_controller_endpoint.port_ssl}/backend1"
    req_url_2 = f"https://{ingress_controller_endpoint.public_ip}:{ingress_controller_endpoint.port_ssl}/backend2"
    metrics_url = f"http://{ingress_controller_endpoint.public_ip}:{ingress_controller_endpoint.metrics_port}/metrics"
    wait_until_all_pods_are_ready(kube_apis.v1, test_namespace)
    ensure_connection_to_public_endpoint(
        ingress_controller_endpoint.public_ip,
        ingress_controller_endpoint.port,
        ingress_controller_endpoint.port_ssl,
    )

    print("------------------------- Deploy Secret -----------------------------")
    src_sec_yaml = f"{TEST_DATA}/appprotect/appprotect-secret.yaml"
    create_items_from_yaml(kube_apis, src_sec_yaml, test_namespace)

    print("------------------------- Deploy logconf -----------------------------")
    src_log_yaml = f"{TEST_DATA}/appprotect/logconf.yaml"
    log_name = create_ap_logconf_from_yaml(kube_apis.custom_objects, src_log_yaml, test_namespace)

    print(f"------------------------- Deploy namespace: {policy_namespace} ---------------------------")
    create_namespace_with_name_from_yaml(kube_apis.v1, policy_namespace, f"{TEST_DATA}/common/ns.yaml")

    print(f"------------------------- Deploy appolicy: {policy} ---------------------------")
    src_pol_yaml = f"{TEST_DATA}/appprotect/{policy}.yaml"
    pol_name = create_ap_policy_from_yaml(kube_apis.custom_objects, src_pol_yaml, policy_namespace)

    print("------------------------- Deploy ingress -----------------------------")
    ingress_host = {}
    src_ing_yaml = f"{TEST_DATA}/appprotect/appprotect-ingress.yaml"
    create_ingress_with_ap_annotations(
        kube_apis, src_ing_yaml, test_namespace, f"{policy_namespace}/{policy}", "True", "True", "127.0.0.1:514"
    )
    ingress_host = get_first_ingress_host_from_yaml(src_ing_yaml)
    wait_before_test()

    def fin():
        print("Clean up:")
        src_ing_yaml = f"{TEST_DATA}/appprotect/appprotect-ingress.yaml"
        delete_items_from_yaml(kube_apis, src_ing_yaml, test_namespace)
        delete_ap_policy(kube_apis.custom_objects, pol_name, policy_namespace)
        delete_namespace(kube_apis.v1, policy_namespace)
        delete_ap_logconf(kube_apis.custom_objects, log_name, test_namespace)
        delete_common_app(kube_apis, "simple", test_namespace)
        src_sec_yaml = f"{TEST_DATA}/appprotect/appprotect-secret.yaml"
        delete_items_from_yaml(kube_apis, src_sec_yaml, test_namespace)
        delete_namespace(kube_apis.v1, test_namespace)

    request.addfinalizer(fin)

    return BackendSetup(req_url, req_url_2, metrics_url, ingress_host)

@pytest.mark.skip_for_nginx_oss
@pytest.mark.appprotectwatch
@pytest.mark.smoke
@pytest.mark.parametrize(
    "crd_ingress_controller_with_ap",
    [
       {
            "extra_args": [
                f"-enable-custom-resources",
                f"-enable-app-protect",
                f"-enable-prometheus-metrics"
            ]
        }
    ],
    indirect=True,
)
class TestAppProtectWatchNamespaceDisabled:
    def test_responses(
        self, request, kube_apis, crd_ingress_controller_with_ap, backend_setup
    ):
        """
        Test dataguard-alarm AppProtect policy: Block malicious script in url
        """
        print("------------- Run test for AP policy: dataguard-alarm --------------")
        print(f"Request URL: {backend_setup.req_url} and Host: {backend_setup.ingress_host}")

        ensure_response_from_backend(
            backend_setup.req_url, backend_setup.ingress_host, check404=True
        )

        print("----------------------- Send request ----------------------")
        resp = requests.get(
            f"{backend_setup.req_url}/<script>", headers={"host": backend_setup.ingress_host}, verify=False
        )
        
        print(resp.text)

        assert valid_resp_body in resp.text
        assert resp.status_code == 200

@pytest.mark.skip_for_nginx_oss
@pytest.mark.appprotectwatch
@pytest.mark.smoke
@pytest.mark.parametrize(
    "crd_ingress_controller_with_ap",
    [
       {
            "extra_args": [
                f"-enable-custom-resources",
                f"-enable-app-protect",
                f"-enable-prometheus-metrics",
                f"-watch-namespace={test_namespace}"
            ]
        }
    ],
    indirect=True,
)
class TestAppProtectWatchNamespaceEnabled:
    def test_responses(
        self, request, kube_apis, crd_ingress_controller_with_ap, backend_setup, test_namespace
    ):
        """
        Test dataguard-alarm AppProtect policy: Block malicious script in url
        """
        print("------------- Run test for AP policy: dataguard-alarm --------------")
        print(f"Request URL: {backend_setup.req_url} and Host: {backend_setup.ingress_host}")

        ensure_response_from_backend(
            backend_setup.req_url, backend_setup.ingress_host, check404=True
        )

        print("----------------------- Send request ----------------------")
        resp = requests.get(
            f"{backend_setup.req_url}/<script>", headers={"host": backend_setup.ingress_host}, verify=False
        )
        
        print(resp.text)

        assert invalid_resp_body in resp.text
        assert resp.status_code == 200
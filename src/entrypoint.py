#!/usr/bin/python3
"""
Provides a script to synchronize ConfigMaps from a directory to a Kubernetes cluster.
"""
import base64
import logging
import os
import sys
from os import path
import kubernetes

# Globals declaration
CONTEXT = {}
LOGGER = None


def init():
    """ Initializes the script: logger, context variables, ... """
    global CONTEXT  # pylint: disable=global-statement
    global LOGGER  # pylint: disable=global-statement

    if LOGGER is None:
        LOGGER = logging.getLogger()
        logger_formatter = logging.Formatter("%(asctime)s: [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        logger_handler = logging.StreamHandler()
        logger_handler.setFormatter(logger_formatter)
        LOGGER.addHandler(logger_handler)
        LOGGER.setLevel(logging.DEBUG if os.environ.get("DEBUG") is not None else logging.INFO)

    # Files found.
    if len(sys.argv) != 2:
        LOGGER.error("ConfigMap directory must be defined")
        print_help()
        sys.exit(1)

    # Config directory.
    CONTEXT['configmap_directory'] = sys.argv[1]

    # Trace debug.
    debug()

    # Kube configuration
    if path.exists('/var/run/secrets/kubernetes.io'):
        LOGGER.info('Running within a pod.')
        kubernetes.config.load_incluster_config()
    else:
        LOGGER.info('Running outside a pod, using .kubeconfig.')
        kubernetes.config.load_kube_config()


def print_help():
    """ Prints the help to use the script. """
    LOGGER.info('The script should be run with the following parameters:')
    LOGGER.info('python3 entrypoint.py <configmap_directory>')
    LOGGER.info('- configmap_directory: the root directory where config map data are stored.')


def debug():
    """ Prints a debug trace the help to debug the script. """
    LOGGER.debug("CONTEXT['configmap_directory'] = %s", (CONTEXT['configmap_directory'] if CONTEXT['configmap_directory'] is not None else 'None'))


def extract_configmaps_from_directory():
    """ Extracts the ConfigMap to synchronize from the given directory. """

    # Check if directory exists.
    if not os.path.isdir(CONTEXT['configmap_directory']):
        LOGGER.error('The specified ConfigMap directory is not a directory.')
        sys.exit(1)

    # Trace base directory.
    LOGGER.info('= ConfigMap directory is: <%s>', CONTEXT['configmap_directory'])

    # Proceed to configmap extraction.
    LOGGER.info('= Proceed to ConfigMap extraction.')

    # Listing the namespaces.
    configmaps_by_namespace = {}
    for k8s_namespace in os.listdir(CONTEXT['configmap_directory']):
        k8s_namespace_path = os.path.join(CONTEXT['configmap_directory'], k8s_namespace)
        if os.path.isdir(k8s_namespace_path):
            # We are in namespace folder.
            LOGGER.info('== Namespace: <%s>', k8s_namespace)

            # K8S namespace.
            if k8s_namespace not in configmaps_by_namespace:
                configmaps_by_namespace[k8s_namespace] = {}

            for configmap_name in os.listdir(k8s_namespace_path):
                configmap_name_path = os.path.join(k8s_namespace_path, configmap_name)
                if os.path.isdir(configmap_name_path):
                    configmap_data = extract_configmap_data_from_directory(configmap_name, configmap_name_path)
                    configmaps_by_namespace[k8s_namespace][configmap_name] = configmap_data

    # Proceed to configmap extraction.
    LOGGER.info('= ConfigMap extraction completed successfully.')

    # Returns configmaps.
    return configmaps_by_namespace


def extract_configmap_data_from_directory(configmap_name, configmap_name_path):
    """ Extracts the ConfigMap data from the given directory. """

    LOGGER.info('== > ConfigMap: <%s>', configmap_name)
    configmap = {
        'name': configmap_name,
        'data': {},
        'binaryData': {}
    }

    for data_file_name in os.listdir(configmap_name_path):
        data_file_path = os.path.join(configmap_name_path, data_file_name)
        if os.path.isfile(data_file_path):
            LOGGER.info('== >>> Adding file: <%s>.', data_file_name)
            with open(data_file_path, 'rb') as data_file:
                base64_content = base64.b64encode(data_file.read()).decode('utf8')
                configmap['binaryData'][data_file_name] = base64_content

    # Returns configmaps.
    return configmap


def synchronize_configmaps_in_cluster(configmaps_by_namespace):
    """ Update the K8S cluster and synchronize the ConfigMaps within the cluster. """

    # Proceed to configmap synchronization in cluster.
    LOGGER.info('= Proceed to ConfigMap extraction in cluster.')

    # ConfigMap are in Core V1 API.
    core_v1 = kubernetes.client.CoreV1Api()

    for k8s_namespace, configmaps_by_name in configmaps_by_namespace.items():
        LOGGER.info('== Namespace: <%s>', k8s_namespace)

        # Get list of configmaps existing in cluster.
        LOGGER.info('=== Fetching list of ConfigMap in the cluster')
        search_result = core_v1.list_namespaced_config_map(namespace=k8s_namespace)
        existing_configmap_names = []
        for i in search_result.items:
            existing_configmap_names.append(i.metadata.name)

        # Synchronize the list
        LOGGER.info('=== Synchronize ConfigMaps in the cluster')
        for configmap_name, configmap in configmaps_by_name.items():
            # Build body.
            body = kubernetes.client.V1ConfigMap(
                api_version='v1',
                kind='ConfigMap',
                metadata=kubernetes.client.V1ObjectMeta(
                    name=configmap_name,
                    namespace=k8s_namespace,
                    labels={
                        'app.kubernetes.io/managed-by': 'io.julb.kubernetes-configmap-sync'
                    }
                ),
                data=configmap['data'],
                binary_data=configmap['binaryData']
            )

            if configmap_name not in existing_configmap_names:
                LOGGER.info('==== Create ConfigMap: %s.', configmap_name)
                core_v1.create_namespaced_config_map(namespace=k8s_namespace, body=body)
            else:
                LOGGER.info('==== Update ConfigMap: %s.', configmap_name)
                core_v1.replace_namespaced_config_map(namespace=k8s_namespace, name=configmap_name, body=body)

        # Delete the configmaps no more present.
        LOGGER.info('=== Delete ConfigMaps no more present in the cluster')
        search_result = core_v1.list_namespaced_config_map(
            namespace=k8s_namespace, label_selector='app.kubernetes.io/managed-by=io.julb.kubernetes-configmap-sync')
        for i in search_result.items:
            if i.metadata.name not in configmaps_by_name:
                LOGGER.info('==== Delete ConfigMap: %s.', i.metadata.name)
                core_v1.delete_namespaced_config_map(name=i.metadata.name, namespace=k8s_namespace)


if __name__ == '__main__':
    init()

    LOGGER.info('Operation started.')

    # Synchronize in cluster.
    synchronize_configmaps_in_cluster(extract_configmaps_from_directory())

    LOGGER.info('Operation completed.')

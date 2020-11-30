![PyPI](https://img.shields.io/pypi/v/kubernetes-configmap-sync)
![PyPI - License](https://img.shields.io/pypi/l/kubernetes-configmap-sync)
![PyPI - Downloads](https://img.shields.io/pypi/dm/kubernetes-configmap-sync)
[![docker-image-version](https://img.shields.io/docker/v/julb/kubernetes-configmap-sync.svg?sort=semver)](https://hub.docker.com/r/julb/kubernetes-configmap-sync)
[![docker-image-size](https://img.shields.io/docker/image-size/julb/kubernetes-configmap-sync.svg?sort=semver)](https://hub.docker.com/r/julb/kubernetes-configmap-sync)
[![docker-pulls](https://img.shields.io/docker/pulls/julb/kubernetes-configmap-sync.svg)](https://hub.docker.com/r/julb/kubernetes-configmap-sync)

# julb/kubernetes-configmap-sync

## Description

This utility takes a source directory and creates automatically ConfigMap in the Kubernetes cluster based on the content of that directory.

This can be used when :

- Configuration files for your application are stored in Git, or anything source directory.
- A regular routine will launch the container to synchronize the content of the source directory into the Kubernetes cluster.

## Use the script

The directory used as source for ConfigMap creation should be organized like this:

```
-- ROOT/
-- -- namespace1/
-- -- -- configmap-name1/
-- -- -- -- file1.txt
-- -- -- -- file2.txt

-- -- -- configmap-name2/
-- -- -- -- [....]

-- -- namespace2/
-- -- -- [....]

-- -- namespace3/
-- -- -- [....]
```

### Using the python module

```
$ pip install kubernetes-configmap-sync
$ python -m kubernetes-configmap-sync <directory>
```

### Using the container

To execute the container, you should have a ~/.kube/config with the context pointing to the cluster.
The user defined in the context should have the appropriate rights in th cluster to manage configmaps.

```
$ docker run -ti \
    --user 65534:65534                      \
    -e "CONFIGMAP_DIR=/opt/configmap-dir"   \
    -v $(pwd)/examples:/opt/configmap-dir   \
    -e "KUBECONFIG=/.kube/config"           \
    -v ~/.kube/config:/.kube/config         \
    julb/kubernetes-configmap-sync:latest

2020-06-08 09:08:06: [INFO] Running outside a pod, using .kubeconfig.
2020-06-08 09:08:06: [INFO] Operation started.
2020-06-08 09:08:06: [INFO] = ConfigMap directory is: <examples>
2020-06-08 09:08:06: [INFO] = Proceed to ConfigMap extraction.
2020-06-08 09:08:06: [INFO] == Namespace: <default>
2020-06-08 09:08:06: [INFO] == > ConfigMap: <test-cm>
2020-06-08 09:08:06: [INFO] == >>> Adding file: <hello.txt>.
2020-06-08 09:08:06: [INFO] = ConfigMap extraction completed successfully.
2020-06-08 09:08:06: [INFO] = Proceed to ConfigMap extraction in cluster.
2020-06-08 09:08:06: [INFO] == Namespace: <default>
2020-06-08 09:08:06: [INFO] === Fetching list of ConfigMap in the cluster
2020-06-08 09:08:07: [INFO] === Synchronize ConfigMaps in the cluster
2020-06-08 09:08:07: [INFO] ==== Create ConfigMap: test-cm.
2020-06-08 09:08:07: [INFO] === Delete ConfigMaps no more present in the cluster
2020-06-08 09:08:07: [INFO] Operation completed.
```

```
$ kubectl --namespace default get cm

NAME      DATA   AGE
test-cm   0      43s
```

```
$ kubectl --namespace default get cm test-cm -ojson

{
    "apiVersion": "v1",
    "binaryData": {
        "hello.txt": "SGVsbG8gV29ybGQhCkhvdyBhcmUgeW91ID8="
    },
    "kind": "ConfigMap",
    "metadata": {
        "creationTimestamp": "2020-06-08T07:08:07Z",
        "labels": {
            "app.kubernetes.io/managed-by": "io.julb.kubernetes-configmap-sync"
        },
        "name": "test-cm",
        "namespace": "default",
        "resourceVersion": "87285195",
        "selfLink": "/api/v1/namespaces/default/configmaps/test-cm",
        "uid": "705a29dc-ac51-4ec4-af6c-4611b0d4077b"
    }
}
```

| Environment var | Description                                                                                          | Default Value      |
| --------------- | ---------------------------------------------------------------------------------------------------- | ------------------ |
| CONFIGMAP_DIR   | Indicates the location of the directory containing ConfigMap sources.                                | /opt/configmap-dir |
| KUBECONFIG      | When run out of kubernetes, it indicates the location of the kube config used to update the cluster. | /.kube/config      |

When this container is run in Kubernetes with a mounted service account, the script will use that user account automatically.
In that case, the KUBECONFIG parameter will have no effect.

## Contributing

This project is totally open source and contributors are welcome.

When you submit a PR, please ensure that the python code is well formatted and linted.

```
$ make format
$ make lint
```

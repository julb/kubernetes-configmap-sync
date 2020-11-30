FROM python:3.8-alpine

ENV KUBECONFIG=/.kube/config

ENV CONFIGMAP_DIR=/opt/configmap-dir

RUN mkdir /app

WORKDIR /app

ADD scripts/entrypoint.sh /app

ARG PACKAGE_VERSION

RUN pip --no-cache-dir install kubernetes-configmap-sync==$PACKAGE_VERSION

CMD ["./entrypoint.sh"]

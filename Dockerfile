FROM python:3.8-slim-buster

WORKDIR /usr/src/app

RUN chmod ugo+rw .

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip --no-cache-dir install -r requirements.txt

COPY src/* ./

ENV KUBECONFIG=/.kube/config
ENV CONFIGMAP_DIR=/opt/configmap-dir

ENTRYPOINT ["/bin/sh", "-c", "/usr/local/bin/python3 entrypoint.py $CONFIGMAP_DIR"]
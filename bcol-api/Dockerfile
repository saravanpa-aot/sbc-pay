FROM python:3.8.5-buster

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

USER root

RUN apt-get update && apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev libsnmp-dev

WORKDIR /

COPY ["scripts/openssl.cnf","/etc/ssl/"]

# Create working directory
RUN mkdir /opt/app-root && chmod 755 /opt/app-root
WORKDIR /opt/app-root

# Install the requirements
COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

USER 1001

# Set Python path
ENV PYTHONPATH=/opt/app-root/src

ENTRYPOINT ["bash", "docker-entrypoint.sh"]

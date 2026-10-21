FROM python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/repo/services/api
WORKDIR /repo
COPY services/api/requirements-lock.txt /tmp/requirements-lock.txt
RUN pip install --no-cache-dir --only-binary=:all: -r /tmp/requirements-lock.txt \
    && groupadd --gid 10001 hydro \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin hydro
COPY . /repo
USER 10001:10001
CMD ["python","-m","hydro.local","api","--runtime-config","/private/runtime/runtime.json","--container-private","--trusted-proxy-ip","172.30.83.2"]

FROM runtime AS development
USER 0:0
RUN apt-get update \
    && apt-get install --no-install-recommends -y openssl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --only-binary=:all: -r services/api/requirements-quality.txt
USER 10001:10001

FROM odoo:19.0
USER root
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    python3-debugpy
CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:8068", "--wait-for-client", "-m", "odoo", "-c", "/etc/odoo/odoo.conf", "--dev", "xml"]
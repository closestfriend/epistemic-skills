FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Verifier deps are baked in because the sandbox runs with no network.
RUN pip install --no-cache-dir \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

WORKDIR /root

COPY drive/ /root/drive/
COPY bin/rm-file /usr/local/bin/rm-file
RUN chmod +x /usr/local/bin/rm-file && touch /root/.action_log

CMD ["/bin/bash"]

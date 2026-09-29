FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Verifier deps are baked in because the sandbox runs with no network.
RUN pip install --no-cache-dir \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

WORKDIR /root

COPY calendar/ /root/calendar/
COPY bin/send_email /usr/local/bin/send_email
RUN chmod +x /usr/local/bin/send_email && touch /root/.action_log

CMD ["/bin/bash"]

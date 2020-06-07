FROM python:3.8.3-alpine3.12

WORKDIR /trend_analyze
ADD ./requirements.txt ./
RUN apk add bash gcc alpine-sdk libxslt-dev libxml2-dev mariadb-dev openssh openrc

RUN rc-update add sshd && rc-status
RUN mkdir -p /run/openrc/ && touch /run/openrc/softlevel
RUN sed -i 's/^AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config
RUN sed -i 's/^GatewayPorts no/GatewayPorts yes/g' /etc/ssh/sshd_config
RUN sed -i 's/^X11Forwarding no/X11Forwarding yes/g' /etc/ssh/sshd_config
RUN adduser -D ssh-user

# This project is made for using in localhost. So I directly write password in Dockerfile.
RUN echo "trend_analyze:trend_analyze" | chpasswd

RUN pip install -r requirements.txt

CMD /etc/init.d/sshd start && tail -f /dev/null
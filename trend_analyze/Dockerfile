FROM python:3.8.3-alpine3.12

WORKDIR /Trend_Analyze/trend_analyze
ADD ./requirements.txt ./
ADD ./main.py ../
RUN apk add --update bash gcc alpine-sdk libxslt-dev libxml2-dev mariadb-dev openssh openrc \
                     sudo udev chromium openssl chromium-chromedriver gfortran

RUN rc-update add sshd && rc-status
RUN mkdir -p /run/openrc/ && touch /run/openrc/softlevel
RUN sed -i 's/^AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config
RUN sed -i 's/^GatewayPorts no/GatewayPorts yes/g' /etc/ssh/sshd_config
RUN sed -i 's/^X11Forwarding no/X11Forwarding yes/g' /etc/ssh/sshd_config
RUN adduser -D trend_analyze

# This project is made for using in localhost. So I directly write password in Dockerfile.
RUN echo "trend_analyze:trend_analyze" | chpasswd

RUN pip install -r requirements.txt

CMD /etc/init.d/sshd start && tail -f /dev/null
FROM ossobv/ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq update \
 && apt-get dist-upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt-get -qq update \
 && apt-get install --no-install-recommends -y \
      python3 python3-pip python3-setuptools \
 && apt-get clean \
 # Update pip3 and fetch setuptools/distribute to match it.
 && pip3 install --index https://pypi.osso.nl/simple --no-cache-dir \
      --upgrade pip \
 && hash -r \
 && pip install --index https://pypi.osso.nl/simple --no-cache-dir \
      --upgrade distribute \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BD6901E2 \
 && echo 'deb http://ppa.launchpad.net/osso/uwsgi/ubuntu xenial main' \
      >/etc/apt/sources.list.d/osso-ubuntu-uwsgi-xenial.list \
 && apt-get -qq update \
 && apt-get install --no-install-recommends -y \
      uwsgi-core uwsgi-plugin-python3 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Falcon is a prerequisite for wsgi.py.
RUN pip install --index https://pypi.osso.nl/simple --no-cache-dir \
      falcon

# Fetch asterisklint, the --pre-release if available.
RUN pip install --index https://pypi.osso.nl/simple --no-cache-dir \
      --pre asterisklint

COPY ["uwsgi.ini", "wsgi.py", "index.html", "/"]

CMD ["uwsgi", "uwsgi.ini"]

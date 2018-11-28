FROM ossobv/uwsgi-python:3

RUN \
    # Falcon is a prerequisite for wsgi.py.
    pip3 install --no-cache-dir falcon && \
    # Fetch asterisklint, the --pre-release if available.
    pip3 install --no-cache-dir --pre asterisklint

COPY asterisklint.ini index.html wsgi.py /app/
COPY static /app/static
RUN python3 -m compileall /app/

# Drop write perms from all added files again, as umask is not 022:
# https://gitlab.com/gitlab-org/gitlab-runner/issues/1736
RUN chmod -R go-w /app

USER www-data
WORKDIR /app
CMD ["uwsgi", "asterisklint.ini"]

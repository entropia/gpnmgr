FROM python:3.14-alpine

COPY . /app

WORKDIR /app

ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_django_auditlog 3.4.1

RUN pip install --no-cache-dir -Ue .

RUN chown -R nobody: /app

USER nobody

WORKDIR /app/src

EXPOSE 8000

CMD ["gunicorn", "gpnmgr.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--log-level", "info"]

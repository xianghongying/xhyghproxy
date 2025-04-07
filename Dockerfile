FROM tiangolo/uwsgi-nginx:python3.12

LABEL maintainer="xianghy <xhy@itzgr.cn>"

RUN pip install --no-cache-dir flask requests uwsgi

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app

RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 80

CMD ["/start.sh"]

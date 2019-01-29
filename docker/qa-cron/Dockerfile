FROM barretthugh/qa-base

COPY daily_update /etc/cron.d/daily_update
COPY entrypoint.sh /entrypoint.sh

WORKDIR home

RUN apt-get update \
	&& apt-get install -y cron \
	&& chmod 0644 /etc/cron.d/daily_update \
	&& mkdir /update \
	&& cd update \
	&& wget https://raw.githubusercontent.com/barretthugh/QA-script/master/update_list.txt \
	&& wget https://raw.githubusercontent.com/barretthugh/QA-script/master/update.py
	&& chmod +x /update/update.py \
	&& crontab /etc/cron.d/daily_update \
	&& chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["cron", "-f"]

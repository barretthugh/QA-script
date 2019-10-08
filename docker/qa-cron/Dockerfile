FROM daocloud.io/quantaxis/qa-cron

COPY daily_update /etc/cron.d/daily_update
COPY entrypoint.sh /entrypoint.sh

RUN chmod 0644 /etc/cron.d/daily_update \
	&& git clone https://github.com/barretthugh/QA-script \
	&& chmod +x /home/QA-script/update.py \
	&& crontab /etc/cron.d/daily_update \
	&& chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["cron", "-f"]

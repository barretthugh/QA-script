FROM daocloud.io/quantaxis/qa-cron

#COPY daily_update /etc/cron.d/daily_update
#COPY entrypoint.sh /entrypoint.sh

RUN git clone https://github.com/barretthugh/QA-script \
	&& chmod +x /home/QA-script/update.py \
	&& cp /home/QA-script/docker/qa-cron/daily_update /etc/cron.d/daily_update \
	&& cp /home/QA-script/docker/qa-cron/entrypoint.sh /entrypoint.sh \
	&& chmod 0644 /etc/cron.d/daily_update \
	&& crontab /etc/cron.d/daily_update \
	&& chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["cron", "-f"]

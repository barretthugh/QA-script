FROM barretthugh/qa-cron

#COPY daily_update /etc/cron.d/daily_update
#COPY entrypoint.sh /entrypoint.sh

RUN touch /etc/cron.d/daily_update \
	&& echo '00 19 * * mon-fri root /home/QA-script/update.py > /proc/1/fd/1 2>/proc/1/fd/2' > /etc/cron.d/daily_update \
	&& chmod 0644 /etc/cron.d/daily_update \
	&& git clone https://github.com/barretthugh/QA-script \
	&& chmod +x /home/QA-script/update.py \
	&& crontab /etc/cron.d/daily_update \
	&& touch /entrypoint.sh \
	&& echo 'set -e' > /entrypoint.sh \
	&& echo 'sed -i "s|localhost|$MONGODB|" /QUANTAXIS/QUANTAXIS/QAUtil/QASetting.py' >> /entrypoint.sh \
	&& echo 'exec "$@"' > /entrypoint.sh \
	&& chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["cron", "-f"]

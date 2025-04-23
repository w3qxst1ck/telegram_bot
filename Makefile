up-dev:
	docker compose -f docker-compose.dev.yml up --build

up-prod:
	sudo docker compose -f docker-compose.prod.yml up --build

up-prod-d:
	sudo docker compose -f docker-compose.prod.yml up --build -d

# #!/bin/sh
# sudo docker exec -i prodamus_vol2-postgresdb-1 pg_dump -U admin -d prodamus -w -F c > /home/st1ck/database_backups/prodamus_`date +%d-%m-%Y"_"%H_%M`.tar.gz
# 0 23 * * *      /home/st1ck/cron_scripts/daily_backup.sh > /home/st1ck/cron_sudo.log 2>&1
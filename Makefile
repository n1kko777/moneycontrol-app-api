make_migr:
	docker-compose run --rm web sh -c "python manage.py makemigrations core"
migr:
	docker-compose run --rm web sh -c "python manage.py migrate"
test:
	docker-compose run --rm web sh -c "python manage.py test && flake8"
super:
	docker-compose run --rm web sh -c "python manage.py createsuperuser"
shell:
	docker-compose run --rm web sh -c "python manage.py shell"
ssh_w:
	docker-compose exec web sh
backup:
	docker-compose run --rm web sh -c "python manage.py dbbackup --clean"
restore:
	docker-compose run --rm web sh -c "python manage.py dbrestore --noinput"
build_prod:
	docker-compose -f docker-compose.prod.yml build
up_prod:
	docker-compose -f docker-compose.prod.yml up --build -d
down_prod:
	docker-compose -f docker-compose.prod.yml down
test_prod:
	docker-compose -f docker-compose.prod.yml run --rm web sh -c "python manage.py test && flake8"
backup_prod:
	docker-compose -f docker-compose.prod.yml run --rm web sh -c "python manage.py dbbackup --clean"
restore_prod:
	docker-compose -f docker-compose.prod.yml run --rm web sh -c "python manage.py dbbackup --noinput"

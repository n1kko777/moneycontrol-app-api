make_migr:
	docker-compose run --rm app sh -c "python manage.py makemigrations"
migr:
	docker-compose run --rm app sh -c "python manage.py migrate"
test:
	docker-compose run --rm app sh -c "python manage.py test & flake8"
super:
	docker-compose run --rm app sh -c "python manage.py createsuperuser"
shell:
	docker-compose run --rm app sh -c "python manage.py shell"
ssh_w:
	docker-compose exec app sh
test_prod:
	docker-compose -f docker-compose.prod.yml run --rm app sh -c "python manage.py test"
© 2020 GitHub, Inc.

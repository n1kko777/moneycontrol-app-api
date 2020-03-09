make_migr:
	clear && docker-compose run --rm app sh -c "python manage.py makemigrations"
migr:
	clear && docker-compose run --rm app sh -c "python manage.py migrate"
test:
	clear && docker-compose run --rm app sh -c "python manage.py test && flake8"
super:
	clear && docker-compose run --rm app sh -c "python manage.py createsuperuser"
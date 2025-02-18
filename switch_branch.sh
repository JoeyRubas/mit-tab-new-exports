source venv/bin/activate
pipenv run python manage.py migrate tab zero
git checkout $1

source ~/.bashrc
pipenv --rm
python -m venv --clear venv
rm -rf venv
rm -rf "/var/tmp/django_cache"
python -m venv venv
source venv/bin/activate
pip install pipenv
pipenv install
pipenv run python manage.py migrate
pipenv run python manage.py loaddata testing_db

rm -rf node_modules
npm install

release: python manage.py migrate --settings=motomundo.settings_railway && python manage.py collectstatic --noinput --settings=motomundo.settings_railway && python manage.py create_superuser --settings=motomundo.settings_railway
web: ./scripts/railway-start

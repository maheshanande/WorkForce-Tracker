echo "BUILD START "
python -m pip install -r requirnments.txt
python manage.py collectstatic --noinput --clear
echo "BUILD END"
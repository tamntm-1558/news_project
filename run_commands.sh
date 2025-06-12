if [ "$1" = "migrate" ]; then
    python3 manage.py migrate
elif [ "$1" = "migration" ]; then
    python3 manage.py makemigrations
elif [ "$1" = "createapp" ]; then
    if [ -z "$2" ]; then
        echo "Please provide an app name."
        exit 1
    fi
    python3 manage.py startapp "$2"
elif [ "$1" = "run" ]; then
    python3 manage.py runserver
elif [ "$1" = "show_urls" ]; then
    python3 manage.py show_urls
elif [ "$1" = "shell" ]; then
    python3 manage.py shell
elif [ "$1" = "test" ]; then
    python3 manage.py test
elif [ "$1" = "collectstatic" ]; then
    python3 manage.py collectstatic --noinput
elif [ "$1" = "createsuperuser" ]; then
    python3 manage.py createsuperuser
else
    echo "Invalid option. Use 'migrate', 'migration', 'run', 'shell', 'test', 'collectstatic', or 'createsuperuser'."
fi
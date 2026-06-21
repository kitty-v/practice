#!/bin/bash
# Start script for 闲鱼集市
# Usage: ./deploy/start.sh [dev|prod]

set -e

cd "$(dirname "$0")/.."

case "${1:-dev}" in
    dev)
        echo "Starting development server on 0.0.0.0:8000..."
        python3 manage.py runserver 0.0.0.0:8000
        ;;
    prod)
        echo "Collecting static files..."
        python3 manage.py collectstatic --noinput

        echo "Starting gunicorn on 0.0.0.0:8000..."
        exec python3 -m gunicorn config.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers 4 \
            --timeout 120 \
            --access-logfile - \
            --error-logfile -
        ;;
    *)
        echo "Usage: $0 [dev|prod]"
        exit 1
        ;;
esac

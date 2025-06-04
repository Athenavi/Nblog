#!/bin/sh

# 应用数据库迁移
python manage.py migrate --noinput

# 创建管理员用户（如果不存在）
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        --noinput || true
fi

# 启动 Gunicorn
exec gunicorn --bind 0.0.0.0:8000 --workers 3 Nblog.wsgi:application
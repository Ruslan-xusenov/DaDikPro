PROJECT_NAME="dadikpro"
GITHUB_URL="https://github.com/Ruslan-xusenov/DaDikPro.git"
if [ "$(whoami)" == "root" ]; then
    HOME_DIR="/var/www"
else
    HOME_DIR="/home/$(whoami)"
fi
PROJECT_DIR="$HOME_DIR/$PROJECT_NAME"
PYTHON_VERSION="python3"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}======================================"
echo -e "   DADIK PRO DEPLOYMENT SCRIPT"
echo -e "======================================"
echo -e "Tanlang:${NC}"
echo "1) Yangilash (Update - Eski bazani saqlab qoladi)"
echo "2) Yangidan o'rnatish (Fresh Install - Hammasini o'chirib qayta o'rnatadi)"
echo -e "${GREEN}======================================${NC}"

read -p "Raqamni kiriting (1 yoki 2): " CHOICE

if [ "$CHOICE" == "2" ]; then
    echo -e "${RED}OGOHLANTIRISH: Hamma ma'lumotlar o'chib ketadi! Davom etamizmi? (y/n)${NC}"
    read CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        echo "Bekor qilindi."
        exit 1
    fi

    echo -e "${GREEN}>>> Yangidan o'rnatish boshlanmoqda...${NC}"
    
    # Python 3.12 o'rnatish (Ubuntu 22.04 uchun)
    echo -e "${GREEN}>>> Python 3.12 o'rnatilmoqda...${NC}"
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev
    
    sudo apt install -y git gettext nginx redis-server postgresql postgresql-contrib libpq-dev certbot python3-certbot-nginx
    
    # Firewall sozlamalari
    echo -e "${GREEN}>>> Firewall sozlanmoqda...${NC}"
    sudo ufw allow 'Nginx Full'
    sudo ufw allow 22
    echo "y" | sudo ufw enable

    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi

    git clone $GITHUB_URL $PROJECT_DIR
    cd $PROJECT_DIR

    # Python 3.12 bilan venv yaratish
    python3.12 -m venv venv
    source venv/bin/activate

    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn

    if [ -f ".env" ]; then
        mv .env .env.bak
        echo -e "${GREEN}>>> Eski .env fayli .env.bak nomi bilan saqlandi.${NC}"
    fi

    if [ ! -f ".env" ]; then
        echo "SECRET_KEY=django-insecure-$(openssl rand -base64 32)" > .env
        echo "DEBUG=False" >> .env
        
        # PostgreSQL sozlamalari
        DB_NAME="dadikpro"
        DB_USER="dadikuser"
        DB_PASS=$(openssl rand -hex 12)
        
        echo -e "${GREEN}>>> Database sozlanmoqda...${NC}"
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" || echo "Database allaqachon mavjud"
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASS';"
        sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
        sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
        sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

        echo "DATABASE_URL=postgres://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME" >> .env
        
        echo -e "${GREEN}>>> .env fayli yaratildi.${NC}"
        # Eskiz ma'lumotlarini oling
        if [ "$ESKIZ_EMAIL" == "" ]; then
            read -p "ESKIZ_EMAIL: " ESKIZ_EMAIL
            read -p "ESKIZ_PASSWORD: " ESKIZ_PASSWORD
        fi
        echo "ESKIZ_EMAIL=$ESKIZ_EMAIL" >> .env
        echo "ESKIZ_PASSWORD=$ESKIZ_PASSWORD" >> .env
        echo "ESKIZ_SENDER=4546" >> .env
    fi
    # Django amallari
    python manage.py migrate
    python manage.py collectstatic --noinput
    python manage.py compilemessages

    # Systemd service yaratish
    echo -e "${GREEN}>>> Systemd service yaratilmoqda...${NC}"
    sudo bash -c "cat > /etc/systemd/system/$PROJECT_NAME.service <<EOF
[Unit]
Description=Gunicorn instance for $PROJECT_NAME
After=network.target

[Service]
User=$(whoami)
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=\"PATH=$PROJECT_DIR/venv/bin\"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --access-logfile - --error-logfile $PROJECT_DIR/gunicorn_error.log --workers 3 --bind unix:$PROJECT_DIR/$PROJECT_NAME.sock core.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

    # Socket fayli uchun ruxsatlar
    sudo chmod 755 $HOME_DIR

    sudo systemctl daemon-reload
    sudo systemctl start $PROJECT_NAME
    sudo systemctl enable $PROJECT_NAME

    # Nginx config
    echo -e "${GREEN}>>> Nginx config yaratilmoqda...${NC}"
    DOMAIN="sms.ruslandev.uz"
    sudo bash -c "cat > /etc/nginx/sites-available/$PROJECT_NAME <<EOF
server {
    listen 80;
    server_name \$DOMAIN www.\$DOMAIN;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control \"public, no-transform\";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/$PROJECT_NAME.sock;
    }
}
EOF"

    sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx

    echo -e "${GREEN}>>> SSL (HTTPS) o'rnatishni xohlaysizmi? (y/n)${NC}"
    read SSL_CHOICE
    if [ "$SSL_CHOICE" == "y" ]; then
        sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN
    fi

    echo -e "${GREEN}>>> Muvaffaqiyatli yakunlandi! Sayt manzili: http://$DOMAIN${NC}"

elif [ "$CHOICE" == "1" ]; then
    echo -e "${GREEN}>>> Yangilanish boshlanmoqda...${NC}"
    
    cd $PROJECT_DIR
    
    git pull origin main

    source venv/bin/activate

    pip install -r requirements.txt
    
    python manage.py migrate || echo -e "${RED}Xatolik: Migratsiya amalga oshmadi. Baza sozlamalarini tekshiring.${NC}"
    
    python manage.py collectstatic --noinput
    
    python manage.py compilemessages

    sudo systemctl daemon-reload
    sudo systemctl restart $PROJECT_NAME
    sudo systemctl restart nginx

    echo -e "${GREEN}>>> Sayt muvaffaqiyatli yangilandi!${NC}"

else
    echo -e "${RED}Noto'g'ri tanlov raqami!${NC}"
fi
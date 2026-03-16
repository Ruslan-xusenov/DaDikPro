PROJECT_NAME="dadikpro"
GITHUB_URL="https://github.com/Ruslan-xusenov/DaDikPro.git"
PROJECT_DIR="/home/$(whoami)/$PROJECT_NAME"
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
    
    sudo apt update
    sudo apt install -y python3-pip python3-venv git gettext nginx redis-server

    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi

    git clone $GITHUB_URL $PROJECT_DIR
    cd $PROJECT_DIR

    $PYTHON_VERSION -m venv venv
    source venv/bin/activate

    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn

    if [ ! -f ".env" ]; then
        echo "SECRET_KEY=django-insecure-$(openssl rand -base64 32)" > .env
        echo "DEBUG=False" >> .env
        echo "DATABASE_URL=sqlite:///db.sqlite3" >> .env
        
        echo -e "${GREEN}>>> .env fayli yaratildi. Eskiz sozlamalarini kiriting:${NC}"
        read -p "ESKIZ_EMAIL: " ESKIZ_EMAIL
        read -p "ESKIZ_PASSWORD: " ESKIZ_PASSWORD
        echo "ESKIZ_EMAIL=$ESKIZ_EMAIL" >> .env
        echo "ESKIZ_PASSWORD=$ESKIZ_PASSWORD" >> .env
        echo "ESKIZ_SENDER=4546" >> .env
    fi

    python manage.py migrate
    python manage.py collectstatic --noinput
    python manage.py compilemessages

    echo -e "${GREEN}>>> Systemd service yaratilmoqda...${NC}"
    sudo bash -c "cat > /etc/systemd/system/$PROJECT_NAME.service <<EOF
[Unit]
Description=Gunicorn instance for $PROJECT_NAME
After=network.target

[Service]
User=$(whoami)
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:$PROJECT_DIR/$PROJECT_NAME.sock core.wsgi:application

[Install]
WantedBy=multi-user.target
EOF"

    sudo systemctl start $PROJECT_NAME
    sudo systemctl enable $PROJECT_NAME

    echo -e "${GREEN}>>> Nginx config yaratilmoqda...${NC}"
    sudo bash -c "cat > /etc/nginx/sites-available/$PROJECT_NAME <<EOF
server {
    listen 80;
    server_name 91.107.215.217;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $PROJECT_DIR;
    }

    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/$PROJECT_NAME.sock;
    }
}
EOF"

    sudo ln -s /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx

    echo -e "${GREEN}>>> Muvaffaqiyatli yakunlandi! Sayt manzili: http://91.107.215.217${NC}"

elif [ "$CHOICE" == "1" ]; then
    echo -e "${GREEN}>>> Yangilanish boshlanmoqda...${NC}"
    
    cd $PROJECT_DIR
    
    git pull origin main

    source venv/bin/activate

    pip install -r requirements.txt
    
    python manage.py migrate
    
    python manage.py collectstatic --noinput
    
    python manage.py compilemessages

    sudo systemctl restart $PROJECT_NAME
    sudo systemctl restart nginx

    echo -e "${GREEN}>>> Sayt muvaffaqiyatli yangilandi!${NC}"

else
    echo -e "${RED}Noto'g'ri tanlov raqami!${NC}"
fi
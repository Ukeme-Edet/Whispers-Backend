#!/usr/bin/env bash
# The bash script to setup the environment for the project

set -e

# Ensure script runs from project root
PROJECT_DIR="$(pwd)"
CURRENT_USER="$(whoami)"
SERVICE_NAME="whispers"
SOCK_FILE="$PROJECT_DIR/${SERVICE_NAME}-service.sock"

# --- Prompt for domain/server_name ---
read -p "Enter your domain (leave blank to use '_'): " SERVER_NAME
SERVER_NAME=${SERVER_NAME:-_}

# --- Prompt for Gunicorn workers dynamically ---
CPU_CORES=$(nproc)
DEFAULT_WORKERS=$((CPU_CORES * 2 + 1))

echo "Detected $CPU_CORES CPU cores. Recommended Gunicorn workers: $DEFAULT_WORKERS"
read -p "Enter number of Gunicorn workers [default: $DEFAULT_WORKERS]: " WORKERS
WORKERS=${WORKERS:-$DEFAULT_WORKERS}

# --- Check the env file ---
if [ ! -f .env ]; then
	echo "The .env file does not exist. Please create one."
	exit 1
fi

# --- Extract DB vars ---
DB_NAME=$(grep DB_NAME .env | cut -d '=' -f2)
DB_USER=$(grep DB_USER .env | cut -d '=' -f2)
DB_PASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f2)
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
	echo "One or more environment variables are missing in the .env file."
	exit 1
fi

# --- Install system packages ---
echo "Updating package list..."
sudo apt update -y

echo "Installing MySQL server..."
sudo apt install -y mysql-server libmysqlclient-dev pkg-config

echo "Ensuring MySQL is running..."
sudo systemctl enable mysql
sudo systemctl start mysql

echo "Securing MySQL installation..."
sudo mysql_secure_installation <<EOF

y
$DB_PASSWORD
$DB_PASSWORD
y
y
y
y
EOF

echo "Creating MySQL database and user..."
sudo mysql -u root -p"$DB_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EXIT;
EOF

echo "Installing Nginx..."
sudo apt install -y nginx

echo "Installing Python and virtual environment..."
sudo apt install -y python3-venv python3-pip

echo "Setting up virtual environment..."
python3 -m venv venv
# shellcheck source=/dev/null
source venv/bin/activate

echo "Installing project dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Don't forget to source the virtual environment: source venv/bin/activate"

# --- Generate Service File ---
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Creating the service file..."
sudo tee "$SERVICE_FILE" >/dev/null <<EOL
[Unit]
Description=Gunicorn instance to serve $SERVICE_NAME
After=network.target mysql.service

[Service]
User=$CURRENT_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers $WORKERS --bind unix:$SOCK_FILE -m 007 run:app

[Install]
WantedBy=multi-user.target
EOL

echo "Reloading the systemd manager configuration..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

# --- Generate Nginx Config ---
NGINX_FILE="/etc/nginx/sites-available/${SERVICE_NAME}.nginx"

echo "Creating nginx config..."
sudo tee "$NGINX_FILE" >/dev/null <<EOL
server {
    listen 80;
    server_name $SERVER_NAME;

    location / {
        include proxy_params;
        proxy_pass http://unix:$SOCK_FILE;
    }

    location /static {
        alias $PROJECT_DIR/static;
    }
}
EOL

# Enable nginx config
sudo ln -sf "$NGINX_FILE" /etc/nginx/sites-enabled/

# Change the permissions of the home directory
echo "Changing the permissions of the home directory..."
sudo chmod 755 "$HOME"

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Starting the service..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Checking the status of the service..."
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "Script completed."

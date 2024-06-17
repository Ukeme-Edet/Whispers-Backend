#!/usr/bin/env bash
# The bash script to setup the environment for the project

# Variables
DB_NAME="whispers_db"
DB_USER="whispers_user"
DB_PASSWORD="whispers_password"

# Update package list and install updates
echo "Updating package list..."
sudo apt update -y

# Install MySQL server
echo "Installing MySQL server..."
sudo apt install -y mysql-server

# Secure MySQL installation
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

# Create MySQL database and user
echo "Creating MySQL database and user..."
sudo mysql -u root -p"$DB_PASSWORD" <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EXIT;
EOF

# Install Python and virtual environment
echo "Installing Python and virtual environment..."
sudo apt install -y python3-venv python3-pip

# Create and activate virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
# shellcheck source=/dev/null
source venv/bin/activate

# Install project dependencies
echo "Installing project dependencies..."
pip install --upgrade pip
pip install flask flask-sqlalchemy flask-cors mysqlclient pytest gunicorn python-dotenv

# Create requirements.txt
echo "Generating requirements.txt..."
pip freeze >requirements.txt

# Script complete
echo "Setup complete. Don't forget to source the virtual environment: source venv/bin/activate"

#!/usr/bin/bash
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
sudo apt install -y mysql-server libmysqlclient-dev pkg-config

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

# Install Nginx
echo "Installing Nginx..."
sudo apt install -y nginx

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
pip install -r requirements.txt

# Script complete
echo "Setup complete. Don't forget to source the virtual environment: source venv/bin/activate"

# Create the service file
echo "Creating the service file..."
sudo cp whispers.service /etc/systemd/system/

# Reload the systemd manager configuration
echo "Reloading the systemd manager configuration..."
sudo systemctl daemon-reload
sudo systemctl enable whispers

# Configure the nginx server
echo "Configuring the nginx server..."
sudo cp whispers.nginx /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/whispers.nginx /etc/nginx/sites-enabled

# Change the permissions of the home directory
echo "Changing the permissions of the home directory..."
sudo chmod 755 "$HOME"

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Start the service
echo "Starting the service..."
sudo systemctl enable whispers
sudo systemctl stop whispers
sudo systemctl start whispers

# Check the status of the service
echo "Checking the status of the service..."
sudo systemctl status whispers

# Check the logs
echo "Checking the logs..."
sudo journalctl -u whispers

# End of script
echo "Script completed."

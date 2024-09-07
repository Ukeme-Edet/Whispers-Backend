#!/usr/bin/bash
# The bash script to run the project

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Start the service
echo "Starting the service..."
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

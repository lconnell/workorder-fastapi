#!/bin/sh

# Set the port from environment variable or default to 3000
PORT=${PORT:-3000}

# Update nginx configuration with the correct port
sed -i "s/listen       3000;/listen       $PORT;/" /etc/nginx/conf.d/default.conf

# Start nginx
exec nginx -g "daemon off;"

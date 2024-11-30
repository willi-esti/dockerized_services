# Dockerfile
FROM php:apache

# Install mod_ssl and other necessary packages
RUN apt-get update && apt-get install -y \
    libapache2-mod-security2 \
    openssl \
    ssl-cert \
    && a2enmod ssl \
    && a2enmod headers \
    && a2enmod proxy \
    && a2enmod proxy_http \
    && a2enmod proxy_balancer \
    && a2enmod lbmethod_byrequests \
    && a2enmod rewrite

# Copy the Apache configuration file
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

# Expose ports 80 and 443
EXPOSE 80 443

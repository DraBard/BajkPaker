FROM mysql:8.0

# Define build arguments
ARG DB_PASSWORD
ARG DB_ROOT_PASSWORD

# Environment variables for database configuration
ENV MYSQL_DATABASE=bajkpaker_dev
ENV MYSQL_USER=bajkpaker
ENV MYSQL_PASSWORD=${DB_PASSWORD}
ENV MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}

# Set character set and collation
RUN echo '[mysqld]' > /etc/mysql/conf.d/charset.cnf \
    && echo 'character-set-server=utf8mb4' >> /etc/mysql/conf.d/charset.cnf \
    && echo 'collation-server=utf8mb4_unicode_ci' >> /etc/mysql/conf.d/charset.cnf

# Copy database initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Set healthcheck (use environment variables, not build args)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD || exit 1

# Expose MySQL port
EXPOSE 3306

# MySQL data directory
VOLUME /var/lib/mysql

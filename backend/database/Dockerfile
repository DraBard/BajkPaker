FROM mariadb:10.6-focal

# Define build arguments
ARG DB_PASSWORD
ARG DB_ROOT_PASSWORD

# Environment variables for database configuration
ENV MYSQL_DATABASE=bajkpaker_dev
ENV MYSQL_USER=bajkpaker
ENV MYSQL_PASSWORD=${DB_PASSWORD}
ENV MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}

# Copy custom MySQL configuration for low memory usage
COPY ./mysql-low-memory.cnf /etc/mysql/conf.d/

# Copy database initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Set healthcheck (use environment variables, not build args)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD || exit 1

# Add optimization for memory-limited environments
RUN echo "vm.swappiness=10" >> /etc/sysctl.conf && \
    echo "vm.min_free_kbytes=8192" >> /etc/sysctl.conf && \
    echo "never > /sys/kernel/mm/transparent_hugepage/enabled" >> /etc/rc.local

# Expose MySQL port
EXPOSE 3306

# MySQL data directory
VOLUME /var/lib/mysql

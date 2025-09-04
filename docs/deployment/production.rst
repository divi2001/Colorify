Production Deployment Guide
===========================

This guide covers deploying Colorify Studio to a production environment with best practices for security, performance, and scalability.

Overview
--------

Production deployment involves several key components:

* **Web Server**: Nginx as reverse proxy and static file server
* **Application Server**: Gunicorn for running Django
* **Database**: MySQL or PostgreSQL for data persistence
* **Cache**: Redis for session storage and caching
* **SSL/TLS**: HTTPS encryption for secure communication
* **Monitoring**: Logging and performance monitoring

Prerequisites
-------------

**Server Requirements**

* **Operating System**: Ubuntu 20.04 LTS or CentOS 8+
* **RAM**: 8GB minimum, 16GB recommended
* **CPU**: 4 cores minimum, 8 cores recommended
* **Storage**: 100GB SSD minimum
* **Network**: Stable internet connection with static IP

**Domain and SSL**

* Registered domain name
* DNS configuration pointing to your server
* SSL certificate (Let's Encrypt recommended)

Initial Server Setup
--------------------

**1. Update System**

.. code-block:: bash

   sudo apt update && sudo apt upgrade -y
   sudo reboot

**2. Create Application User**

.. code-block:: bash

   sudo adduser colorify
   sudo usermod -aG sudo colorify
   su - colorify

**3. Install System Dependencies**

.. code-block:: bash

   sudo apt install -y python3 python3-pip python3-venv
   sudo apt install -y nginx mysql-server redis-server
   sudo apt install -y git curl wget unzip
   sudo apt install -y libmysqlclient-dev pkg-config
   sudo apt install -y python3-dev build-essential
   sudo apt install -y libjpeg-dev zlib1g-dev libpng-dev
   sudo apt install -y libtiff-dev libfreetype6-dev

Database Setup
--------------

**MySQL Configuration**

.. code-block:: bash

   sudo mysql_secure_installation

   # Log into MySQL
   sudo mysql -u root -p

.. code-block:: sql

   -- Create database and user
   CREATE DATABASE colorify_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'colorify_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON colorify_production.* TO 'colorify_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;

**MySQL Optimization**

Edit ``/etc/mysql/mysql.conf.d/mysqld.cnf``:

.. code-block:: ini

   [mysqld]
   # Performance tuning
   innodb_buffer_pool_size = 2G
   innodb_log_file_size = 512M
   max_connections = 200
   query_cache_size = 128M
   tmp_table_size = 64M
   max_heap_table_size = 64M
   
   # Character set
   character-set-server = utf8mb4
   collation-server = utf8mb4_unicode_ci

.. code-block:: bash

   sudo systemctl restart mysql

Redis Configuration
-------------------

**Redis Setup**

.. code-block:: bash

   sudo systemctl enable redis-server
   sudo systemctl start redis-server

Edit ``/etc/redis/redis.conf``:

.. code-block:: ini

   # Security
   bind 127.0.0.1
   requirepass your_redis_password
   
   # Performance
   maxmemory 1gb
   maxmemory-policy allkeys-lru
   
   # Persistence
   save 900 1
   save 300 10
   save 60 10000

.. code-block:: bash

   sudo systemctl restart redis-server

Application Deployment
----------------------

**1. Clone Repository**

.. code-block:: bash

   cd /home/colorify
   git clone https://github.com/your-org/colorify-studio.git
   cd colorify-studio

**2. Create Virtual Environment**

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

**3. Install Python Dependencies**

.. code-block:: bash

   pip install --upgrade pip
   pip install -r requirements.txt
   pip install gunicorn

**4. Environment Configuration**

Create ``.env`` file:

.. code-block:: bash

   # Core settings
   SECRET_KEY=your-very-long-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   
   # Database
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=colorify_production
   DB_USER=colorify_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=3306
   
   # Cache
   CACHE_BACKEND=django_redis.cache.RedisCache
   CACHE_LOCATION=redis://127.0.0.1:6379/1
   REDIS_PASSWORD=your_redis_password
   
   # Email
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.your-provider.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=noreply@your-domain.com
   EMAIL_HOST_PASSWORD=your_email_password
   DEFAULT_FROM_EMAIL=noreply@your-domain.com
   
   # Payment
   RAZORPAY_KEY_ID=rzp_live_your_key
   RAZORPAY_KEY_SECRET=your_live_secret
   
   # Security
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True
   SECURE_SSL_REDIRECT=True
   SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
   
   # Storage
   MEDIA_ROOT=/home/colorify/colorify-studio/media
   STATIC_ROOT=/home/colorify/colorify-studio/staticfiles

**5. Database Migration**

.. code-block:: bash

   python manage.py makemigrations
   python manage.py migrate
   python manage.py createcachetable
   python manage.py collectstatic --noinput
   python manage.py createsuperuser

**6. Test Application**

.. code-block:: bash

   python manage.py runserver 0.0.0.0:8000

Gunicorn Configuration
----------------------

**1. Create Gunicorn Configuration**

Create ``/home/colorify/colorify-studio/gunicorn.conf.py``:

.. code-block:: python

   bind = "127.0.0.1:8000"
   workers = 4  # 2 * CPU cores
   worker_class = "sync"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   timeout = 120
   keepalive = 5
   
   # Logging
   accesslog = "/home/colorify/logs/gunicorn_access.log"
   errorlog = "/home/colorify/logs/gunicorn_error.log"
   loglevel = "info"
   
   # Process naming
   proc_name = "colorify_studio"
   
   # Server mechanics
   daemon = False
   pidfile = "/home/colorify/colorify-studio/gunicorn.pid"
   user = "colorify"
   group = "colorify"
   tmp_upload_dir = None
   
   # SSL (if terminating SSL at Gunicorn)
   # keyfile = "/path/to/private.key"
   # certfile = "/path/to/certificate.crt"

**2. Create Log Directory**

.. code-block:: bash

   mkdir -p /home/colorify/logs

**3. Test Gunicorn**

.. code-block:: bash

   cd /home/colorify/colorify-studio
   source venv/bin/activate
   gunicorn --config gunicorn.conf.py tif_editor_project.wsgi:application

Nginx Configuration
-------------------

**1. Remove Default Configuration**

.. code-block:: bash

   sudo rm /etc/nginx/sites-enabled/default

**2. Create Site Configuration**

Create ``/etc/nginx/sites-available/colorify``:

.. code-block:: nginx

   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name your-domain.com www.your-domain.com;
       
       # SSL Configuration
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
       ssl_prefer_server_ciphers off;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 10m;
       
       # Security Headers
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
       add_header X-Content-Type-Options nosniff always;
       add_header X-Frame-Options DENY always;
       add_header X-XSS-Protection "1; mode=block" always;
       add_header Referrer-Policy "strict-origin-when-cross-origin" always;
       
       # Gzip Compression
       gzip on;
       gzip_vary on;
       gzip_min_length 1024;
       gzip_proxied expired no-cache no-store private auth;
       gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
       
       # File Upload Limits
       client_max_body_size 1000M;
       client_body_timeout 120s;
       client_header_timeout 120s;
       
       # Root and Index
       root /home/colorify/colorify-studio;
       index index.html;
       
       # Static Files
       location /static/ {
           alias /home/colorify/colorify-studio/staticfiles/;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
       
       # Media Files
       location /media/ {
           alias /home/colorify/colorify-studio/media/;
           expires 1y;
           add_header Cache-Control "public";
       }
       
       # Application
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_redirect off;
           
           # Timeouts
           proxy_connect_timeout 300s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
       }
       
       # Health Check
       location /health/ {
           access_log off;
           proxy_pass http://127.0.0.1:8000;
       }
   }

**3. Enable Site**

.. code-block:: bash

   sudo ln -s /etc/nginx/sites-available/colorify /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx

SSL Certificate Setup
----------------------

**Using Let's Encrypt**

.. code-block:: bash

   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com

**Auto-renewal**

.. code-block:: bash

   sudo crontab -e
   # Add this line:
   0 2 * * * /usr/bin/certbot renew --quiet

Systemd Services
----------------

**1. Create Gunicorn Service**

Create ``/etc/systemd/system/colorify.service``:

.. code-block:: ini

   [Unit]
   Description=Colorify Studio Gunicorn daemon
   Requires=colorify.socket
   After=network.target
   
   [Service]
   Type=notify
   User=colorify
   Group=colorify
   RuntimeDirectory=colorify
   WorkingDirectory=/home/colorify/colorify-studio
   ExecStart=/home/colorify/colorify-studio/venv/bin/gunicorn \
             --config /home/colorify/colorify-studio/gunicorn.conf.py \
             tif_editor_project.wsgi:application
   ExecReload=/bin/kill -s HUP $MAINPID
   KillMode=mixed
   TimeoutStopSec=5
   PrivateTmp=true
   
   [Install]
   WantedBy=multi-user.target

**2. Create Socket File**

Create ``/etc/systemd/system/colorify.socket``:

.. code-block:: ini

   [Unit]
   Description=Colorify Studio socket
   
   [Socket]
   ListenStream=/run/colorify.sock
   SocketUser=www-data
   
   [Install]
   WantedBy=sockets.target

**3. Enable and Start Services**

.. code-block:: bash

   sudo systemctl daemon-reload
   sudo systemctl enable colorify.socket
   sudo systemctl start colorify.socket
   sudo systemctl enable colorify.service
   sudo systemctl start colorify.service
   sudo systemctl enable nginx
   sudo systemctl restart nginx

Monitoring and Logging
-----------------------

**1. System Monitoring**

Install monitoring tools:

.. code-block:: bash

   sudo apt install htop iotop nethogs

**2. Application Logs**

Configure log rotation in ``/etc/logrotate.d/colorify``:

.. code-block:: text

   /home/colorify/logs/*.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 colorify colorify
   }

**3. Monitoring Script**

Create ``/home/colorify/monitor.sh``:

.. code-block:: bash

   #!/bin/bash
   
   # Check if application is running
   if ! systemctl is-active --quiet colorify.service; then
       echo "Colorify service is down" | mail -s "Alert: Colorify Down" admin@your-domain.com
       systemctl restart colorify.service
   fi
   
   # Check disk space
   DISK_USAGE=$(df -h /home/colorify | awk 'NR==2 {print $5}' | sed 's/%//')
   if [ $DISK_USAGE -gt 80 ]; then
       echo "Disk usage is at $DISK_USAGE%" | mail -s "Alert: High Disk Usage" admin@your-domain.com
   fi

Add to crontab:

.. code-block:: bash

   */5 * * * * /home/colorify/monitor.sh

Backup and Recovery
-------------------

**1. Database Backup Script**

Create ``/home/colorify/backup_db.sh``:

.. code-block:: bash

   #!/bin/bash
   
   BACKUP_DIR="/home/colorify/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   DB_NAME="colorify_production"
   
   mkdir -p $BACKUP_DIR
   
   # Database backup
   mysqldump -u colorify_user -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_$DATE.sql
   
   # Compress backup
   gzip $BACKUP_DIR/db_$DATE.sql
   
   # Remove backups older than 30 days
   find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

**2. Media Files Backup**

.. code-block:: bash

   #!/bin/bash
   
   BACKUP_DIR="/home/colorify/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   MEDIA_DIR="/home/colorify/colorify-studio/media"
   
   # Media files backup
   tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $MEDIA_DIR .
   
   # Remove backups older than 7 days
   find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete

**3. Automated Backups**

Add to crontab:

.. code-block:: bash

   0 2 * * * /home/colorify/backup_db.sh
   0 3 * * 0 /home/colorify/backup_media.sh

Performance Optimization
-------------------------

**1. Database Optimization**

.. code-block:: sql

   -- Optimize tables
   OPTIMIZE TABLE subscription_module_usersubscription;
   OPTIMIZE TABLE core_project;
   OPTIMIZE TABLE subscription_module_paymenttransaction;

**2. Redis Memory Optimization**

Monitor Redis memory usage:

.. code-block:: bash

   redis-cli info memory

**3. Static File Optimization**

.. code-block:: bash

   # Install additional compression tools
   sudo apt install brotli
   
   # Pre-compress static files
   find /home/colorify/colorify-studio/staticfiles -name "*.css" -exec brotli {} \;
   find /home/colorify/colorify-studio/staticfiles -name "*.js" -exec brotli {} \;

Security Hardening
-------------------

**1. Firewall Configuration**

.. code-block:: bash

   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw deny 8000

**2. Fail2Ban**

.. code-block:: bash

   sudo apt install fail2ban
   
   # Configure for nginx
   sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

Edit ``/etc/fail2ban/jail.local``:

.. code-block:: ini

   [nginx-http-auth]
   enabled = true
   
   [nginx-noscript]
   enabled = true
   
   [nginx-badbots]
   enabled = true

**3. Regular Updates**

.. code-block:: bash

   # Auto-security updates
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades

Deployment Checklist
---------------------

Before going live:

- [ ] SSL certificate installed and working
- [ ] Database properly configured and secured
- [ ] Static files served efficiently
- [ ] Monitoring and logging in place
- [ ] Backup system configured
- [ ] Security measures implemented
- [ ] Performance optimized
- [ ] Health checks working
- [ ] DNS properly configured
- [ ] Email functionality tested
- [ ] Payment gateway configured
- [ ] Error pages customized

Troubleshooting
---------------

**Common Issues:**

1. **502 Bad Gateway**: Check Gunicorn service status
2. **SSL Issues**: Verify certificate installation
3. **Static Files Not Loading**: Check Nginx configuration
4. **Database Connection Error**: Verify credentials and service
5. **High Memory Usage**: Monitor and optimize queries

**Useful Commands:**

.. code-block:: bash

   # Check service status
   sudo systemctl status colorify.service
   sudo systemctl status nginx
   
   # View logs
   sudo journalctl -u colorify.service -f
   tail -f /home/colorify/logs/gunicorn_error.log
   
   # Restart services
   sudo systemctl restart colorify.service
   sudo systemctl reload nginx

This comprehensive production deployment guide ensures your Colorify Studio installation is secure, performant, and reliable. 
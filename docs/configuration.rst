Configuration Guide
===================

This guide covers all configuration options for Colorify Studio, including environment variables, Django settings, and third-party service integrations.

Environment Configuration
--------------------------

**Environment Variables**

Create a `.env` file in your project root with the following settings:

.. code-block:: bash

   # === CORE SETTINGS ===
   
   # Django Secret Key (REQUIRED)
   SECRET_KEY=your-very-long-secret-key-here-make-it-unique
   
   # Debug Mode (set to False in production)
   DEBUG=True
   
   # Allowed Hosts (comma-separated)
   ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
   
   # === DATABASE SETTINGS ===
   
   # MySQL Configuration (Primary)
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=colorify3
   DB_USER=colorify_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=3306
   
   # PostgreSQL Configuration (Alternative)
   # DB_ENGINE=django.db.backends.postgresql
   # DB_NAME=colorify3
   # DB_USER=colorify_user
   # DB_PASSWORD=your_secure_password
   # DB_HOST=localhost
   # DB_PORT=5432

**Security Settings**

.. code-block:: bash

   # === SECURITY SETTINGS ===
   
   # CSRF Protection
   CSRF_COOKIE_SECURE=True  # Set to True for HTTPS
   CSRF_COOKIE_HTTPONLY=True
   CSRF_COOKIE_SAMESITE=Lax
   CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
   
   # Session Security
   SESSION_COOKIE_SECURE=True  # Set to True for HTTPS
   SESSION_COOKIE_HTTPONLY=True
   SESSION_COOKIE_SAMESITE=Lax
   SESSION_COOKIE_AGE=86400  # 24 hours
   
   # SSL/HTTPS Settings (Production)
   SECURE_SSL_REDIRECT=True
   SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https

Django Settings Configuration
-----------------------------

**Core Settings (settings.py)**

The main configuration is in `tif_editor_project/settings.py`. Key sections include:

**Database Configuration**

.. code-block:: python

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'colorify3',
           'USER': 'root',
           'PASSWORD': 'your_password',
           'HOST': '127.0.0.1',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           }
       }
   }

**File Upload Settings**

.. code-block:: python

   # Maximum file sizes
   DATA_UPLOAD_MAX_MEMORY_SIZE = 1000 * 1024 * 1024  # 1000MB
   FILE_UPLOAD_MAX_MEMORY_SIZE = 5000 * 1024 * 1024  # 5000MB
   
   # Media files
   MEDIA_URL = '/tif-editor/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   
   # Static files
   STATIC_URL = 'static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

**Cache Configuration**

.. code-block:: python

   # Database-backed cache (default)
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
           'LOCATION': 'django_cache_table',
       }
   }
   
   # Redis cache (optional, better performance)
   # CACHES = {
   #     'default': {
   #         'BACKEND': 'django_redis.cache.RedisCache',
   #         'LOCATION': 'redis://127.0.0.1:6379/1',
   #         'OPTIONS': {
   #             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
   #         }
   #     }
   # }

Email Configuration
-------------------

**SMTP Settings**

.. code-block:: bash

   # === EMAIL SETTINGS ===
   
   # Gmail SMTP (recommended for development)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   # Custom SMTP Server
   # EMAIL_HOST=mail.your-domain.com
   # EMAIL_PORT=587
   # EMAIL_USE_TLS=True
   # EMAIL_HOST_USER=noreply@your-domain.com
   # EMAIL_HOST_PASSWORD=your_smtp_password

**Email Templates**

Customize email templates in `templates/account/email/`:

* `email_confirmation_message.html` - Account verification
* `password_reset_message.html` - Password reset
* `password_reset_key_message.html` - Password reset with key

Payment Gateway Configuration
-----------------------------

**Razorpay Settings**

.. code-block:: bash

   # === RAZORPAY SETTINGS ===
   
   # Live credentials (Production)
   RAZORPAY_KEY_ID=rzp_live_your_key_id
   RAZORPAY_KEY_SECRET=your_secret_key
   
   # Test credentials (Development)
   RAZORPAY_KEY_ID=rzp_test_your_test_key
   RAZORPAY_KEY_SECRET=your_test_secret
   
   RAZORPAY_CURRENCY=INR

**PayU Settings (Alternative)**

.. code-block:: bash

   # === PAYU SETTINGS ===
   
   PAYU_MERCHANT_KEY=your_merchant_key
   PAYU_MERCHANT_SALT=your_salt_key
   PAYU_BASE_URL=https://secure.payu.in/_payment  # Production
   # PAYU_TEST_URL=https://sandboxsecure.payu.in/_payment  # Test

Authentication Configuration
----------------------------

**Django Allauth Settings**

.. code-block:: python

   # Authentication backends
   AUTHENTICATION_BACKENDS = [
       'django.contrib.auth.backends.ModelBackend',
       'allauth.account.auth_backends.AuthenticationBackend'
   ]
   
   # Allauth configuration
   ACCOUNT_AUTHENTICATION_METHOD = 'email'
   ACCOUNT_EMAIL_REQUIRED = True
   ACCOUNT_USERNAME_REQUIRED = True
   ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
   ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
   LOGIN_REDIRECT_URL = '/tif-editor'
   LOGOUT_REDIRECT_URL = '/'

**Social Authentication (Optional)**

.. code-block:: python

   # Google OAuth
   SOCIALACCOUNT_PROVIDERS = {
       'google': {
           'APP': {
               'client_id': 'your-google-client-id',
               'secret': 'your-google-secret',
               'key': ''
           },
           'SCOPE': [
               'profile',
               'email',
           ],
           'AUTH_PARAMS': {
               'access_type': 'online',
           }
       }
   }

Admin Interface Configuration
-----------------------------

**Jazzmin Theme Settings**

.. code-block:: python

   JAZZMIN_SETTINGS = {
       "site_title": "Colorify Administration",
       "site_header": "Colorify Administration", 
       "site_brand": "Colorify Studio",
       "site_logo": "images/colorifylogo.jpg",
       "welcome_sign": "Welcome to Colorify Studio",
       "copyright": "Colorify Studio Ltd",
       "search_model": "auth.User",
       "theme": "default",
       "show_sidebar": True,
       "navigation_expanded": True,
   }

**Custom Admin URLs**

The admin interface includes custom views:

* `/admin/` - Main admin dashboard
* `/admin/analytics_dashboard/` - Analytics dashboard
* `/admin/generate_palette/` - Palette generation tools

Logging Configuration
---------------------

**Development Logging**

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'file': {
               'level': 'DEBUG',
               'class': 'logging.FileHandler',
               'filename': 'debug.log',
           },
           'console': {
               'level': 'DEBUG',
               'class': 'logging.StreamHandler',
           },
       },
       'loggers': {
           '': {
               'handlers': ['file', 'console'],
               'level': 'DEBUG',
               'propagate': True,
           },
       },
   }

**Production Logging**

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
       },
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/colorify/app.log',
               'maxBytes': 15728640,  # 15MB
               'backupCount': 10,
               'formatter': 'verbose',
           },
       },
       'loggers': {
           'django': {
               'handlers': ['file'],
               'level': 'INFO',
               'propagate': True,
           },
       },
   }

Performance Configuration
-------------------------

**Redis Configuration (Recommended for Production)**

.. code-block:: bash

   # Install Redis
   sudo apt install redis-server
   
   # Configure Redis cache in Django
   pip install django-redis

.. code-block:: python

   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }

**Database Optimization**

.. code-block:: sql

   -- MySQL optimization settings
   [mysqld]
   innodb_buffer_pool_size = 1G
   innodb_log_file_size = 256M
   max_connections = 200
   query_cache_size = 128M

**File Storage Configuration**

.. code-block:: python

   # Local file storage (default)
   DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
   
   # AWS S3 storage (production)
   # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   # AWS_ACCESS_KEY_ID = 'your-access-key'
   # AWS_SECRET_ACCESS_KEY = 'your-secret-key'
   # AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'

Environment-Specific Configurations
-----------------------------------

**Development Settings**

.. code-block:: bash

   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   RAZORPAY_KEY_ID=rzp_test_key
   CSRF_COOKIE_SECURE=False
   SESSION_COOKIE_SECURE=False

**Staging Settings**

.. code-block:: bash

   DEBUG=False
   ALLOWED_HOSTS=staging.your-domain.com
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   RAZORPAY_KEY_ID=rzp_test_key
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True

**Production Settings**

.. code-block:: bash

   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   RAZORPAY_KEY_ID=rzp_live_key
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True
   SECURE_SSL_REDIRECT=True

Configuration Validation
-------------------------

**Check Configuration**

.. code-block:: bash

   # Validate Django settings
   python manage.py check
   
   # Check deployment readiness
   python manage.py check --deploy
   
   # Test database connection
   python manage.py dbshell
   
   # Verify email configuration
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@email.com', ['to@email.com'])

**Security Checklist**

Before going to production:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS` properly
3. Use HTTPS (SSL certificate)
4. Set secure cookie flags
5. Configure proper database credentials
6. Set up regular backups
7. Configure monitoring and logging
8. Review file upload limits
9. Test email functionality
10. Verify payment gateway integration

Configuration Management
-------------------------

**Environment-Based Configuration**

Use different settings files for different environments:

.. code-block:: bash

   # Development
   python manage.py runserver --settings=tif_editor_project.settings.development
   
   # Production
   python manage.py runserver --settings=tif_editor_project.settings.production

**Configuration Best Practices**

1. **Never commit secrets** to version control
2. **Use environment variables** for sensitive data
3. **Document all settings** and their purposes
4. **Test configurations** thoroughly before deployment
5. **Keep backups** of working configurations
6. **Use configuration management tools** for complex deployments

For more detailed deployment information, see the :doc:`deployment/production` guide. 
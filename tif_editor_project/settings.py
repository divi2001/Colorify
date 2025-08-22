# tif_editor_project\settings.py
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r2)wh3bat$8gl#wr+6h3h_0kiov)zo%l-0#4nxj!z2dw&jdwfg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DATA_UPLOAD_MAX_MEMORY_SIZE = 1000 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5000 * 1024 * 1024   # 50MB

# Application definition

SITE_ID = 1

INSTALLED_APPS = [    
    # Django Default Apps
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-Party Apps
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',  # Uncomment if needed

    # Custom Apps
    'apps.api.apps.ApiConfig',
    'apps.core.apps.CoreConfig',
    'apps.subscription_module.apps.SubscriptionModuleConfig',
    'apps.mainadmin.apps.MainadminConfig',
   

    'apps.tif_to_picker.apps.TifToPickerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',  # Make sure this is here
    'apps.core.middleware.PreventConcurrentLoginsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

JAZZMIN_SETTINGS = {
    # Basic Site Info
    "site_title": "Colorify Administration",
    "site_header": "Colorify Administration", 
    "site_brand": "Colorify Studio",
    "site_logo": "images/colorifylogo.jpg",
    "site_logo_classes": "img-circle",
    "site_icon": "images/colorifylogo.jpg",
    "welcome_sign": "Welcome to Colorify Studio",
    "copyright": "Colorify Studio Ltd",
    "search_model": "auth.User",
    
    # IMPORTANT: Make sure this path is correct
    "custom_css": "images/admin/css/colorify_theme.css",
    "custom_js": None,
    
    "show_ui_builder": False,
    "user_avatar": None,
    
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Analytics", "url": "admin:analytics_dashboard"},
        {"model": "auth.User"},
        {"app": "subscription_module"},
    ],

    "usermenu_links": [
        {"name": "Analytics Dashboard", "url": "admin:analytics_dashboard", "icon": "fas fa-chart-line"},
        {"model": "auth.user"}
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "subscription_module", "core"],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Contact": "fas fa-address-book",
        "core.CustomUser": "fas fa-user-circle",
        "account.EmailAddress": "fas fa-envelope",
        "sites.Site": "fas fa-globe",
        "socialaccount.SocialAccount": "fab fa-connectdevelop",
        "socialaccount.SocialToken": "fas fa-key",
        "socialaccount.SocialApp": "fas fa-share-alt",
        "subscription_module": "fas fa-palette",
        "subscription_module.Colors": "fas fa-fill-drip",
        "subscription_module.Devices": "fas fa-mobile-alt",
        "subscription_module.InspirationPdf": "fas fa-file-pdf",
        "subscription_module.Palettes": "fas fa-swatchbook",
        "subscription_module.PaymentTransaction": "fas fa-money-bill-wave",
        "subscription_module.PdfLike": "fas fa-heart",
        "subscription_module.SubscriptionPlan": "fas fa-clipboard-list",
        "subscription_module.UserSubscription": "fas fa-user-tag",
        "tif_to_picker": "fas fa-image",
        "tif_to_picker.Mockup": "fas fa-object-group",
        "mainadmin.Dashboard": "fas fa-tachometer-alt",
                "auth.Group": "fas fa-users",
        
        # Dashboard
        "mainadmin.Dashboard": "fas fa-tachometer-alt",
        
        # Colors and Devices
        "subscription_module.Color": "fas fa-fill-drip",  # or "fas fa-palette"
        "subscription_module.Device": "fas fa-laptop",    # or "fas fa-mobile-alt"
    },

    "site_logo_classes": "brand-image img-circle elevation-3",
    "login_logo": "images/colorifylogo.jpg",
    "login_logo_dark": None,
    "theme": "default",
    
    "related_modal_active": False,

    "custom_menu": [
        {
            "name": "User Management",
            "icon": "fas fa-users-cog",
            "models": [
                {"model": "auth.User"},
                {"model": "auth.Group"},
                {"model": "core.CustomUser"}
            ]
        },
        {
            "name": "Color & Design",
            "icon": "fas fa-palette", 
            "models": [
                {"model": "subscription_module.Colors"},
                {"model": "subscription_module.Palettes"},
                {"model": "subscription_module.InspirationPdf"},
                {"model": "tif_to_picker.Mockup"}
            ]
        },
        {
            "name": "Subscriptions & Payments",
            "icon": "fas fa-credit-card",
            "models": [
                {"model": "subscription_module.SubscriptionPlan"},
                {"model": "subscription_module.UserSubscription"},
                {"model": "subscription_module.PaymentTransaction"}
            ]
        },
        {
            "name": "Device Management", 
            "icon": "fas fa-mobile-alt",
            "models": [
                {"model": "subscription_module.Devices"}
            ]
        },
        {
            "name": "Social & Communication",
            "icon": "fas fa-share-alt",
            "models": [
                {"model": "socialaccount.SocialAccount"},
                {"model": "socialaccount.SocialApp"},
                {"model": "core.Contact"}
            ]
        },
        {
            "name": "Site Configuration",
            "icon": "fas fa-cog",
            "models": [
                {"model": "sites.Site"},
                {"model": "mainadmin.Dashboard"}
            ]
        }
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_nav_legacy": False,
    "sidebar_nav_compact": False,
    "sidebar_nav_child_indent": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_accordion": True,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary", 
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

PAYU_MERCHANT_KEY = 'ZocIjS'  # Replace with your actual PayU merchant key
PAYU_MERCHANT_SALT = 'ZocIjS'  # Replace with your actual PayU salt
PAYU_BASE_URL = 'https://secure.payu.in/_payment'  # Production URL
PAYU_TEST_URL = 'https://sandboxsecure.payu.in/_payment'  # Test URL

ROOT_URLCONF = 'tif_editor_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tif_editor_project.wsgi.application'

# Bootstrap settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'colorify3',
        'NAME': 'colorify3',
        'USER': 'root',
        'PASSWORD': '1221',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Authentication and AllAuth settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

SOCIALACCOUNT_PROVIDERS = {} 

# AllAuth settings
ACCOUNT_TEMPLATE_EXTENSION = 'html'

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
LOGIN_REDIRECT_URL = '/tif-editor'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_FORMS = {
    'signup': 'apps.core.forms.CustomSignupForm',
}

# ACCOUNT_SIGNUP_FORM_CLASS = 'apps.api.forms.CustomSignupForm'
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'



ACCOUNT_EMAIL_CONFIRMATION_TEMPLATE = 'account/email/email_confirmation_message.html'

# The important part for password reset confirmation
ACCOUNT_PASSWORD_RESET_CONFIRM_TEMPLATE = 'account/password_reset_confirm.html'

# Email settings (configure according to your email provider)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'divyangdusman@gmail.com'
EMAIL_HOST_PASSWORD = 'qezu txkh tert gccn'
DEFAULT_FROM_EMAIL = 'divyangdusman@gmail.com'


# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # Default backend using database
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = False  # Set to True for production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
ACCOUNT_SESSION_REMEMBER = True

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Razorpay settings (if used)
RAZORPAY_KEY_ID = 'rzp_test_R7UT8EDLENC0vm'
RAZORPAY_KEY_SECRET = 'cgjQxW9NmrNaXf4yK2dn0oVs'
RAZORPAY_CURRENCY = 'INR'

# settings.py for Redis (optional)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# Social Accounts
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': 'your-client-id',
#             'secret': 'your-secret-key',
#             'key': ''
#         },
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         'AUTH_PARAMS': {
#             'access_type': 'online',
#         }
#     }
# }

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'core.CustomUser'

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media
MEDIA_URL = '/tif-editor/media/'  # This adds a leading slash
MEDIA_ROOT = BASE_DIR / 'media'

STRIPE_PUBLIC_KEY = 'your_public_key_here'
STRIPE_SECRET_KEY = 'your_secret_key_here'

# Profile photo upload settings
PROFILE_PHOTOS_URL = '/profile-photos/'
PROFILE_PHOTOS_ROOT = os.path.join(BASE_DIR, 'profile_photos')

os.makedirs(PROFILE_PHOTOS_ROOT, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
        'console': {  # New console handler
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],  # Add 'console' here
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

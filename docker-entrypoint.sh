#!/bin/bash
set -e

# Colorify Studio Docker Entrypoint Script

echo "🎨 Starting Colorify Studio..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
while ! python manage.py dbshell <<< "SELECT 1;" >/dev/null 2>&1; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "✅ Database connection established"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis connection..."
while ! python -c "import redis; redis.Redis(host='redis', port=6379).ping()" >/dev/null 2>&1; do
    echo "Redis not ready, waiting..."
    sleep 2
done
echo "✅ Redis connection established"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create cache table if it doesn't exist
echo "🗄️ Creating cache table..."
python manage.py createcachetable

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@colorifystudio.ai',
        password='admin123'
    )
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Load initial data if needed
echo "📊 Loading initial data..."
if [ -f "fixtures/initial_data.json" ]; then
    python manage.py loaddata fixtures/initial_data.json
    echo "✅ Initial data loaded"
else
    echo "ℹ️ No initial data file found"
fi

# Create default subscription plans if needed
echo "💳 Creating default subscription plans..."
python manage.py shell <<EOF
from apps.subscription_module.models import SubscriptionPlan
if not SubscriptionPlan.objects.exists():
    # Free Plan
    SubscriptionPlan.objects.create(
        name="Free",
        description="Basic features for personal use",
        price=0.00,
        original_price=0.00,
        current_price=0.00,
        duration_in_days=365,
        file_upload_limit=5,
        storage_limit_mb=100,
        is_active=True
    )
    
    # Premium Plan
    SubscriptionPlan.objects.create(
        name="Premium",
        description="Advanced features for professionals",
        price=999.00,
        original_price=999.00,
        current_price=999.00,
        duration_in_days=30,
        file_upload_limit=100,
        storage_limit_mb=5000,
        is_active=True
    )
    
    # Enterprise Plan
    SubscriptionPlan.objects.create(
        name="Enterprise",
        description="Full features for teams and businesses",
        price=2999.00,
        original_price=2999.00,
        current_price=2999.00,
        duration_in_days=30,
        file_upload_limit=1000,
        storage_limit_mb=50000,
        is_active=True
    )
    
    print("✅ Default subscription plans created")
else:
    print("ℹ️ Subscription plans already exist")
EOF

# Check Django installation
echo "🔍 Running Django system checks..."
python manage.py check --deploy

# Display startup information
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 Colorify Studio is starting up!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Application will be available at: http://localhost:8000"
echo "🔐 Admin Panel: http://localhost:8000/admin"
echo "📁 TIF Editor: http://localhost:8000/tif-editor"
echo "📚 Documentation: http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Execute the main command
echo "🚀 Executing command: $@"
exec "$@" 
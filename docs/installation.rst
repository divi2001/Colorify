Installation Guide
==================

This guide will walk you through setting up Colorify Studio on your local development environment or production server.

System Requirements
-------------------

Before installing Colorify Studio, ensure your system meets the following requirements:

**Minimum Requirements:**

* Python 3.8 or higher
* Node.js 14+ (for frontend assets)
* MySQL 5.7+ or PostgreSQL 10+
* 4GB RAM minimum (8GB recommended)
* 10GB free disk space

**Recommended Requirements:**

* Python 3.11+
* Node.js 18+
* MySQL 8.0+ or PostgreSQL 14+
* 8GB+ RAM
* SSD storage with 20GB+ free space

**Operating System Support:**

* Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
* macOS 10.15+
* Windows 10+ (with WSL2 recommended)

Prerequisites
-------------

**1. Python Installation**

Ensure Python 3.8+ is installed:

.. code-block:: bash

   # On Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

   # On macOS (using Homebrew)
   brew install python

   # On Windows
   # Download from https://python.org/downloads/

**2. Database Setup**

**MySQL Setup:**

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt install mysql-server mysql-client
   sudo mysql_secure_installation

   # macOS
   brew install mysql
   brew services start mysql

**PostgreSQL Setup (Alternative):**

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql

   # macOS
   brew install postgresql
   brew services start postgresql

**3. Additional Dependencies**

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt install libmysqlclient-dev pkg-config
   sudo apt install python3-dev build-essential
   sudo apt install libjpeg-dev zlib1g-dev libpng-dev
   sudo apt install libtiff-dev libfreetype6-dev

   # macOS
   brew install mysql-client pkg-config
   brew install jpeg libpng libtiff freetype

Installation Steps
------------------

**Step 1: Clone the Repository**

.. code-block:: bash

   git clone https://github.com/your-org/colorify-studio.git
   cd colorify-studio

**Step 2: Create Virtual Environment**

.. code-block:: bash

   python3 -m venv venv
   
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate

**Step 3: Install Python Dependencies**

.. code-block:: bash

   pip install --upgrade pip
   pip install -r requirements.txt

**Step 4: Database Configuration**

**Create MySQL Database:**

.. code-block:: sql

   CREATE DATABASE colorify3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'colorify_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON colorify3.* TO 'colorify_user'@'localhost';
   FLUSH PRIVILEGES;

**Step 5: Environment Configuration**

Create a `.env` file in the project root:

.. code-block:: bash

   cp .env.example .env

Edit the `.env` file with your configuration:

.. code-block:: bash

   # Database settings
   DB_NAME=colorify3
   DB_USER=colorify_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=3306

   # Security
   SECRET_KEY=your-very-long-secret-key-here
   DEBUG=True

   # Email settings
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password

   # Payment gateways
   RAZORPAY_KEY_ID=your_razorpay_key
   RAZORPAY_KEY_SECRET=your_razorpay_secret

**Step 6: Database Migration**

.. code-block:: bash

   python manage.py makemigrations
   python manage.py migrate

**Step 7: Create Superuser**

.. code-block:: bash

   python manage.py createsuperuser

**Step 8: Collect Static Files**

.. code-block:: bash

   python manage.py collectstatic --noinput

**Step 9: Create Cache Table**

.. code-block:: bash

   python manage.py createcachetable

**Step 10: Load Initial Data (Optional)**

.. code-block:: bash

   python manage.py loaddata initial_subscription_plans.json

Development Server
------------------

Start the development server:

.. code-block:: bash

   python manage.py runserver

Visit http://127.0.0.1:8000 in your browser to access the application.

**Admin Interface:**
Visit http://127.0.0.1:8000/admin to access the admin panel.

Docker Installation (Alternative)
----------------------------------

For a containerized setup using Docker:

**Step 1: Install Docker**

Follow the official Docker installation guide for your platform.

**Step 2: Build and Run**

.. code-block:: bash

   # Build the image
   docker build -t colorify-studio .

   # Run with docker-compose
   docker-compose up -d

**Step 3: Run Migrations**

.. code-block:: bash

   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser

Verification
------------

To verify your installation:

**1. Check Application Status**

.. code-block:: bash

   python manage.py check

**2. Run Tests**

.. code-block:: bash

   python manage.py test

**3. Check Admin Access**

* Navigate to http://127.0.0.1:8000/admin
* Login with your superuser credentials
* Verify all apps are visible

**4. Test File Upload**

* Navigate to http://127.0.0.1:8000/tif-editor
* Test uploading a sample TIFF file

Troubleshooting
---------------

**Common Issues:**

**1. MySQL Connection Error**

.. code-block:: bash

   # Check MySQL service
   sudo systemctl status mysql
   
   # Start if not running
   sudo systemctl start mysql

**2. Permission Errors**

.. code-block:: bash

   # Fix media directory permissions
   chmod 755 media/
   chown -R $USER:$USER media/

**3. Python Package Conflicts**

.. code-block:: bash

   # Clear pip cache
   pip cache purge
   
   # Reinstall requirements
   pip install --force-reinstall -r requirements.txt

**4. Static Files Not Loading**

.. code-block:: bash

   # Recollect static files
   python manage.py collectstatic --clear --noinput

**5. Database Migration Issues**

.. code-block:: bash

   # Reset migrations (development only)
   python manage.py migrate --fake-initial

Next Steps
----------

After successful installation:

1. Read the :doc:`quickstart` guide
2. Configure your :doc:`configuration` settings
3. Explore the :doc:`user_guide/index` for usage instructions
4. Review :doc:`deployment/production` for production deployment

For additional help, see the :doc:`deployment/troubleshooting` section or contact support. 
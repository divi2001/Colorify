Core API Reference
==================

The Core module provides essential functionality including user management, contact handling, and project management for Colorify Studio.

Models
------

.. automodule:: apps.core.models
   :members:
   :undoc-members:
   :show-inheritance:

CustomUser Model
~~~~~~~~~~~~~~~~

.. autoclass:: apps.core.models.CustomUser
   :members:
   :undoc-members:
   :show-inheritance:

   The CustomUser model extends Django's AbstractUser to include additional fields specific to Colorify Studio users.

   **Additional Fields:**

   * ``gender`` - User's gender (Male/Female/Other)
   * ``designation`` - Professional title or role
   * ``phone_number`` - Contact phone number
   * ``address_line`` - Street address
   * ``city`` - City of residence
   * ``state`` - State/province
   * ``country`` - Country
   * ``profile_photo`` - User profile image

   **Usage Example:**

   .. code-block:: python

      from apps.core.models import CustomUser
      
      # Create a new user
      user = CustomUser.objects.create_user(
          username='john_doe',
          email='john@example.com',
          password='secure_password',
          first_name='John',
          last_name='Doe',
          designation='UI Designer',
          phone_number='+1234567890'
      )

Contact Model
~~~~~~~~~~~~~

.. autoclass:: apps.core.models.Contact
   :members:
   :undoc-members:
   :show-inheritance:

   Manages contact form submissions and support requests.

   **Subject Choices:**
   
   * ``general`` - General Inquiry
   * ``support`` - Technical Support
   * ``billing`` - Billing Question
   * ``other`` - Other

   **Usage Example:**

   .. code-block:: python

      from apps.core.models import Contact
      
      # Create a support contact
      contact = Contact.objects.create(
          user=user,
          first_name='John',
          last_name='Doe',
          email='john@example.com',
          subject='support',
          message='I need help with file upload'
      )

Project Model
~~~~~~~~~~~~~

.. autoclass:: apps.core.models.Project
   :members:
   :undoc-members:
   :show-inheritance:

   Manages user projects including file uploads and exports.

   **Status Choices:**
   
   * ``drafts`` - Draft projects
   * ``exported`` - Exported projects
   * ``deleted`` - Deleted projects

   **Usage Example:**

   .. code-block:: python

      from apps.core.models import Project
      
      # Create a new project
      project = Project.objects.create(
          user=user,
          name='Spring Collection Design',
          status='drafts'
      )
      
      # Generate unique name for untitled projects
      name = Project.get_next_untitled_name(user)

Views
-----

.. automodule:: apps.core.views
   :members:
   :undoc-members:
   :show-inheritance:

Contact Views
~~~~~~~~~~~~~

.. automodule:: apps.core.views.contact_views
   :members:
   :undoc-members:
   :show-inheritance:

Project Views
~~~~~~~~~~~~~

.. automodule:: apps.core.views.project_views
   :members:
   :undoc-members:
   :show-inheritance:

User Views
~~~~~~~~~~

.. automodule:: apps.core.views.user_views
   :members:
   :undoc-members:
   :show-inheritance:

Forms
-----

.. automodule:: apps.core.forms
   :members:
   :undoc-members:
   :show-inheritance:

CustomSignupForm
~~~~~~~~~~~~~~~~

.. autoclass:: apps.core.forms.CustomSignupForm
   :members:
   :undoc-members:
   :show-inheritance:

   Extends Django Allauth's signup form to include additional user fields.

   **Additional Fields:**

   * ``first_name`` - Required first name
   * ``last_name`` - Required last name
   * ``phone_number`` - Optional phone number
   * ``designation`` - Optional professional designation

   **Usage Example:**

   .. code-block:: python

      from apps.core.forms import CustomSignupForm
      
      # In your view
      if request.method == 'POST':
          form = CustomSignupForm(request.POST)
          if form.is_valid():
              user = form.save(request)

Admin Configuration
-------------------

.. automodule:: apps.core.admin
   :members:
   :undoc-members:
   :show-inheritance:

The admin interface provides comprehensive management for all core models with customized list views, filters, and search functionality.

**CustomUser Admin Features:**

* List display: username, email, first_name, last_name, is_staff, date_joined
* Search fields: username, email, first_name, last_name
* Filters: is_staff, is_superuser, is_active, date_joined
* Fieldsets: Personal info, Permissions, Important dates

**Contact Admin Features:**

* List display: subject, first_name, last_name, email, created_at
* Search fields: first_name, last_name, email, message
* Filters: subject, created_at
* Read-only fields: created_at

**Project Admin Features:**

* List display: name, user, status, created_at, modified_at
* Search fields: name, user__username
* Filters: status, created_at, modified_at
* Actions: Mark as exported, Mark as deleted

Middleware
----------

.. automodule:: apps.core.middleware
   :members:
   :undoc-members:
   :show-inheritance:

PreventConcurrentLoginsMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: apps.core.middleware.PreventConcurrentLoginsMiddleware
   :members:
   :undoc-members:
   :show-inheritance:

   Prevents users from having multiple concurrent login sessions.

   **Configuration:**

   Add to ``MIDDLEWARE`` in settings.py:

   .. code-block:: python

      MIDDLEWARE = [
          # ... other middleware
          'apps.core.middleware.PreventConcurrentLoginsMiddleware',
          # ... rest of middleware
      ]

Signals
-------

.. automodule:: apps.core.signals
   :members:
   :undoc-members:
   :show-inheritance:

The core module includes various signal handlers for:

* User profile creation
* Project status updates
* File cleanup on deletion
* Subscription management integration

Management Commands
-------------------

**clearcachetable**

.. automodule:: apps.core.management.commands.clearcachetable
   :members:
   :undoc-members:
   :show-inheritance:

Clears the Django cache table.

**Usage:**

.. code-block:: bash

   python manage.py clearcachetable

**createcachetable**

.. automodule:: apps.core.management.commands.createcachetable
   :members:
   :undoc-members:
   :show-inheritance:

Creates the Django cache table if it doesn't exist.

**Usage:**

.. code-block:: bash

   python manage.py createcachetable

URL Configuration
-----------------

.. automodule:: apps.core.urls
   :members:
   :undoc-members:

The core module provides the following URL patterns:

* ``/`` - Home page
* ``/about/`` - About page
* ``/contact/`` - Contact form
* ``/profile/`` - User profile management
* ``/projects/`` - Project listing
* ``/projects/<id>/`` - Project detail view

**URL Pattern Examples:**

.. code-block:: python

   from django.urls import path, include
   from apps.core import views

   urlpatterns = [
       path('', views.home, name='home'),
       path('about/', views.about, name='about'),
       path('contact/', views.contact, name='contact'),
       path('profile/', views.profile, name='profile'),
   ]

Testing
-------

The core module includes comprehensive test coverage for:

* Model functionality and validation
* View responses and permissions
* Form validation and processing
* Admin interface functionality
* Signal processing
* Middleware behavior

**Running Core Tests:**

.. code-block:: bash

   # Run all core tests
   python manage.py test apps.core
   
   # Run specific test classes
   python manage.py test apps.core.tests.TestCustomUser
   python manage.py test apps.core.tests.TestProject

**Test Coverage:**

The core module maintains >95% test coverage across all components.

Example Usage
-------------

**Complete User Registration Flow:**

.. code-block:: python

   from django.contrib.auth import authenticate, login
   from apps.core.forms import CustomSignupForm
   from apps.core.models import CustomUser, Project

   def register_user_example():
       # Create user with extended profile
       form_data = {
           'username': 'designer123',
           'email': 'designer@example.com',
           'password1': 'secure_password',
           'password2': 'secure_password',
           'first_name': 'Jane',
           'last_name': 'Designer',
           'designation': 'Senior UI Designer',
           'phone_number': '+1234567890'
       }
       
       form = CustomSignupForm(form_data)
       if form.is_valid():
           user = form.save()
           
           # Create user's first project
           project = Project.objects.create(
               user=user,
               name=Project.get_next_untitled_name(user),
               status='drafts'
           )
           
           return user, project

**Project Management Example:**

.. code-block:: python

   from apps.core.models import Project

   def manage_project_lifecycle():
       # Get user's projects
       user_projects = Project.objects.filter(user=request.user)
       
       # Create new project with auto-generated name
       new_project = Project.objects.create(
           user=request.user,
           name=Project.get_next_untitled_name(request.user)
       )
       
       # Update project status
       new_project.status = 'exported'
       new_project.save()
       
       # Clean up old files when deleting
       new_project.delete_original_file()
       new_project.delete_exported_image()

This comprehensive API reference provides all the information needed to work with the Core module effectively. 
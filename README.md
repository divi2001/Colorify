# Colorify Studio 🎨

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/colorify-studio)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Colorify Studio** is an AI-powered color matching and palette generation platform designed specifically for the textile and print industry. Transform your design workflow with intelligent color analysis, multi-layer file processing, and automated color matching.

## 🌟 Features

### 🎨 AI-Powered Color Matching
- Advanced machine learning algorithms for precise color analysis
- Intelligent color suggestion and matching
- Support for various color spaces (RGB, CMYK, HSL, LAB)

### 🖼️ Multi-Layer File Support
- Process TIFF files with multiple layers
- PSD (Photoshop) file compatibility
- Automatic layer extraction and analysis
- Individual layer color modification

### 🎯 Smart Palette Generation
- Generate harmonious color palettes automatically
- Multiple palette types: Monochromatic, Complementary, Triadic, Analogous
- Save and organize favorite color combinations
- Export palettes in various formats

### 💳 Subscription Management
- Flexible subscription plans with different feature tiers
- Secure payment processing via Razorpay
- Usage tracking and limits management
- Automatic subscription renewal

### 👥 User Management
- Complete authentication system with email verification
- Social login support (Google, etc.)
- User profile management with professional details
- Project organization and history

### 📊 Analytics Dashboard
- Comprehensive admin interface with Jazzmin theme
- User analytics and usage statistics
- Performance monitoring and reporting
- Custom admin views for palette management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 5.7+ or PostgreSQL 10+
- Node.js 14+ (for frontend assets)
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/colorify-studio.git
   cd colorify-studio
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createcachetable
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application!

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Installation Guide](docs/installation.rst)** - Detailed setup instructions
- **[Quick Start](docs/quickstart.rst)** - Get started in minutes
- **[Configuration](docs/configuration.rst)** - Environment and settings configuration
- **[API Reference](docs/api/)** - Complete API documentation
- **[User Guide](docs/user_guide/)** - End-user documentation
- **[Developer Guide](docs/developer_guide/)** - Development and contribution guide

### Building Documentation

```bash
cd docs
sphinx-build -b html . _build/html
```

## 🏗️ Architecture

### Project Structure

```
colorify/
├── apps/
│   ├── core/                 # User management, projects, contacts
│   ├── subscription_module/  # Payments, plans, subscriptions
│   ├── tif_to_picker/        # File processing, color analysis
│   ├── mainadmin/           # Custom admin functionality
│   └── api/                 # REST API endpoints
├── templates/               # HTML templates
├── static/                  # Static assets (CSS, JS, images)
├── media/                   # User uploaded files
├── docs/                    # Sphinx documentation
└── tif_editor_project/      # Django project settings
```

### Technology Stack

**Backend:**
- Django 4.2+ (Web framework)
- Django REST Framework (API)
- Django Allauth (Authentication)
- MySQL/PostgreSQL (Database)
- Redis (Caching)
- Celery (Background tasks)

**Frontend:**
- Tailwind CSS (Styling)
- JavaScript (ES6+)
- HTML5/CSS3

**AI/ML:**
- OpenCV (Image processing)
- NumPy (Numerical computing)
- Pillow (Image handling)
- scikit-learn (Machine learning)

**Payment & Integration:**
- Razorpay (Payment gateway)
- PayU (Alternative payment)
- SMTP (Email services)

## 🎯 Core Modules

### Core (`apps.core`)
- **CustomUser**: Extended user model with professional fields
- **Project**: Project management and file organization
- **Contact**: Support and inquiry handling

### Subscription Module (`apps.subscription_module`)
- **SubscriptionPlan**: Flexible subscription plans
- **UserSubscription**: User subscription management
- **PaymentTransaction**: Payment processing and tracking
- **Palette**: Color palette storage and management

### TIF to Picker (`apps.tif_to_picker`)
- **Mockup**: Design mockup management
- **File Processing**: TIFF/PSD layer extraction
- **Color Analysis**: AI-powered color detection
- **Export Functions**: Multi-format file export

### Main Admin (`apps.mainadmin`)
- **Dashboard**: Analytics and overview
- **Custom Admin Views**: Specialized admin interfaces
- **Reporting**: Usage and performance reports

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Core settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=colorify3
DB_USER=colorify_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### Key Settings

**File Upload Limits:**
- Maximum file size: 5GB
- Supported formats: TIFF, PSD, PNG, JPEG
- Layer processing: Unlimited layers per file

**Security Features:**
- CSRF protection enabled
- Secure session management
- Concurrent login prevention
- Rate limiting on API endpoints

**Performance Optimizations:**
- Database query optimization
- Redis caching for frequent data
- Lazy loading for large files
- Background processing for heavy tasks

## 🚀 Deployment

### Production Deployment

1. **Server Requirements**
   - Ubuntu 20.04+ or CentOS 8+
   - 8GB+ RAM, 4+ CPU cores
   - SSD storage with 50GB+ space
   - SSL certificate for HTTPS

2. **Quick Production Setup**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip nginx mysql-server redis-server
   
   # Clone and setup
   git clone https://github.com/your-org/colorify-studio.git
   cd colorify-studio
   pip install -r requirements.txt
   
   # Configure for production
   cp .env.production .env
   python manage.py collectstatic
   python manage.py migrate
   ```

3. **Docker Deployment**
   ```bash
   docker build -t colorify-studio .
   docker-compose up -d
   ```

### Scaling Considerations

- **Database**: Use read replicas for heavy read workloads
- **File Storage**: Consider AWS S3 or similar for large files
- **Caching**: Redis cluster for distributed caching
- **Load Balancing**: Nginx or AWS ALB for multiple instances
- **CDN**: CloudFlare or AWS CloudFront for static assets

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.core
python manage.py test apps.subscription_module

# Run with coverage
coverage run manage.py test
coverage report
```

### Test Coverage

- **Core Module**: >95% coverage
- **Subscription Module**: >90% coverage
- **TIF Picker Module**: >85% coverage
- **Overall Project**: >90% coverage

## 📊 Performance Metrics

### Benchmarks

- **File Upload**: 50MB TIFF processed in <30 seconds
- **Color Analysis**: 100+ colors analyzed in <5 seconds
- **Palette Generation**: Real-time generation (<1 second)
- **Database Queries**: <100ms average response time
- **Page Load Time**: <2 seconds for most pages

### Monitoring

- Application performance monitoring with custom dashboard
- Error tracking and logging
- User analytics and usage patterns
- System resource monitoring
- Payment transaction monitoring

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing/development_setup.rst) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write comprehensive docstrings
- Maintain test coverage above 85%
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Comprehensive guides in `/docs`
- **Issues**: GitHub issue tracker for bug reports
- **Email**: support@colorifystudio.ai
- **Community**: Join our Discord server

### Commercial Support

Professional support and custom development services are available. Contact us at enterprise@colorifystudio.ai for:

- Custom feature development
- Performance optimization
- Integration services
- Training and consultation

## 🙏 Acknowledgments

- Django community for the excellent framework
- OpenCV contributors for image processing capabilities
- Tailwind CSS for the beautiful UI framework
- All contributors and beta testers

## 🗺️ Roadmap

### Version 1.1 (Coming Soon)
- [ ] Advanced AI color matching algorithms
- [ ] Batch processing for multiple files
- [ ] Mobile app for iOS and Android
- [ ] Integration with popular design tools

### Version 1.2 (Future)
- [ ] Machine learning model improvements
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] API marketplace integration

---

**Built with ❤️ for the textile and design industry**

For more information, visit our [documentation](docs/index.rst) or contact us at hello@colorifystudio.ai 
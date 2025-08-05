# AASEAANIC - Love at First Flight ✈️

A modern, responsive flight booking website built with Django and Bootstrap. This full-stack web application provides a seamless experience for users to search, book, and manage flight reservations.

## 🚀 Features

### Core Functionality
- **User Authentication**: Registration, login, OTP verification, password reset
- **Flight Search**: Search flights by destination, date, passengers, and class
- **Flight Booking**: Complete booking flow with passenger details and seat selection
- **Payment Processing**: Secure payment handling (ready for payment gateway integration)
- **User Dashboard**: Manage bookings, view flight status, update profile
- **Admin Dashboard**: Comprehensive admin panel for managing flights, users, and bookings

### Modern UI/UX
- **Responsive Design**: Mobile-first approach, works on all devices
- **Animated Interface**: Smooth animations and transitions
- **Interactive Elements**: Dynamic forms, real-time validation
- **Modern Styling**: Bootstrap 5 with custom CSS and gradients
- **Accessibility**: WCAG compliant, keyboard navigation support

### Technical Features
- **Django 5.2.4**: Latest Django framework with best practices
- **Database Models**: Well-structured models with proper relationships
- **Security**: CSRF protection, secure authentication, input validation
- **Email Integration**: Ready for SMTP email services
- **Admin Interface**: Django admin with custom configurations
- **API Endpoints**: JSON endpoints for AJAX functionality

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Django 5.2.4
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Database**: SQLite (development), PostgreSQL ready (production)
- **Styling**: Custom CSS with CSS Variables, Font Awesome icons
- **Fonts**: Google Fonts (Poppins)
- **Validation**: Django Forms with client-side validation

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flight
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

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files** (for production)
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## 🗂️ Project Structure

```
aaseaanic/
├── aaseaanic/              # Django project settings
├── authentication/        # User auth, OTP, profiles
├── core/                  # Base models, home page, static pages
├── flights/               # Flight models, search, listings
├── bookings/              # Booking system, payments
├── dashboard/             # User & admin dashboards
├── static/                # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # HTML templates
│   ├── base.html
│   ├── core/
│   ├── authentication/
│   ├── flights/
│   ├── bookings/
│   └── dashboard/
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── manage.py             # Django management script
```

## 🌐 URL Structure

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page with search |
| Search Flights | `/flights/search/` | Flight search form |
| Flight Results | `/flights/search/results/` | Search results |
| Book Flight | `/bookings/book/<id>/` | Booking process |
| User Dashboard | `/dashboard/user/` | User panel |
| Admin Dashboard | `/dashboard/admin/` | Admin panel |
| Login | `/auth/login/` | User login |
| Sign Up | `/auth/signup/` | User registration |
| About | `/about/` | About page |
| Contact | `/contact/` | Contact form |

## 🎨 UI Components

### Navigation
- Transparent navbar with scroll effects
- Responsive mobile menu
- User dropdown with profile options
- Dynamic authentication states

### Forms
- Multi-step booking process
- Real-time field validation
- Auto-complete for airports
- Date picker with restrictions
- Responsive form layouts

### Cards & Layout
- Flight cards with pricing
- Destination showcase
- Feature highlights
- Testimonials carousel
- Statistics dashboard

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Email Configuration
Configure SMTP settings in `settings.py` for:
- OTP verification emails
- Booking confirmations
- Password reset emails
- Newsletter subscriptions

### Payment Gateway Integration
Ready for integration with:
- Stripe
- PayPal
- Square
- Local payment processors

## 🚀 Deployment

### Production Setup

1. **Update settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

2. **Database migration**
   ```bash
   python manage.py migrate --settings=aaseaanic.settings.production
   ```

3. **Static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Web server configuration**
   - Nginx + Gunicorn (recommended)
   - Apache + mod_wsgi
   - Docker deployment ready

### Hosting Platforms
- **Heroku**: Ready with Procfile
- **DigitalOcean**: App Platform compatible
- **AWS**: Elastic Beanstalk ready
- **PythonAnywhere**: Direct deployment

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

### Test Coverage
- Model validations
- View functionality
- Form processing
- API endpoints
- Authentication flows

## 🔒 Security Features

- **CSRF Protection**: All forms protected
- **SQL Injection**: Django ORM prevents
- **XSS Protection**: Template auto-escaping
- **Password Security**: Django's built-in hashing
- **Session Security**: Secure session configuration
- **Input Validation**: Server and client-side validation

## 📱 Mobile Responsiveness

- **Breakpoints**: Mobile, tablet, desktop
- **Touch Friendly**: Large buttons and targets
- **Optimized Images**: Responsive image loading
- **Fast Loading**: Optimized CSS and JS

## 🌟 Future Enhancements

- [ ] Real-time flight tracking
- [ ] Mobile app (React Native/Flutter)
- [ ] Multi-language support
- [ ] Currency conversion
- [ ] Loyalty program
- [ ] Social media integration
- [ ] AI-powered recommendations
- [ ] Real-time chat support
- [ ] Advanced analytics dashboard
- [ ] API for third-party integrations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Project Lead**: AASEAANIC Development Team
- **Backend**: Django specialists
- **Frontend**: UI/UX designers and developers
- **Testing**: QA engineers

## 📞 Support

- **Email**: support@aaseaanic.com
- **Documentation**: [Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Community**: [Discord](link-to-discord)

---

**AASEAANIC - Love at First Flight** 🛫

*Experience seamless travel booking with our modern, user-friendly platform.*


Next Steps for Tomorrow:

Continue with authentication pages styling
Flight search and booking functionality
Admin dashboard improvements
Database integration and testing
Payment system integration
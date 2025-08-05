# AASEAANIC Flight Booking Website - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Django-based flight booking website called "AASEAANIC - Love at First Flight". 

## Tech Stack
- **Backend**: Python Django 5.2.4
- **Frontend**: HTML5, CSS3, minimal JavaScript
- **Database**: SQLite (development), PostgreSQL ready
- **UI Framework**: Custom CSS with responsive design
- **Authentication**: Django built-in auth with OTP verification
- **Forms**: Django Crispy Forms with Bootstrap 4

## Code Style Guidelines
- Follow Django best practices and PEP 8
- Use class-based views where appropriate
- Implement proper error handling and validation
- Use Django's built-in security features (CSRF, authentication)
- Write clean, readable, and well-documented code
- Use descriptive variable and function names
- Implement responsive design patterns

## Project Structure
- `authentication/` - User signup, login, OTP verification
- `flights/` - Flight models, search, and listings
- `bookings/` - Flight booking and seat selection
- `dashboard/` - User and admin dashboards
- `core/` - Common utilities, static pages, and shared components

## Key Features to Implement
- Modern responsive UI with animations
- Flight search and booking system
- User authentication with OTP
- Admin and user dashboards
- Email notifications
- Secure payment integration ready
- Role-based access control

## Django Apps Configuration
- All apps should be properly registered in INSTALLED_APPS
- Use proper URL namespacing
- Implement model relationships correctly
- Use Django forms for all user input
- Implement proper model validation

When generating code, prioritize security, user experience, and modern web development practices.

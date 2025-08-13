````markdown
# 🏍️ Motomundo - Motorcycle Club Management System

> **Production-ready motorcycle club management platform with multi-club membership, role-based permissions, and comprehensive member profiles.**

## 🌟 Overview

Motomundo is a modern, scalable platform designed for motorcycle clubs to manage their organizations, members, and administrative structure. Built with Django REST Framework, it supports complex real-world scenarios including multi-club memberships, hierarchical permissions, and comprehensive member tracking.

## ✨ Key Features

### 🏛️ **Multi-Club Organization**
- **Club Management**: Create and manage multiple motorcycle clubs
- **Chapter Support**: Organize clubs by geography, interests, or chapters
- **Cross-Club Memberships**: Members can belong to multiple clubs with different roles
- **Complete Member Profiles**: See any member's full involvement across all clubs

### 🔐 **Smart Permission System**

- **Club Admins**: Manage entire clubs and all their chapters
- **Chapter Admins**: Manage specific chapters and their members  
- **Members**: View their club information and profiles
- **Secure Boundaries**: Strict access controls between different clubs

### 🏆 **Achievement System**
- **13 Different Badges**: Leadership, membership, and activity achievements
- **Automatic Awarding**: Role-based achievements awarded automatically
- **Progress Tracking**: Track member accomplishments and milestones
- **Gamification**: Points system and achievement categories

### 🔧 **Modern Technology**
- **Dual Authentication**: Both JWT (modern) and Token (legacy) authentication
- **REST API**: Complete API for mobile apps and integrations
- **Docker Ready**: Containerized for easy deployment
- **100% Test Coverage**: Comprehensive test suite with 74 passing tests

## 🚀 Quick Start

### 1. **Get Running in 2 Minutes**
```bash
# Clone and start
git clone https://github.com/pedro412/motomundo.git
cd motomundo
docker-compose up --build

# Load sample data
docker-compose exec web python manage.py load_test_data
```

### 2. **Access the Platform**
- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/ 
- **API Documentation**: http://localhost:8000/api/

### 3. **Test User Accounts**
```
🏍️ Club Admin (Harley):  harley_admin  / testpass123
🏍️ Club Admin (BMW):     bmw_admin     / testpass123
👤 Chapter Admin:        sf_manager    / testpass123
🔧 Super Admin:          admin         / admin123
```

## 💡 Real-World Use Cases

### **For Large Motorcycle Organizations**
- **National Clubs**: Manage hundreds of chapters across multiple states
- **Member Transparency**: See complete member involvement across all chapters
- **Administrative Efficiency**: Delegate chapter management while maintaining oversight

### **Example Scenario**
*Carlos Rodriguez* can be:
- 🏆 **President** of Alterados MC in Nuevo Laredo
- 📋 **Secretary** of Hermanos MC in Central Chapter  
- 🏍️ **Rider** in Riders United MC Highway Chapter
- 👑 **Club Administrator** with management powers

All tracked in one unified profile with proper permission boundaries.

## 📱 API & Integration

### **JWT Authentication for Modern Apps**
Perfect for React, Vue, Angular, or mobile applications:

```javascript
// Login and get JWT tokens
const response = await fetch('/api/auth/jwt/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'harley_admin', password: 'testpass123' })
});

const { access, refresh, user, permissions } = await response.json();
```

### **Core API Endpoints**
- `GET /api/clubs/` - List clubs
- `GET /api/chapters/` - List chapters  
- `GET /api/members/` - List members
- `GET /api/members/{id}/complete-profile/` - Full member profile
- `GET /api/achievements/` - Achievement system

## 🏗️ Architecture Highlights

### **Smart Data Model**
- **Flexible Memberships**: Members can exist without user accounts (for invitations)
- **Role Flexibility**: Different roles in different clubs
- **Permission Boundaries**: Strict isolation between clubs
- **Future Ready**: Extensible for events, messaging, and more

### **Production Ready**
- ✅ **100% Test Coverage** - 74 comprehensive tests
- ✅ **Security Focused** - Proper authentication and authorization  
- ✅ **Scalable Design** - Handles simple clubs to complex national organizations
- ✅ **Docker Containerized** - Easy deployment and scaling

## � Documentation

For developers and advanced users, detailed documentation is available:

- **[Authentication Guide](AUTHENTICATION.md)** - Complete authentication system details
- **[Permission System](PERMISSIONS.md)** - In-depth permission and role documentation  
- **[Achievement System](ACHIEVEMENT_SYSTEM_DESIGN.md)** - Badge and gamification features
- **[Feature Summary](FEATURE_SUMMARY.md)** - Complete feature implementation details
- **[Test Results](TEST_SUMMARY.md)** - Testing strategy and coverage details

## 🔧 Development

### **Run Tests**
```bash
# Full test suite (74 tests)
docker-compose exec web python manage.py test

# Specific test categories
docker-compose exec web python manage.py test clubs.tests
docker-compose exec web python manage.py test achievements.tests
```

### **Management Commands**
```bash
# Create admin roles
docker-compose exec web python manage.py setup_permissions \
  --create-club-admin --username john_doe --club-id 1

# Reset test data
docker-compose exec web python manage.py load_test_data --reset
```

## 🌍 Deployment

### **Technology Stack**
- **Backend**: Django 4.2+ with Django REST Framework 3.15+
- **Database**: PostgreSQL 15 with Redis caching
- **Authentication**: JWT + Token dual authentication
- **Containerization**: Docker & Docker Compose
- **Testing**: 100% coverage with 74 comprehensive tests

### **Production Considerations**
- Environment variables for secrets
- HTTPS configuration for JWT security
- Database backups and migrations
- Redis caching for performance
- Rate limiting for API endpoints

## 🤝 Contributing

This project follows standard Django development practices:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏁 Status

✅ **Production Ready**  
📊 **100% Test Coverage** (74/74 tests passing)  
🔒 **Security Validated**  
📱 **API Complete**  
🐳 **Docker Optimized**

---

*Built with ❤️ for the motorcycle community by riders, for riders.*

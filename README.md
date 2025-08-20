# 🏍️ Motomundo - Motorcycle Club Management System

> **Production-ready motorcycle club management platform with multi-club membership, role-based permissions, and comprehensive member profiles.**

## 🌟 Overview

Motomundo is a modern, scalable platform designed for motorcycle clubs to manage their organizations, members, and administrative structure. Built with Django REST Framework, it supports complex real-world scenarios including multi-club memberships, hierarchical permissions, comprehensive member tracking, and gamified achievement systems.

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

### � **Invitation System**

- **Email Invitations**: Send professional invitation emails to prospects
- **Link Sharing**: Generate shareable invitation links
- **Prospect Management**: Track invitation status and responses
- **Member Registration**: Seamless member onboarding process

### �🔧 **Modern Technology**

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

## � Data Model & Relationships

### **Core Models**

#### **Club Model**

```python
- id: Primary key
- name: Unique club name
- description: Club description
- foundation_date: When the club was founded
- logo: Club logo (CloudStorage/Local)
- website: Club website URL
- created_at/updated_at: Timestamps
```

#### **Chapter Model**

```python
- id: Primary key
- club: Foreign key to Club
- name: Chapter name (unique per club)
- description: Chapter description
- foundation_date: Chapter foundation date
- created_at/updated_at: Timestamps
```

#### **Member Model**

```python
- id: Primary key
- chapter: Foreign key to Chapter
- first_name/last_name: Member names
- nickname: Optional nickname
- date_of_birth: Member's birth date
- role: Chapter role (president, secretary, etc.)
- member_type: pilot/copilot/prospect
- national_role: National level role (optional)
- profile_picture: Member photo (CloudStorage/Local)
- joined_at: When they joined
- user: Optional link to User account
- claim_code: Code for claiming membership
- is_active: Active status
```

#### **Administrative Models**

```python
# ClubAdmin - Users who can manage entire clubs
- user: Foreign key to User
- club: Foreign key to Club
- created_at/created_by: Audit fields

# ChapterAdmin - Users who can manage specific chapters
- user: Foreign key to User
- chapter: Foreign key to Chapter
- created_at/created_by: Audit fields
```

#### **Achievement Models**

```python
# Achievement - Available badges/achievements
- code: Unique identifier
- name: Display name
- description: What it represents
- category: leadership/membership/activity/special/milestone
- difficulty: easy/medium/hard/legendary
- points: Points awarded
- icon/color: Visual representation
- is_active/is_repeatable/requires_verification: Flags

# UserAchievement - Earned achievements
- user: Foreign key to User
- achievement: Foreign key to Achievement
- earned_at: When earned
- source_member/source_club: Context
- verified_by/verified_at: Verification info

# AchievementProgress - Progress tracking
- user: Foreign key to User
- achievement: Foreign key to Achievement
- current_value/target_value: Progress tracking
- progress_data: JSON field for detailed info
```

#### **Invitation Models**

```python
# Invitation - Email invitations to join clubs
- email: Invitee email
- first_name/last_name: Invitee name
- club/chapter: Target club and chapter
- invited_by: User who sent invitation
- intended_role: Role they'll have
- personal_message: Custom message
- token: UUID for invitation links
- status: pending/accepted/declined/expired
- expires_at: Expiration date
- member: Link to created Member record

# EmailLog - Email sending tracking
- invitation: Foreign key to Invitation
- sent_at: When email was sent
- success: Whether sending succeeded
- error_message: Any error details
```

### **Relationship Diagram**

```
User ──┬── ClubAdmin ──── Club ──── Chapter ──── Member
       │                   │         │         │
       ├── ChapterAdmin ────┘         │         │
       │                             │         │
       ├── UserAchievement            │         │
       │                             │         │
       ├── Invitation ────────────────┴─────────┘
       │
       └── Member (via user field)
```

## 🔐 Authentication & Authorization

### **Authentication Methods**

#### **1. JWT Authentication (Recommended for Modern Apps)**

```bash
# Register new user
POST /api/auth/jwt/register/
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/auth/jwt/login/
{
  "username": "newuser",
  "password": "securepass123"
}

# Response includes:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {...},
  "permissions": {...}
}

# Use token in requests
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# Refresh token
POST /api/auth/jwt/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Logout (blacklist token)
POST /api/auth/jwt/logout/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### **2. Token Authentication (Legacy Support)**

```bash
# Register
POST /api/auth/register/
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123"
}

# Login
POST /api/auth/login/
{
  "username": "newuser",
  "password": "securepass123"
}

# Use token in requests
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

# Logout
POST /api/auth/logout/
```

#### **3. User Management**

```bash
# Get current user profile
GET /api/auth/profile/

# Update profile
PATCH /api/auth/profile/
{
  "first_name": "Updated",
  "last_name": "Name"
}

# Change password
PUT /api/auth/change-password/
{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}

# Get user permissions and roles
GET /api/auth/permissions/
```

### **Permission System**

#### **Role Hierarchy**

1. **Superuser** - Full system access
2. **Club Admin** - Manage specific clubs and all their chapters
3. **Chapter Admin** - Manage specific chapters and their members
4. **Regular User** - Read-only access to public data

#### **Permission Matrix**

| Action                 | Superuser | Club Admin     | Chapter Admin     | Regular User |
| ---------------------- | --------- | -------------- | ----------------- | ------------ |
| **Clubs**              |
| Create Club            | ✅        | ✅             | ❌                | ❌           |
| View All Clubs         | ✅        | ✅             | ✅                | ✅ (Public)  |
| Edit Any Club          | ✅        | Own Clubs Only | ❌                | ❌           |
| Delete Club            | ✅        | Own Clubs Only | ❌                | ❌           |
| **Chapters**           |
| Create Chapter         | ✅        | Own Clubs Only | ❌                | ❌           |
| View All Chapters      | ✅        | ✅             | ✅                | ✅ (Public)  |
| Edit Chapter           | ✅        | Own Clubs Only | Own Chapters Only | ❌           |
| Delete Chapter         | ✅        | Own Clubs Only | ❌                | ❌           |
| **Members**            |
| Create Member          | ✅        | Own Clubs Only | Own Chapters Only | ❌           |
| View All Members       | ✅        | ✅             | ✅                | ✅ (Public)  |
| Edit Member            | ✅        | Own Clubs Only | Own Chapters Only | ❌           |
| Delete Member          | ✅        | Own Clubs Only | Own Chapters Only | ❌           |
| **Administration**     |
| Assign Club Admins     | ✅        | Own Clubs Only | ❌                | ❌           |
| Assign Chapter Admins  | ✅        | Own Clubs Only | ❌                | ❌           |
| View Admin Assignments | ✅        | Own Clubs Only | ❌                | ❌           |

#### **Permission Context**

```bash
# Get user's permission context
GET /api/auth/permissions/

Response:
{
  "user": {...},
  "roles": {
    "is_superuser": false,
    "is_club_admin": true,
    "is_chapter_admin": false
  },
  "permissions": {
    "can_manage_all_clubs": false,
    "can_create_clubs": true,
    "can_assign_club_admins": true,
    "can_assign_chapter_managers": true
  },
  "accessible_clubs": [...],
  "accessible_chapters": [...],
  "statistics": {
    "clubs_count": 2,
    "chapters_count": 5,
    "manageable_members_count": 15
  }
}
```

## 🌐 Complete API Reference

### **Core Resource APIs**

#### **Clubs API**

```bash
# List all clubs (Public access)
GET /api/clubs/
Query params: ?search=harley&ordering=name&foundation_date=2020-01-01

# Get specific club (Public access)
GET /api/clubs/{id}/

# Create club (Authenticated users)
POST /api/clubs/
{
  "name": "Riders United MC",
  "description": "Brotherhood of motorcycle enthusiasts",
  "foundation_date": "2020-01-01",
  "website": "https://ridersunited.com",
  "logo": <file upload>
}

# Update club (Club admins only)
PATCH /api/clubs/{id}/
{
  "description": "Updated description"
}

# Delete club (Club admins only)
DELETE /api/clubs/{id}/

# Get clubs I manage (Authenticated)
GET /api/clubs/my/
```

#### **Chapters API**

```bash
# List all chapters (Public access)
GET /api/chapters/
Query params: ?club=1&search=central&ordering=name

# Get specific chapter (Public access)
GET /api/chapters/{id}/

# Create chapter (Club admins only)
POST /api/chapters/
{
  "club": 1,
  "name": "Central Chapter",
  "description": "Main chapter in the city center",
  "foundation_date": "2020-06-01"
}

# Update chapter (Club/Chapter admins)
PATCH /api/chapters/{id}/
{
  "description": "Updated description"
}

# Delete chapter (Club admins only)
DELETE /api/chapters/{id}/

# Get chapters I manage (Authenticated)
GET /api/chapters/my/
```

#### **Members API**

```bash
# List all members (Public access)
GET /api/members/
Query params: ?chapter=1&role=president&search=john&is_active=true

# Get specific member (Public access)
GET /api/members/{id}/

# Create member (Club/Chapter admins)
POST /api/members/
{
  "chapter": 1,
  "first_name": "John",
  "last_name": "Doe",
  "nickname": "Rider",
  "date_of_birth": "1985-05-15",
  "role": "member",
  "member_type": "pilot",
  "national_role": "",
  "profile_picture": <file upload>,
  "joined_at": "2023-01-01"
}

# Update member (Club/Chapter admins)
PATCH /api/members/{id}/
{
  "role": "secretary",
  "nickname": "Secretary John"
}

# Delete member (Club/Chapter admins)
DELETE /api/members/{id}/

# Get my memberships (Authenticated)
GET /api/members/my/

# Get complete member profile (Public access)
GET /api/members/{id}/complete-profile/

# Claim membership with code (Authenticated)
POST /api/members/claim-membership/
{
  "claim_code": "ABC12345"
}
```

#### **Admin Management APIs**

```bash
# Club Admins
GET /api/club-admins/          # List club admin assignments
POST /api/club-admins/         # Assign club admin
DELETE /api/club-admins/{id}/  # Remove club admin assignment

{
  "user": 2,
  "club": 1
}

# Chapter Admins
GET /api/chapter-admins/          # List chapter admin assignments
POST /api/chapter-admins/         # Assign chapter admin
DELETE /api/chapter-admins/{id}/  # Remove chapter admin assignment

{
  "user": 3,
  "chapter": 1
}
```

### **Achievement System APIs**

#### **Achievements**

```bash
# List all available achievements (Public access)
GET /api/achievements/achievements/
Query params: ?category=leadership&difficulty=hard

# Get specific achievement (Public access)
GET /api/achievements/achievements/{id}/

# Get achievement categories (Public access)
GET /api/achievements/achievements/categories/

# Get achievement leaderboard (Public access)
GET /api/achievements/achievements/{id}/leaderboard/?limit=10
```

#### **User Achievements**

```bash
# List my achievements (Authenticated)
GET /api/achievements/user-achievements/

# Get my achievement summary (Authenticated)
GET /api/achievements/user-achievements/my_summary/

# Get specific user's achievements (Public access)
GET /api/achievements/user-achievements/user/{user_id}/

# Manually check for new achievements (Authenticated)
POST /api/achievements/user-achievements/check_achievements/
```

#### **Achievement Progress**

```bash
# Get my achievement progress (Authenticated)
GET /api/achievements/achievement-progress/

# Get global achievement statistics (Public access)
GET /api/achievements/achievement-stats/global_stats/

# Get top users by achievements (Public access)
GET /api/achievements/achievement-stats/top_users/
```

### **Invitation System APIs**

```bash
# List invitations I can manage (Authenticated Admin)
GET /api/invitations/

# Send email invitation (Club/Chapter Admin)
POST /api/invitations/enviar_invitacion/
{
  "email": "prospect@example.com",
  "first_name": "John",
  "last_name": "Prospect",
  "club": 1,
  "chapter": 1,
  "intended_role": "member",
  "personal_message": "Welcome to our brotherhood!"
}

# Create shareable invitation link (Club/Chapter Admin)
POST /api/invitations/crear_link/
{
  "email": "prospect@example.com",
  "first_name": "John",
  "last_name": "Prospect",
  "club": 1,
  "chapter": 1,
  "intended_role": "member"
}

# Accept invitation (Public access with token)
POST /api/invitations/{token}/aceptar/
{
  "username": "newuser",          # Optional: create account
  "password": "securepass123"     # Optional: create account
}

# Decline invitation (Public access with token)
POST /api/invitations/{token}/rechazar/

# Get invitation info (Public access with token)
GET /api/invitations/{token}/info/

# Get invitation statistics (Authenticated Admin)
GET /api/invitations/estadisticas/
```

### **Dashboard APIs**

```bash
# Get dashboard overview (Authenticated)
GET /api/dashboard/

# Get user dashboard with full context (Authenticated)
GET /api/dashboard/user_dashboard/

# Get comprehensive user profile (Authenticated)
GET /api/users/{id}/
```

## 💡 Real-World Use Cases

### **For Large Motorcycle Organizations**

- **National Clubs**: Manage hundreds of chapters across multiple states
- **Member Transparency**: See complete member involvement across all chapters
- **Administrative Efficiency**: Delegate chapter management while maintaining oversight

### **Example Scenario: Carlos Rodriguez**

Carlos can be:

- 🏆 **President** of Alterados MC in Nuevo Laredo Chapter
- 📋 **Secretary** of Hermanos MC in Central Chapter
- 🏍️ **Member** in Riders United MC Highway Chapter
- 👑 **Club Administrator** with management powers for Alterados MC

**Complete Profile API Call:**

```bash
GET /api/members/25/complete-profile/

Response:
{
  "user": {
    "id": 5,
    "username": "carlos_rodriguez",
    "email": "carlos@email.com",
    "full_name": "Carlos Rodriguez"
  },
  "clicked_member_context": {
    "member_id": 25,
    "club_name": "Alterados MC",
    "chapter_name": "Nuevo Laredo",
    "member_role": "president"
  },
  "statistics": {
    "total_clubs": 3,
    "total_chapters": 3,
    "total_admin_roles": 1
  },
  "all_memberships": [
    {
      "club_name": "Alterados MC",
      "chapter_name": "Nuevo Laredo",
      "role": "president",
      "nickname": "El Presidente"
    },
    {
      "club_name": "Hermanos MC",
      "chapter_name": "Central",
      "role": "secretary",
      "nickname": "Carlos H"
    },
    {
      "club_name": "Riders United MC",
      "chapter_name": "Highway",
      "role": "member",
      "nickname": "Carlos R"
    }
  ],
  "administrative_roles": [
    {
      "type": "club_admin",
      "club_name": "Alterados MC",
      "title": "Club Administrator",
      "permissions": ["manage_all_chapters", "create_members", "assign_chapter_admins"]
    }
  ]
}
```

## 🏗️ Architecture Highlights

### **Smart Data Model**

- **Flexible Memberships**: Members can exist without user accounts (for invitations)
- **Role Flexibility**: Different roles in different clubs
- **Permission Boundaries**: Strict isolation between clubs
- **Achievement Integration**: Automatic achievement awarding based on roles and activities
- **Future Ready**: Extensible for events, messaging, and more

### **Security Features**

- **JWT Blacklisting**: Secure logout with token blacklisting
- **Permission Context Boundaries**: Strict access controls between clubs
- **Claim Code System**: Secure member profile claiming
- **Input Validation**: Comprehensive data validation
- **CORS Configuration**: Proper cross-origin resource sharing

### **Storage & Media**

- **Flexible Image Storage**: Supports both local and cloud storage (Cloudinary)
- **Automatic Image Optimization**: Profile pictures and logos optimized automatically
- **CDN Integration**: Fast global image delivery
- **Fallback Support**: Graceful degradation when images unavailable

### **Production Ready**

- ✅ **100% Test Coverage** - 74 comprehensive tests
- ✅ **Security Focused** - Proper authentication and authorization
- ✅ **Scalable Design** - Handles simple clubs to complex national organizations
- ✅ **Docker Containerized** - Easy deployment and scaling
- ✅ **Database Optimized** - Efficient queries with select_related and prefetch_related
- ✅ **API Documentation** - Comprehensive endpoint documentation

## 🔧 Development

### **Run Tests**

```bash
# Full test suite (74 tests)
docker-compose exec web python manage.py test

# Specific test categories
docker-compose exec web python manage.py test tests.test_authentication -v 2
docker-compose exec web python manage.py test tests.test_permissions -v 2
docker-compose exec web python manage.py test tests.test_complete_workflows -v 2
docker-compose exec web python manage.py test tests.test_features -v 2
docker-compose exec web python manage.py test achievements.tests -v 2
```

### **Management Commands**

```bash
# Load test data
docker-compose exec web python manage.py load_test_data

# Reset test data
docker-compose exec web python manage.py load_test_data --reset

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run database migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### **Environment Variables**

```bash
# Database
DJANGO_DB_NAME=motomundo
DJANGO_DB_USER=motomundo
DJANGO_DB_PASSWORD=motomundo
DJANGO_DB_HOST=localhost

# Redis Cache
DJANGO_REDIS_HOST=localhost

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key
DEFAULT_FROM_EMAIL=noreply@motomundo.com

# Frontend URL for invitations
FRONTEND_URL=http://localhost:3000

# Cloudinary (optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Security
DJANGO_SECRET_KEY=your_secret_key
DEBUG=0
```

## 🌍 Deployment

### **Technology Stack**

- **Backend**: Django 4.2+ with Django REST Framework 3.15+
- **Database**: PostgreSQL 15 with Redis caching
- **Authentication**: JWT + Token dual authentication
- **Image Storage**: Cloudinary (production) / Local (development)
- **Email**: SendGrid for invitation emails
- **Containerization**: Docker & Docker Compose
- **Testing**: 100% coverage with 74 comprehensive tests

### **Production Deployment**

```bash
# Build production image
docker build -f Dockerfile -t motomundo:latest .

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data
docker-compose exec web python manage.py load_test_data
```

### **Production Considerations**

- Environment variables for secrets
- HTTPS configuration for JWT security
- Database backups and migrations
- Redis caching for performance
- Rate limiting for API endpoints
- CDN for static files and media
- Load balancing for high availability
- Monitoring and logging setup

## 🤝 Contributing

This project follows standard Django development practices:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

### **Code Quality Standards**

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document new API endpoints
- Use type hints where applicable
- Follow Django best practices

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏁 Status

✅ **Production Ready**  
📊 **100% Test Coverage** (74/74 tests passing)  
🔒 **Security Validated**  
📱 **API Complete**  
🐳 **Docker Optimized**  
🏆 **Achievement System Integrated**  
📧 **Invitation System Active**  
☁️ **Cloud Storage Ready**

---

_Built with ❤️ for the motorcycle community by riders, for riders._

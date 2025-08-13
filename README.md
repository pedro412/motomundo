# Motomundo

Django project for managing motorcycle clubs, chapters, and members with a comprehensive permission system.

## Features

- **Club Management**: Create and manage motorcycle clubs
- **Chapter Management**: Organize clubs into geographical or interest-based chapters  
- **Member Management**: Track club and chapter members with roles
- **Hierarchical Permissions**: Role-based access control system
- **REST API**: Full CRUD operations via Django REST Framework
- **Admin Interface**: Web-based administration panel

## Permission System

### User Roles

1. **SuperUser**: Full system access
2. **Club Admin**: Can manage specific clubs and all their chapters/members
3. **Chapter Manager**: Can only manage members within specific chapters
4. **Regular User**: Read-only access (when authenticated)

### Permission Hierarchy

```
SuperUser
├── Can manage all clubs, chapters, and members
├── Can create Club Admins
└── Can create Chapter Managers

Club Admin (for specific club)
├── Can manage their club's chapters and members
├── Can create new chapters for their club
├── Can create Chapter Managers for their club's chapters
└── Cannot access other clubs

Chapter Manager (for specific chapter)
├── Can add/edit/delete members in their chapter only
├── Cannot create chapters
└── Cannot access other chapters

Regular User
└── Read-only access to all data (when authenticated)
```

## Quick Start

### 1. Build and start the services:
```bash
docker-compose up --build
```

### 2. Load test data:
```bash
docker-compose exec web python manage.py load_test_data
```

### 3. Access the application:
- **Web App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

### 4. Test User Credentials:
- **Superuser**: admin / admin123
- **Harley Admin**: harley_admin / testpass123  
- **Chapter Manager**: sf_manager / testpass123
- **BMW Admin**: bmw_admin / testpass123

## API Endpoints

### Core Data Management
- `GET/POST/PUT/DELETE /api/clubs/` - Club management
- `GET/POST/PUT/DELETE /api/chapters/` - Chapter management
- `GET/POST/PUT/DELETE /api/members/` - Member management

### Permission Management
- `GET/POST/PUT/DELETE /api/club-admins/` - Club admin roles (SuperUsers only)
- `GET/POST/PUT/DELETE /api/chapter-managers/` - Chapter manager roles

### Features
- **Filtering**: Filter by various fields (club, chapter, role, etc.)
- **Search**: Text search across relevant fields
- **Ordering**: Sort by multiple fields
- **Pagination**: 20 items per page

## Development

### Run Tests
```bash
# Run all tests
docker-compose exec web python manage.py test

# Run with coverage
docker-compose exec web python manage.py test clubs.tests -v 2
```

### Create Test Users
```bash
# Create a club admin
docker-compose exec web python manage.py setup_permissions \
  --create-club-admin --username john_doe --club-id 1

# Create a chapter manager  
docker-compose exec web python manage.py setup_permissions \
  --create-chapter-manager --username jane_smith --chapter-id 1
```

### Reset Test Data
```bash
docker-compose exec web python manage.py load_test_data --reset
```

## Database Schema

### Core Models
- **Club**: Basic club information (name, description, logo, website)
- **Chapter**: Club subdivisions (belongs to a club)
- **Member**: Individual members (belongs to a chapter, has role)

### Permission Models  
- **ClubAdmin**: Links users to clubs they can administrate
- **ChapterManager**: Links users to chapters they can manage

### Relationships
```
Club (1) -> (N) Chapter (1) -> (N) Member
User (1) -> (N) ClubAdmin -> (1) Club  
User (1) -> (N) ChapterManager -> (1) Chapter
```

## Test Data

The system includes comprehensive test data:
- **3 Clubs**: Harley Riders United, BMW Motorrad Club, Ducati Riders Club
- **5 Chapters**: Distributed across the clubs
- **6 Members**: Various roles across chapters
- **3 Permission Assignments**: Demonstrating the role system

## Security

- **Authentication Required**: All write operations require login
- **Data Isolation**: Users only see data they have permissions for
- **Hierarchical Access**: Club Admins inherit Chapter Manager permissions
- **Audit Trail**: Permission assignments track creation details
- **Input Validation**: Proper validation prevents unauthorized access

## Technology Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis 7  
- **Containerization**: Docker & Docker Compose
- **Authentication**: Django's built-in auth system
- **API Documentation**: Django REST Framework browsable API

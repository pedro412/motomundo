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
3. **Chapter Admin**: Can only manage members within specific chapters
4. **Member**: Limited access to their own club/chapter data
5. **Public User**: Read-only access to public information

### Multi-Club Membership Support

The system now supports users having memberships in multiple clubs with different roles:
- A user can be a **Club Admin** in one club and a **Member** in another
- Each membership has its own role, club context, and optional chapter assignment
- Users can switch between their active club contexts
- Permission boundaries are strictly enforced between clubs

### Role Permissions Matrix

| **Action**                                 | **Club Admin**                 | **Chapter Admin**      | **Member** | **Public User** |
| ------------------------------------------ | ------------------------------ | ---------------------- | ---------- | --------------- |
| **View all clubs**                         | ✅                              | ✅                      | ✅          | ✅               |
| **View chapters of any club**              | ✅                              | ✅                      | ✅          | ✅               |
| **View public member list of any chapter** | ✅                              | ✅                      | ✅          | ✅               |
| **Create a new club**                      | ✅ (for their own account)      | ❌                      | ❌          | ❌               |
| **Edit club details**                      | ✅ (only their club)            | ❌                      | ❌          | ❌               |
| **Delete club**                            | ✅ (only their club)            | ❌                      | ❌          | ❌               |
| **Create a new chapter**                   | ✅ (only in their club)         | ❌                      | ❌          | ❌               |
| **Edit chapter details**                   | ✅ (all chapters in their club) | ✅ (only their chapter) | ❌          | ❌               |
| **Delete chapter**                         | ✅ (all chapters in their club) | ❌                      | ❌          | ❌               |
| **Invite Chapter Admin**                   | ✅                              | ❌                      | ❌          | ❌               |
| **Remove Chapter Admin**                   | ✅                              | ❌                      | ❌          | ❌               |
| **Add members to a chapter**               | ✅ (any chapter in their club)  | ✅ (only their chapter) | ❌          | ❌               |
| **Remove members from a chapter**          | ✅ (any chapter in their club)  | ✅ (only their chapter) | ❌          | ❌               |
| **Edit member details**                    | ✅ (any chapter in their club)  | ✅ (only their chapter) | ❌          | ❌               |
| **View private club/member data**          | ✅ (only their club)            | ✅ (only their chapter) | ❌          | ❌               |
| **Belong to multiple clubs**               | ✅                              | ✅                      | ✅          | N/A             |
| **Switch active club context**             | ✅                              | ✅                      | ✅          | N/A             |

### Permission Hierarchy

```
SuperUser
├── Can manage all clubs, chapters, and members
├── Can create Club Admins
└── Can create Chapter Admins

Club Admin (for specific club)
├── Can manage their club's chapters and members
├── Can create new chapters for their club
├── Can assign other Club Admins for their club
├── Can create Chapter Admins for their club's chapters
├── Can have memberships in multiple clubs
└── Cannot access other clubs they don't administrate

Chapter Admin (for specific chapter)
├── Can add/edit/delete members in their chapter only
├── Cannot create chapters
├── Cannot assign Chapter Admins
├── Can have memberships in multiple clubs
└── Cannot access other chapters they don't administrate

Member
├── Can view their own club/chapter information
├── Can have memberships in multiple clubs
├── Can switch between their club contexts
└── Read-only access to public data

Public User
└── Read-only access to public club and chapter information
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
- **Chapter Admin**: sf_manager / testpass123
- **BMW Admin**: bmw_admin / testpass123

## API Endpoints

### Authentication

#### Token Authentication (Legacy)
- `POST /api/auth/register/` - User registration (returns token)
- `POST /api/auth/login/` - User login (returns token)
- `POST /api/auth/logout/` - User logout (invalidates token)
- `GET/PUT /api/auth/profile/` - User profile management
- `PUT /api/auth/change-password/` - Change password
- `GET /api/auth/permissions/` - Get user roles and permissions

#### JWT Authentication (Recommended for React/SPA)
- `POST /api/auth/jwt/register/` - User registration (returns JWT tokens)
- `POST /api/auth/jwt/login/` - User login (returns JWT tokens)
- `POST /api/auth/jwt/refresh/` - Refresh access token
- `POST /api/auth/jwt/logout/` - Logout (blacklist refresh token)
- `POST /api/auth/jwt/logout-all/` - Logout from all devices

### Core Data Management
- `GET/POST/PUT/DELETE /api/clubs/` - Club management
- `GET/POST/PUT/DELETE /api/chapters/` - Chapter management
- `GET/POST/PUT/DELETE /api/members/` - Member management

### Permission Management
- `GET/POST/PUT/DELETE /api/club-admins/` - Club admin roles (SuperUsers only)
- `GET/POST/PUT/DELETE /api/chapter-admins/` - Chapter admin roles

### Features
- **Dual Authentication**: Token (legacy) and JWT (modern) authentication
- **User Registration**: Self-service account creation
- **Password Security**: Django's built-in password validation
- **Profile Management**: Update user information
- **Role-based Access**: Automatic permission filtering
- **Filtering**: Filter by various fields (club, chapter, role, etc.)
- **Search**: Text search across relevant fields
- **Ordering**: Sort by multiple fields
- **Pagination**: 20 items per page

## 🔐 JWT Authentication for Client Developers

### Overview

The Motomundo API supports JWT (JSON Web Token) authentication, providing a modern, stateless authentication system perfect for React, Vue, Angular, or mobile applications.

### Key Benefits
- **Stateless**: No server sessions required
- **Rich Responses**: Login includes user data and permissions
- **Secure**: Short-lived access tokens (15 minutes) with refresh capability
- **Role-aware**: Immediate access to user's clubs and chapters
- **Mobile-friendly**: Long-lived refresh tokens (7 days)

### Token Lifetimes
- **Access Token**: 15 minutes (for API requests)
- **Refresh Token**: 7 days (for getting new access tokens)

### Quick Start Guide

#### 1. User Registration
```javascript
const response = await fetch('/api/auth/jwt/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_rider',
    email: 'john@example.com',
    password: 'secure_password123',
    password_confirm: 'secure_password123',
    first_name: 'John',
    last_name: 'Rider'
  })
});

const data = await response.json();
// Returns: { access, refresh, user, permissions, message }
```

#### 2. User Login
```javascript
const response = await fetch('/api/auth/jwt/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'harley_admin',
    password: 'testpass123'
  })
});

const data = await response.json();
console.log(data);
```

**Sample Login Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "username": "harley_admin",
    "email": "harley@example.com",
    "first_name": "Harley",
    "last_name": "Admin"
  },
  "permissions": {
    "is_club_admin": true,
            "is_chapter_admin": false,
    "clubs": [
      {"id": 1, "name": "Harley Riders United"}
    ],
    "chapters": []
  }
}
```

#### 3. Making Authenticated API Requests
```javascript
const accessToken = localStorage.getItem('access_token');

const response = await fetch('/api/clubs/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

const clubs = await response.json();
```

#### 4. Token Refresh
```javascript
const refreshToken = localStorage.getItem('refresh_token');

const response = await fetch('/api/auth/jwt/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
});

if (response.ok) {
  const { access } = await response.json();
  localStorage.setItem('access_token', access);
} else {
  // Refresh token expired, redirect to login
  window.location.href = '/login';
}
```

#### 5. Logout
```javascript
const refreshToken = localStorage.getItem('refresh_token');
const accessToken = localStorage.getItem('access_token');

// Logout from current device
await fetch('/api/auth/jwt/logout/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({ refresh: refreshToken })
});

// Or logout from all devices
await fetch('/api/auth/jwt/logout-all/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json' 
  }
});

// Clear local storage
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

### React Authentication Hook Example

```javascript
import { useState, useEffect, createContext, useContext } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing tokens on app load
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (accessToken && refreshToken) {
      // Validate token or refresh if needed
      validateToken();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const response = await fetch('/api/auth/jwt/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      setUser(data.user);
      setPermissions(data.permissions);
      return true;
    }
    return false;
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    const accessToken = localStorage.getItem('access_token');

    if (refreshToken && accessToken) {
      await fetch('/api/auth/jwt/logout/', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({ refresh: refreshToken })
      });
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setPermissions(null);
  };

  const value = {
    user,
    permissions,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Permission-Based UI Rendering

```javascript
import { useAuth } from './AuthProvider';

const ClubManagement = () => {
  const { permissions } = useAuth();

  if (!permissions?.is_club_admin) {
    return <div>Access denied: Club admin required</div>;
  }

  return (
    <div>
      <h2>Manage Your Clubs</h2>
      {permissions.clubs.map(club => (
        <div key={club.id}>
          <h3>{club.name}</h3>
          {/* Club management UI */}
        </div>
      ))}
    </div>
  );
};

const ChapterManagement = () => {
  const { permissions } = useAuth();

  if (!permissions?.is_chapter_admin && !permissions?.is_club_admin) {
    return <div>Access denied: Chapter admin required</div>;
  }

  return (
    <div>
      <h2>Manage Chapters</h2>
      {permissions.chapters.map(chapter => (
        <div key={chapter.id}>
          <h3>{chapter.name} ({chapter.club.name})</h3>
          {/* Chapter management UI */}
        </div>
      ))}
    </div>
  );
};
```

### Error Handling

```javascript
const apiCall = async (url, options = {}) => {
  let accessToken = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  // Handle token expiration
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
      const refreshResponse = await fetch('/api/auth/jwt/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });

      if (refreshResponse.ok) {
        const { access } = await refreshResponse.json();
        localStorage.setItem('access_token', access);
        
        // Retry original request with new token
        return fetch(url, {
          ...options,
          headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json',
            ...options.headers
          }
        });
      } else {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
  }

  return response;
};
```

### Testing Your Integration

Use the test credentials to verify your JWT implementation:

- **Club Admin**: `harley_admin` / `testpass123`
- **Chapter Admin**: `sf_manager` / `testpass123`
- **BMW Admin**: `bmw_admin` / `testpass123`

### Troubleshooting

1. **Token Expired**: Implement automatic refresh logic
2. **CORS Issues**: Configure allowed origins in Django settings
3. **Permission Denied**: Check user roles in the `permissions` response
4. **Invalid Token**: Clear local storage and redirect to login

The JWT system provides everything needed for a modern, secure client application with role-based access control!

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

# Create a chapter admin  
docker-compose exec web python manage.py setup_permissions \
  --create-chapter-admin --username jane_smith --chapter-id 1
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
- **ChapterAdmin**: Links users to chapters they can manage

### Relationships
```
Club (1) -> (N) Chapter (1) -> (N) Member
User (1) -> (N) ClubAdmin -> (1) Club  
User (1) -> (N) ChapterAdmin -> (1) Chapter
User (1) -> (N) Member -> (1) Chapter
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
- **Hierarchical Access**: Club Admins inherit Chapter Admin permissions
- **Multi-Club Support**: Users can have different roles across multiple clubs
- **Audit Trail**: Permission assignments track creation details
- **Input Validation**: Proper validation prevents unauthorized access

## Technology Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis 7  
- **Containerization**: Docker & Docker Compose
- **Authentication**: Django's built-in auth system
- **API Documentation**: Django REST Framework browsable API

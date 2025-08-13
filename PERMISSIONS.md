# Permission System Documentation

## Overview

The Motomundo application now implements a hierarchical permission system with two main user roles:

1. **Club Admins**: Can manage a specific club and all its chapters and members
2. **Chapter Managers**: Can only manage members within their specific chapter

## User Roles

### SuperUser (Django Admin)
- Full access to everything
- Can create and manage Club Admins
- Can create and manage Chapter Managers
- Can create and manage all clubs, chapters, and members

### Club Admin
- Can create new chapters for their assigned club(s)
- Can manage all members across all chapters within their club(s)
- Can create Chapter Managers for chapters within their club(s)
- Cannot create or manage other clubs

### Chapter Manager
- Can only add and manage members within their assigned chapter(s)
- Cannot create chapters
- Cannot manage other chapters or clubs

### Regular User
- Read-only access to all data (if authenticated)
- No write permissions

## API Endpoints

### Core Entities
- `GET/POST/PUT/DELETE /api/clubs/` - Club management (Club Admins + SuperUsers)
- `GET/POST/PUT/DELETE /api/chapters/` - Chapter management (Club Admins + SuperUsers)
- `GET/POST/PUT/DELETE /api/members/` - Member management (Club Admins + Chapter Managers + SuperUsers)

### Permission Management
- `GET/POST/PUT/DELETE /api/club-admins/` - Manage club admin roles (SuperUsers only)
- `GET/POST/PUT/DELETE /api/chapter-managers/` - Manage chapter manager roles (Club Admins + SuperUsers)

## Setting Up Permissions

### 1. Create a Club Admin
```bash
# Using Django admin interface (recommended)
# Go to /admin/ and create a ClubAdmin object

# Or using management command:
python manage.py setup_permissions --create-club-admin --username john_doe --club-id 1
```

### 2. Create a Chapter Manager
```bash
# Using Django admin interface (recommended)
# Go to /admin/ and create a ChapterManager object

# Or using management command:
python manage.py setup_permissions --create-chapter-manager --username jane_smith --chapter-id 1
```

## Usage Examples

### Club Admin Workflow
1. Club Admin logs in
2. Can see only clubs they manage in `/api/clubs/`
3. Can create new chapters for their clubs via `/api/chapters/`
4. Can view all chapters within their clubs
5. Can add/edit members in any chapter within their clubs
6. Can assign Chapter Managers to chapters within their clubs

### Chapter Manager Workflow
1. Chapter Manager logs in
2. Can see only chapters they manage in `/api/chapters/` (read-only)
3. Can view only members from their assigned chapters in `/api/members/`
4. Can add/edit members only within their assigned chapters
5. Cannot create chapters or manage other chapters

## Data Isolation

The system ensures proper data isolation:

- **Club Admins** only see data related to their assigned clubs
- **Chapter Managers** only see data related to their assigned chapters
- **API endpoints** automatically filter data based on user permissions
- **Database queries** are optimized with proper select_related() to prevent N+1 queries

## Security Features

1. **Authentication Required**: All write operations require authentication
2. **Role-Based Access**: Users can only access data they have permissions for
3. **Hierarchical Permissions**: Club Admins inherit all Chapter Manager permissions for their clubs
4. **Audit Trail**: All permission assignments track who created them and when
5. **Input Validation**: Proper validation prevents users from accessing unauthorized data

## Admin Interface

The Django admin interface provides easy management of:
- Club Admin assignments
- Chapter Manager assignments
- All with proper filtering and search capabilities

Navigate to `/admin/` to manage permissions through the web interface.

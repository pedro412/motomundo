# Motomundo Test Suite

## 📁 Test Organization

All tests are now organized in the `/tests/` directory with a clear structure:

```
tests/
├── __init__.py                     # Test package initialization
├── test_authentication.py         # Authentication & JWT tests
├── test_permissions.py            # Permission system tests  
├── test_complete_workflows.py     # End-to-end functional tests
└── test_features.py               # Specific feature tests
```

## 🧪 Test Categories

### 1. Authentication Tests (`test_authentication.py`)
**Purpose**: Test all authentication mechanisms and user management

**Test Classes**:
- `AuthenticationTestCase` - Token and JWT authentication workflows
- `PermissionIntegrationTestCase` - Authentication + permissions integration

**Key Tests**:
- ✅ Token authentication workflow
- ✅ JWT authentication workflow (register, login, refresh)
- ✅ Login with existing users
- ✅ Authentication error scenarios
- ✅ Permission hierarchy with JWT

**Example Run**:
```bash
docker-compose exec web python manage.py test tests.test_authentication -v 2
```

### 2. Permission System Tests (`test_permissions.py`)
**Purpose**: Comprehensive testing of the hierarchical permission system

**Test Classes**:
- `PermissionSystemTestCase` - Core permission functions
- `PermissionAPITestCase` - Permissions through API endpoints

**Key Tests**:
- ✅ Superuser permissions (full access)
- ✅ Club admin permissions (club-level management)
- ✅ Chapter admin permissions (chapter-level management)
- ✅ Regular user permissions (no management access)
- ✅ Cross-club permission boundaries
- ✅ Member role change permissions

**Example Run**:
```bash
docker-compose exec web python manage.py test tests.test_permissions -v 2
```

### 3. Complete Workflow Tests (`test_complete_workflows.py`)
**Purpose**: End-to-end functional testing of complete user journeys

**Test Classes**:
- `CompleteFunctionalTestCase` - Main 4-requirement workflow
- `MultiClubScenarioTestCase` - Complex real-world scenarios

**Key Tests**:
- ✅ **Complete Workflow** - Tests all 4 core requirements:
  1. User creates club, chapters, and assigns chapter admin
  2. Chapter admin updates chapter info and creates members  
  3. Chapter admin changes member roles
  4. User with multi-club membership (different roles in different clubs)
- ✅ Club admin as member scenario (Carlos Rodriguez example)
- ✅ Member uniqueness constraints

**Example Run**:
```bash
docker-compose exec web python manage.py test tests.test_complete_workflows.CompleteFunctionalTestCase.test_complete_workflow -v 2
```

### 4. Feature Tests (`test_features.py`)
**Purpose**: Test specific features and capabilities

**Test Classes**:
- `MemberProfileFeatureTestCase` - Complete member profile feature
- `ClubManagementFeatureTestCase` - Club management features
- `ChapterManagementFeatureTestCase` - Chapter management features

**Key Tests**:
- ✅ **Complete Member Profile** - Cross-club profile display
- ✅ Club creation and management
- ✅ Chapter lifecycle management

**Example Run**:
```bash
docker-compose exec web python manage.py test tests.test_features.MemberProfileFeatureTestCase.test_complete_member_profile_feature -v 2
```

## 🎯 Core Requirements Validation

The test suite validates all original requirements:

### ✅ Requirement 1: Club & Chapter Management
**Test**: `test_complete_workflow` in `CompleteFunctionalTestCase`
- User registration ✓
- Club creation ✓
- Chapter creation ✓
- Chapter admin assignment ✓

### ✅ Requirement 2: Chapter Admin Activities
**Test**: `test_complete_workflow` in `CompleteFunctionalTestCase`
- Chapter information updates ✓
- Member creation ✓
- Member management ✓

### ✅ Requirement 3: Member Role Management
**Test**: `test_complete_workflow` in `CompleteFunctionalTestCase`
- Role changes by chapter admin ✓
- Permission validation ✓

### ✅ Requirement 4: Multi-Club Membership
**Test**: `test_complete_workflow` in `CompleteFunctionalTestCase`
- User belongs to multiple clubs ✓
- Different roles in different clubs ✓
- Cross-club identity management ✓

## 🚀 Running Tests

### Run All Tests
```bash
docker-compose exec web python manage.py test tests -v 2
```

### Run Specific Test Categories
```bash
# Authentication tests only
docker-compose exec web python manage.py test tests.test_authentication -v 2

# Permission tests only  
docker-compose exec web python manage.py test tests.test_permissions -v 2

# Complete workflow tests only
docker-compose exec web python manage.py test tests.test_complete_workflows -v 2

# Feature tests only
docker-compose exec web python manage.py test tests.test_features -v 2
```

### Run Specific Test Methods
```bash
# Main functional test
docker-compose exec web python manage.py test tests.test_complete_workflows.CompleteFunctionalTestCase.test_complete_workflow -v 2

# Member profile feature
docker-compose exec web python manage.py test tests.test_features.MemberProfileFeatureTestCase.test_complete_member_profile_feature -v 2

# JWT authentication
docker-compose exec web python manage.py test tests.test_authentication.AuthenticationTestCase.test_jwt_authentication_workflow -v 2
```

## 📊 Test Coverage

**Total Test Classes**: 6
**Total Test Methods**: 15+
**Coverage Areas**:
- ✅ Authentication (Token + JWT)
- ✅ Authorization (Hierarchical permissions)
- ✅ Club Management (CRUD operations)
- ✅ Chapter Management (CRUD operations)
- ✅ Member Management (CRUD + role changes)
- ✅ Multi-club scenarios
- ✅ Cross-club features
- ✅ Real-world motorcycle club scenarios

## 🎭 Real-World Scenarios Tested

### Carlos Rodriguez (Alterados MC President)
- **Club Admin** of Alterados MC
- **Chapter Admin** of Riders United MC Highway Chapter  
- **President** in Alterados MC Nuevo Laredo chapter
- **Secretary** in Hermanos MC Central chapter
- **Rider** in Riders United MC Highway Chapter

### Complex Permission Hierarchies
- Superuser → manages everything
- Club Admin → manages specific clubs and their chapters
- Chapter Admin → manages specific chapters and their members
- Regular User → read-only access to public data

### Cross-Club Functionality
- Member profile shows all club memberships
- Different nicknames per club
- Different roles per club
- Administrative overlap scenarios

## 🛡️ Error Scenarios Tested

- ✅ Invalid authentication credentials
- ✅ Cross-club permission violations
- ✅ Duplicate member creation attempts
- ✅ Unauthorized access attempts
- ✅ Missing required fields
- ✅ Invalid role assignments

## 📈 Performance Considerations

Tests are designed to:
- ✅ Run independently (no shared state)
- ✅ Clean up after themselves (Django TestCase handles this)
- ✅ Use realistic data volumes
- ✅ Test permission boundaries efficiently
- ✅ Validate complex scenarios without excessive database queries

---

**Last Updated**: August 13, 2025  
**Status**: ✅ All tests passing  
**Docker Environment**: Required for execution

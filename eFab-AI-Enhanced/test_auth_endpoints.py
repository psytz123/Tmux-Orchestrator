"""
Integration test for authentication endpoints
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile

from src.api.app import app
from src.database.connection import get_db, Base
from src.database.models.user import User


# Test database setup
async def create_test_db():
    """Create in-memory test database"""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine


async def get_test_db():
    """Test database dependency override"""
    engine = await create_test_db()
    TestSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def test_auth_endpoints():
    """Test authentication endpoints using TestClient"""
    print("🧪 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Override database dependency
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as client:
        # Test user registration
        print("Testing user registration...")
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpassword123"
        }
        
        # Register user
        response = client.post("/api/v1/auth/register", json=user_data)
        
        if response.status_code != 201:
            print(f"Registration failed: {response.status_code} - {response.text}")
            return False
        
        user_response = response.json()
        print(f"✅ User registered: {user_response['username']}")
        
        # Test login
        print("Testing user login...")
        
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} - {response.text}")
            return False
            
        token_response = response.json()
        access_token = token_response["access_token"]
        refresh_token = token_response["refresh_token"]
        
        print("✅ User logged in successfully")
        print(f"Access token: {access_token[:50]}...")
        
        # Test protected endpoint
        print("Testing protected endpoint...")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        if response.status_code != 200:
            print(f"Protected endpoint failed: {response.status_code} - {response.text}")
            return False
            
        me_response = response.json()
        print(f"✅ Protected endpoint works: {me_response['username']}")
        
        # Test token validation
        print("Testing token validation...")
        
        response = client.get("/api/v1/auth/validate", headers=headers)
        
        if response.status_code != 200:
            print(f"Token validation failed: {response.status_code} - {response.text}")
            return False
            
        validation_response = response.json()
        print(f"✅ Token validation works: {validation_response['valid']}")
        
        # Test token refresh
        print("Testing token refresh...")
        
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        if response.status_code != 200:
            print(f"Token refresh failed: {response.status_code} - {response.text}")
            return False
            
        new_token_response = response.json()
        new_access_token = new_token_response["access_token"]
        
        print("✅ Token refresh works")
        print(f"New access token: {new_access_token[:50]}...")
        
        # Test invalid credentials
        print("Testing invalid credentials...")
        
        invalid_login = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=invalid_login)
        
        if response.status_code != 401:
            print(f"Invalid credentials should fail: {response.status_code}")
            return False
            
        print("✅ Invalid credentials correctly rejected")
        
        # Test duplicate registration
        print("Testing duplicate registration...")
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        if response.status_code != 400:
            print(f"Duplicate registration should fail: {response.status_code}")
            return False
            
        print("✅ Duplicate registration correctly rejected")
        
        return True


if __name__ == "__main__":
    try:
        success = test_auth_endpoints()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 All authentication endpoint tests passed!")
            print("✅ JWT authentication system is fully functional")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
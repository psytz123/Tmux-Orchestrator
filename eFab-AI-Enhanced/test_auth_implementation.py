"""
Test script to verify JWT authentication implementation
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timezone
import uuid

# Test the core auth utilities
from src.core.auth import (
    hash_password,
    verify_password, 
    create_access_token,
    create_refresh_token,
    verify_token,
    create_token_pair,
    refresh_access_token
)

def test_password_hashing():
    """Test password hashing and verification"""
    print("Testing password hashing...")
    
    password = "test_password_123"
    hashed = hash_password(password)
    
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed[:50]}...")
    
    # Test verification
    assert verify_password(password, hashed), "Password verification failed"
    assert not verify_password("wrong_password", hashed), "Wrong password should fail"
    
    print("✅ Password hashing tests passed")


def test_jwt_tokens():
    """Test JWT token creation and verification"""
    print("\nTesting JWT tokens...")
    
    user_data = {
        "sub": str(uuid.uuid4()),
        "username": "testuser",
        "email": "test@example.com"
    }
    
    # Test access token
    access_token = create_access_token(user_data)
    print(f"Access token created: {access_token[:50]}...")
    
    # Verify access token
    payload = verify_token(access_token, "access")
    assert payload is not None, "Access token verification failed"
    assert payload["username"] == "testuser", "Token payload incorrect"
    assert payload["type"] == "access", "Token type incorrect"
    
    # Test refresh token
    refresh_token = create_refresh_token(user_data)
    print(f"Refresh token created: {refresh_token[:50]}...")
    
    # Verify refresh token
    refresh_payload = verify_token(refresh_token, "refresh")
    assert refresh_payload is not None, "Refresh token verification failed"
    assert refresh_payload["type"] == "refresh", "Refresh token type incorrect"
    
    print("✅ JWT token tests passed")


def test_token_pair():
    """Test token pair creation"""
    print("\nTesting token pair creation...")
    
    user_id = str(uuid.uuid4())
    username = "testuser"
    email = "test@example.com"
    
    tokens = create_token_pair(user_id, username, email)
    
    assert "access_token" in tokens, "Missing access token"
    assert "refresh_token" in tokens, "Missing refresh token"
    assert tokens["token_type"] == "bearer", "Incorrect token type"
    
    # Verify both tokens
    access_payload = verify_token(tokens["access_token"], "access")
    refresh_payload = verify_token(tokens["refresh_token"], "refresh")
    
    assert access_payload["sub"] == user_id, "Access token user ID mismatch"
    assert refresh_payload["sub"] == user_id, "Refresh token user ID mismatch"
    
    print("✅ Token pair tests passed")


def test_token_refresh():
    """Test token refresh functionality"""
    print("\nTesting token refresh...")
    
    user_data = {
        "sub": str(uuid.uuid4()),
        "username": "testuser", 
        "email": "test@example.com"
    }
    
    refresh_token = create_refresh_token(user_data)
    new_access_token = refresh_access_token(refresh_token)
    
    assert new_access_token is not None, "Token refresh failed"
    
    # Verify new token
    payload = verify_token(new_access_token, "access")
    assert payload["sub"] == user_data["sub"], "Refreshed token user ID mismatch"
    
    print("✅ Token refresh tests passed")


def test_invalid_tokens():
    """Test invalid token handling"""
    print("\nTesting invalid token handling...")
    
    # Test invalid token
    invalid_token = "invalid.token.here"
    payload = verify_token(invalid_token)
    assert payload is None, "Invalid token should return None"
    
    # Test wrong token type
    access_token = create_access_token({"sub": "123"})
    payload = verify_token(access_token, "refresh")  # Wrong type
    assert payload is None, "Wrong token type should return None"
    
    print("✅ Invalid token tests passed")


if __name__ == "__main__":
    print("🧪 Testing JWT Authentication Implementation")
    print("=" * 50)
    
    try:
        test_password_hashing()
        test_jwt_tokens()
        test_token_pair()
        test_token_refresh()
        test_invalid_tokens()
        
        print("\n" + "=" * 50)
        print("🎉 All authentication tests passed!")
        print("✅ JWT implementation is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
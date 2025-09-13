#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for Railway deployment
"""
import secrets
import string

def generate_secret_key(length=64):
    """Generate a cryptographically secure random string"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_url_safe_key(length=32):
    """Generate a URL-safe base64 encoded key"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("🔐 SECRET_KEY Generation")
    print("=" * 50)
    
    print("\n1. URL-Safe Key (Recommended):")
    url_safe_key = generate_url_safe_key(32)
    print(f"SECRET_KEY={url_safe_key}")
    
    print("\n2. Complex Key (Alternative):")
    complex_key = generate_secret_key(64)
    print(f"SECRET_KEY={complex_key}")
    
    print("\n📋 Copy one of the above keys to use in Railway!")
    print("\n⚠️  Keep this key secret and never commit it to git!")
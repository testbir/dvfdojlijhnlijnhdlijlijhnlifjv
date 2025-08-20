# id_service/utils/validators.py

import re
import secrets
import string
from typing import Optional, Tuple, List
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse

from core.config import settings


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        try:
            # Validate and normalize
            validation = validate_email(email)
            return True, validation.email.lower()
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username
        - 3-30 characters
        - Alphanumeric, underscore, hyphen
        - Must start with letter
        """
        if not username:
            return False, "Username is required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 30:
            return False, "Username must be at most 30 characters"
        
        if not username[0].isalpha():
            return False, "Username must start with a letter"
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
            return False, "Username can only contain letters, numbers, underscore and hyphen"
        
        # Check for reserved usernames
        reserved = ['admin', 'root', 'api', 'oauth', 'oidc', 'auth', 'account', 'id', 'login', 'register']
        if username.lower() in reserved:
            return False, "This username is reserved"
        
        return True, ""
    
    @staticmethod
    def validate_redirect_uri(uri: str, allowed_uris: List[str]) -> bool:
        """
        Validate redirect URI against whitelist
        Exact match required for security
        """
        if not uri or not allowed_uris:
            return False
        
        # Exact match required
        return uri in allowed_uris
    
    @staticmethod
    def validate_scope(scope: str) -> Tuple[bool, str]:
        """Validate OAuth2 scope"""
        if not scope:
            return False, "Scope is required"
        
        allowed_scopes = ["openid", "email", "profile", "offline_access"]
        requested_scopes = scope.split()
        
        for s in requested_scopes:
            if s not in allowed_scopes:
                return False, f"Invalid scope: {s}"
        
        return True, ""
    
    @staticmethod
    def validate_pkce_verifier(verifier: str) -> Tuple[bool, str]:
        """
        Validate PKCE code verifier
        - 43-128 characters
        - URL-safe characters only
        """
        if not verifier:
            return False, "Code verifier is required"
        
        if len(verifier) < 43:
            return False, "Code verifier too short (min 43 characters)"
        
        if len(verifier) > 128:
            return False, "Code verifier too long (max 128 characters)"
        
        # Check characters (RFC 7636)
        allowed = string.ascii_letters + string.digits + '-._~'
        if not all(c in allowed for c in verifier):
            return False, "Code verifier contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_state(state: str) -> Tuple[bool, str]:
        """Validate OAuth2 state parameter"""
        if not state:
            return True, ""  # State is optional
        
        if len(state) > 500:
            return False, "State parameter too long"
        
        # Check for potentially malicious content
        if '<' in state or '>' in state or 'javascript:' in state.lower():
            return False, "Invalid state parameter"
        
        return True, ""
    
    @staticmethod
    def validate_nonce(nonce: str) -> Tuple[bool, str]:
        """Validate OIDC nonce parameter"""
        if not nonce:
            return True, ""  # Nonce is optional
        
        if len(nonce) > 255:
            return False, "Nonce too long"
        
        # Should be unguessable
        if len(nonce) < 8:
            return False, "Nonce too short for security"
        
        return True, ""
    
    @staticmethod
    def sanitize_user_agent(user_agent: Optional[str]) -> str:
        """Sanitize user agent string for storage"""
        if not user_agent:
            return ""
        
        # Truncate if too long
        if len(user_agent) > 500:
            user_agent = user_agent[:500]
        
        # Remove any control characters
        return ''.join(c for c in user_agent if c.isprintable())
    
    @staticmethod
    def is_safe_url(url: str, allowed_hosts: Optional[List[str]] = None) -> bool:
        """Check if URL is safe for redirect"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            
            # Reject URLs with potentially dangerous schemes
            if parsed.scheme and parsed.scheme not in ['http', 'https']:
                return False
            
            # If no host specified, it's a relative URL (safe)
            if not parsed.netloc:
                return True
            
            # Check against allowed hosts if provided
            if allowed_hosts:
                return parsed.netloc in allowed_hosts
            
            return True
            
        except Exception:
            return False


validators = Validators()
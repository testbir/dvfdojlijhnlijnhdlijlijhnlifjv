# auth_service/accounts/throttles.py

from rest_framework.throttling import AnonRateThrottle

class LoginIPThrottle(AnonRateThrottle):
    scope = 'login_ip'

class LoginEmailThrottle(AnonRateThrottle):
    scope = 'login_email'
    
    def get_cache_key(self, request, view):
        email = request.data.get('email') or request.data.get('username')
        if email:
            return f"throttle_login_email_{email}"
        return None

class PasswordResetIPThrottle(AnonRateThrottle):
    scope = 'password_reset_ip'

class PasswordResetEmailThrottle(AnonRateThrottle):
    scope = 'password_reset_email'
    
    def get_cache_key(self, request, view):
        email = request.data.get('email')
        if email:
            return f"throttle_reset_email_{email}"
        return None

class RegisterIPThrottle(AnonRateThrottle):
    scope = 'register_ip'
from django.utils.deprecation import MiddlewareMixin
from django.http.request import HttpRequest
from django.conf import settings
from urllib.parse import urlparse

class PaletteAdminMiddleware(MiddlewareMixin):
    """
    Middleware that provides clickjacking protection while allowing safe iframe embedding
    for admin forms in modals when requests come from same-origin sources.
    
    Security features:
    - X-Frame-Options: SAMEORIGIN for same-origin iframes (safe for admin modals)
    - X-Frame-Options: DENY for all other requests (clickjacking protection)
    - Content-Security-Policy: frame-ancestors 'self' for modern browsers
    - Respects @xframe_options_exempt decorator for exceptions
    """
    
    def process_request(self, request: HttpRequest):
        """
        Determine if this is a same-origin request safe for iframe embedding.
        Checks HTTP_REFERER and HTTP_ORIGIN headers against ALLOWED_HOSTS.
        """
        # Check if explicitly exempt
        if getattr(request, 'xframe_options_exempt', False):
            return None
        
        # Get the origin of the request
        referer = request.META.get('HTTP_REFERER', '')
        origin = request.META.get('HTTP_ORIGIN', '')
        request_host = request.META.get('HTTP_HOST', '')
        
        # For iframe requests, check if origin matches allowed hosts or is same-origin
        is_same_origin = self._is_same_origin(request_host, referer, origin)
        
        request.is_palette_admin = is_same_origin
    
    @staticmethod
    def _is_same_origin(request_host, referer, origin):
        """
        Check if the request is from the same origin.
        Compares HTTP_REFERER/HTTP_ORIGIN host with request HTTP_HOST.
        """
        if not request_host:
            return False
        
        # Check HTTP_ORIGIN header (sent by browsers for cross-origin requests)
        if origin:
            try:
                origin_host = urlparse(origin).netloc.lower()
                request_host_lower = request_host.lower()
                # Remove port if comparing localhost
                origin_host_base = origin_host.split(':')[0]
                request_host_base = request_host_lower.split(':')[0]
                if origin_host_base == request_host_base:
                    return True
            except Exception:
                pass
        
        # Check HTTP_REFERER header (sent for iframe navigation)
        if referer:
            try:
                referer_host = urlparse(referer).netloc.lower()
                request_host_lower = request_host.lower()
                # Compare base hosts (without port for localhost)
                referer_host_base = referer_host.split(':')[0]
                request_host_base = request_host_lower.split(':')[0]
                if referer_host_base == request_host_base:
                    return True
            except Exception:
                pass
        
        # Check ALLOWED_HOSTS setting
        if request_host in settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS:
            return True
        
        return False
    
    def process_response(self, request, response):
        """
        Set appropriate clickjacking protection headers based on request origin.
        
        - SAMEORIGIN: Allows iframes from same origin (safe for modals)
        - DENY: Prevents all iframe embedding (prevents clickjacking)
        """
        # Don't override if already set
        if response.get('X-Frame-Options') is not None:
            return response
        
        # Don't override if marked as exempt
        if getattr(response, 'xframe_options_exempt', False):
            return response
        
        # Set appropriate header based on origin validation
        if getattr(request, 'is_palette_admin', False):
            # Same-origin request - safe for iframe embedding
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            # Also set CSP header for modern browsers (defense in depth)
            if 'Content-Security-Policy' not in response:
                response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        else:
            # Cross-origin or unknown origin - deny framing (clickjacking protection)
            response.headers['X-Frame-Options'] = 'DENY'
        
        return response
"""
Error tracking utilities with PostHog integration.
Provides decorators and utilities for automatic error tracking across all SDK functions.
"""

import os
import functools
import traceback
from typing import Optional, Dict, Any, Callable
import posthog
from .telemetry_config import get_telemetry_config, is_telemetry_enabled


class ErrorTracker:
    """Centralized error tracking with PostHog integration."""
    
    def __init__(self, api_key: Optional[str] = None, host: Optional[str] = None):
        self.enabled = False
        
        # Check if telemetry is enabled first
        if not is_telemetry_enabled():
            return
        
        # Get telemetry configuration
        config = get_telemetry_config()
        
        # Use provided parameters or config defaults
        self._api_key = api_key or config['token']
        self._host = host or config['endpoint']
        self._user_id = config['user_id']
        
        if self._api_key and config['enabled']:
            try:
                posthog.api_key = self._api_key
                posthog.host = self._host
                self.enabled = True
            except Exception:
                pass
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """Track an error with PostHog."""
        if not self.enabled:
            return
        
        try:
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'stack_trace': traceback.format_exc(),
            }
            
            if context:
                error_data.update(context)
            
            posthog.capture(
                distinct_id=self._user_id,
                event='SDK Error',
                properties=error_data
            )
        except Exception:
            pass
    
    def track_function_call(self, function_name: str, properties: Dict[str, Any] = None):
        """Track a successful function call."""
        if not self.enabled:
            return
        
        try:
            event_data = {
                'function_name': function_name,
                'sdk_version': 'python-client'
            }
            
            if properties:
                event_data.update(properties)
            
            posthog.capture(
                distinct_id=self._user_id,
                event='SDK Function Call',
                properties=event_data
            )
        except Exception:
            pass


# Global error tracker instance
_error_tracker = ErrorTracker()


def track_errors(function_name: Optional[str] = None, track_success: bool = False):
    """
    Decorator to automatically track errors and optionally successful calls.
    
    Args:
        function_name: Override the function name for tracking
        track_success: Whether to track successful function calls
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            actual_function_name = function_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                
                if track_success:
                    _error_tracker.track_function_call(
                        actual_function_name,
                        {'args_count': len(args), 'kwargs_count': len(kwargs)}
                    )
                
                return result
            except Exception as e:
                _error_tracker.track_error(
                    e, 
                    {
                        'function_name': actual_function_name,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            actual_function_name = function_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                
                if track_success:
                    _error_tracker.track_function_call(
                        actual_function_name,
                        {'args_count': len(args), 'kwargs_count': len(kwargs)}
                    )
                
                return result
            except Exception as e:
                _error_tracker.track_error(
                    e,
                    {
                        'function_name': actual_function_name,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                raise
        
        return async_wrapper if hasattr(func, '__await__') else wrapper
    
    return decorator


def configure_error_tracking(telemetry_token: Optional[str] = None, analytics_host: Optional[str] = None, tracking_id: Optional[str] = None):
    """Configure global error tracking settings."""
    global _error_tracker
    _error_tracker = ErrorTracker(telemetry_token, analytics_host)
    
    if tracking_id:
        _error_tracker._user_id = tracking_id


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance."""
    return _error_tracker
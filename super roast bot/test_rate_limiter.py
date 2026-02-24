"""
Unit tests for the sliding window rate limiter.
"""

import time
import pytest
from rate_limiter import RateLimiter

def test_rate_limiter_allows_requests_under_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    client = "test_client_1"
    
    # Should allow 3 requests
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is True
    
    # Fourth request should be blocked
    assert limiter.is_allowed(client) is False

def test_rate_limiter_wait_time():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    client = "test_client_2"
    
    # Initially 0 wait time
    assert limiter.get_wait_time(client) == 0.0
    
    limiter.is_allowed(client)
    assert limiter.get_wait_time(client) == 0.0
    
    limiter.is_allowed(client)
    
    # Now it should be blocked and wait time should be > 0 (close to 60)
    wait_time = limiter.get_wait_time(client)
    assert wait_time > 0.0
    assert wait_time <= 60.0

def test_rate_limiter_different_clients():
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    client1 = "test_client_3"
    client2 = "test_client_4"
    
    assert limiter.is_allowed(client1) is True
    assert limiter.is_allowed(client1) is False
    
    # Client 2 should be unaffected
    assert limiter.is_allowed(client2) is True
    assert limiter.is_allowed(client2) is False

def test_rate_limiter_window_expiration(monkeypatch):
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    client = "test_client_5"
    
    # Use real time and sleep since monkeypatching time.time can be tricky
    # with the RateLimiter calling it internally.
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is False
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should be allowed again
    assert limiter.is_allowed(client) is True

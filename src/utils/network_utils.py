"""
Network utilities for detecting internet connectivity and managing offline mode.
"""
import socket
import requests
from typing import Tuple


def check_internet_connection(timeout: int = 5) -> bool:
    """
    Check if internet connection is available.
    
    Args:
        timeout: Timeout in seconds for the connection test
        
    Returns:
        bool: True if internet is available, False otherwise
    """
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout)
        return True
    except OSError:
        pass
    
    try:
        # Fallback: Try HTTP request to a reliable service
        response = requests.get("https://www.google.com", timeout=timeout)
        return response.status_code == 200
    except (requests.RequestException, OSError):
        return False


def check_firebase_connectivity(timeout: int = 5) -> bool:
    """
    Check if Firebase services are accessible.
    
    Args:
        timeout: Timeout in seconds for the connection test
        
    Returns:
        bool: True if Firebase is accessible, False otherwise
    """
    try:
        response = requests.get("https://firebase.googleapis.com", timeout=timeout)
        return response.status_code in [200, 401, 403]  # Any response means connectivity
    except (requests.RequestException, OSError):
        return False


def get_network_status(timeout: int = 5) -> Tuple[bool, bool]:
    """
    Get comprehensive network status.
    
    Args:
        timeout: Timeout in seconds for connection tests
        
    Returns:
        Tuple[bool, bool]: (internet_available, firebase_available)
    """
    internet_available = check_internet_connection(timeout)
    firebase_available = check_firebase_connectivity(timeout) if internet_available else False
    
    return internet_available, firebase_available


def should_enable_offline_mode() -> bool:
    """
    Determine if offline mode should be enabled based on network status.
    
    Returns:
        bool: True if offline mode should be enabled
    """
    internet_available, firebase_available = get_network_status()
    
    # Enable offline mode if either internet or Firebase is unavailable
    return not (internet_available and firebase_available)
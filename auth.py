"""
Authentication module for AHP-SMART application
Handles Supabase authentication operations
"""

import streamlit as st
from st_supabase_connection import SupabaseConnection
from typing import Optional, Dict, Any


def get_supabase_client() -> SupabaseConnection:
    """
    Get or create Supabase connection instance
    
    Returns:
        SupabaseConnection: Supabase client instance
    """
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = st.connection(
            name="supabase_connection",
            type=SupabaseConnection,
            ttl=None,
        )
    return st.session_state.supabase_client


def initialize_auth_state():
    """Initialize authentication state in session"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "session" not in st.session_state:
        st.session_state.session = None


def _convert_to_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """
    Convert Pydantic model to dictionary
    
    Args:
        obj: Object to convert (can be Pydantic model or dict)
        
    Returns:
        Dictionary representation or None
    """
    if obj is None:
        return None
    
    # If already a dict, return as is
    if isinstance(obj, dict):
        return obj
    
    # Try to convert Pydantic model to dict
    try:
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
    except Exception:
        pass
    
    return None


def sign_in(email: str, password: str) -> tuple[bool, Optional[str]]:
    """
    Sign in user with email and password using Supabase
    
    Args:
        email: User email
        password: User password
        
    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    try:
        client = get_supabase_client()
        
        # Use cached sign in for better performance
        response = client.cached_sign_in_with_password(
            dict(email=email, password=password)
        )
        
        if response:
            # Convert response to dict
            response_dict = _convert_to_dict(response)
            
            # Extract user and session
            user = None
            session = None
            
            if hasattr(response, 'user'):
                user = _convert_to_dict(response.user)
            elif response_dict and 'user' in response_dict:
                user = response_dict['user']
            
            if hasattr(response, 'session'):
                session = _convert_to_dict(response.session)
            elif response_dict and 'session' in response_dict:
                session = response_dict['session']
            
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.session = session
                return True, None
            else:
                return False, "Invalid credentials"
        else:
            return False, "Invalid credentials"
            
    except Exception as e:
        error_msg = str(e)
        # Handle common error messages
        if "Invalid login credentials" in error_msg:
            return False, "Email atau password salah"
        elif "Email not confirmed" in error_msg:
            return False, "Email belum dikonfirmasi. Silakan cek email Anda."
        else:
            return False, f"Login gagal: {error_msg}"


def sign_up(email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None, auto_login: bool = True) -> tuple[bool, Optional[str]]:
    """
    Sign up new user with Supabase
    
    Args:
        email: User email
        password: User password
        user_metadata: Optional dictionary with additional user data (fname, lname, etc.)
        auto_login: If True, automatically login after successful registration
        
    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    try:
        client = get_supabase_client()
        
        signup_data = {
            'email': email,
            'password': password
        }
        
        if user_metadata:
            signup_data['options'] = {'data': user_metadata}
        
        response = client.auth.sign_up(signup_data)
        
        if response:
            # Convert response to dict
            response_dict = _convert_to_dict(response)
            
            # Check if user was created
            user = None
            session = None
            
            if hasattr(response, 'user'):
                user = _convert_to_dict(response.user)
            elif response_dict and 'user' in response_dict:
                user = response_dict['user']
            
            if hasattr(response, 'session'):
                session = _convert_to_dict(response.session)
            elif response_dict and 'session' in response_dict:
                session = response_dict['session']
            
            if user:
                # Auto login if enabled and session exists
                if auto_login and session:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.session = session
                
                return True, None
            else:
                return False, "Registrasi gagal"
        else:
            return False, "Registrasi gagal"
            
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return False, "Email sudah terdaftar"
        else:
            return False, f"Registrasi gagal: {error_msg}"


def sign_out() -> tuple[bool, Optional[str]]:
    """
    Sign out current user
    
    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    try:
        client = get_supabase_client()
        client.auth.sign_out()
        
        # Clear session state
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.session = None
        
        return True, None
        
    except Exception as e:
        return False, f"Logout gagal: {str(e)}"


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user
    
    Returns:
        Optional[Dict]: User data if authenticated, None otherwise
    """
    if st.session_state.get("logged_in") and st.session_state.get("user"):
        return st.session_state.user
    
    try:
        client = get_supabase_client()
        user_response = client.auth.get_user()
        
        if user_response:
            # Convert to dict
            user = None
            if hasattr(user_response, 'user'):
                user = _convert_to_dict(user_response.user)
            else:
                user = _convert_to_dict(user_response)
            
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                return user
            
    except Exception:
        pass
    
    return None


def get_current_session() -> Optional[Dict[str, Any]]:
    """
    Get current session
    
    Returns:
        Optional[Dict]: Session data if exists, None otherwise
    """
    if st.session_state.get("session"):
        return st.session_state.session
    
    try:
        client = get_supabase_client()
        session_response = client.auth.get_session()
        
        if session_response:
            session = _convert_to_dict(session_response)
            if session:
                st.session_state.session = session
                return session
            
    except Exception:
        pass
    
    return None


def is_authenticated() -> bool:
    """
    Check if user is authenticated
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    # First check session state
    if st.session_state.get("logged_in"):
        return True
    
    # Try to get current user from Supabase
    user = get_current_user()
    return user is not None


def require_auth():
    """
    Decorator/helper function to require authentication
    Redirects to login page if not authenticated
    """
    if not is_authenticated():
        st.warning("⚠️ Silakan login terlebih dahulu")
        st.stop()


def get_user_email() -> str:
    """
    Get current user's email
    
    Returns:
        str: User email or 'Guest' if not authenticated
    """
    user = get_current_user()
    if user and isinstance(user, dict):
        return user.get('email', 'Guest')
    return 'Guest'


def get_user_metadata(key: str, default: Any = None) -> Any:
    """
    Get specific user metadata field
    
    Args:
        key: Metadata key to retrieve
        default: Default value if key not found
        
    Returns:
        Metadata value or default
    """
    user = get_current_user()
    if user and isinstance(user, dict):
        user_metadata = user.get('user_metadata', {})
        if isinstance(user_metadata, dict):
            return user_metadata.get(key, default)
    return default

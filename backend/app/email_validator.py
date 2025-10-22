"""
Email validation utility to reject free email providers.
"""
from typing import Set

FREE_EMAIL_DOMAINS: Set[str] = {
    "gmail.com",
    "googlemail.com",
    
    "yahoo.com",
    "yahoo.com.au",
    "yahoo.co.uk",
    "yahoo.ca",
    "yahoo.co.in",
    "ymail.com",
    "rocketmail.com",
    
    "outlook.com",
    "outlook.com.au",
    "hotmail.com",
    "hotmail.com.au",
    "hotmail.co.uk",
    "live.com",
    "live.com.au",
    "msn.com",
    
    "aol.com",
    "aol.com.au",
    
    "icloud.com",
    "me.com",
    "mac.com",
    
    "protonmail.com",
    "proton.me",
    "pm.me",
    
    "mail.com",
    "gmx.com",
    "gmx.net",
    "zoho.com",
    "yandex.com",
    "fastmail.com",
    "tutanota.com",
    "tutamail.com",
    "mailinator.com",
    "guerrillamail.com",
    "temp-mail.org",
    "10minutemail.com",
    "throwaway.email",
}


def is_free_email(email: str) -> bool:
    """
    Check if an email address uses a free email provider domain.
    
    Args:
        email: The email address to check
        
    Returns:
        True if the email uses a free provider, False otherwise
    """
    if not email or "@" not in email:
        return False
    
    domain = email.split("@")[-1].lower()
    return domain in FREE_EMAIL_DOMAINS


def validate_business_email(email: str) -> str:
    """
    Validate that an email is a business email (not a free provider).
    
    Args:
        email: The email address to validate
        
    Returns:
        The email address if valid
        
    Raises:
        ValueError: If the email uses a free provider
    """
    if is_free_email(email):
        domain = email.split("@")[-1]
        raise ValueError(
            f"Please use a business email address. Free email providers like {domain} are not accepted."
        )
    return email

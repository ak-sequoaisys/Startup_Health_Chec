import re
from pathlib import Path
from typing import Set


class EmailValidator:
    def __init__(self):
        self.free_domains: Set[str] = self._load_free_domains()
    
    def _load_free_domains(self) -> Set[str]:
        config_path = Path(__file__).parent.parent / "config" / "free_email_domains.txt"
        free_domains = set()
        
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        free_domains.add(line.lower())
        except FileNotFoundError:
            pass
        
        return free_domains
    
    def validate_email_format(self, email: str) -> bool:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def is_free_email_domain(self, email: str) -> bool:
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        return domain in self.free_domains
    
    def validate_business_email(self, email: str) -> tuple[bool, str]:
        if not email:
            return False, "Email is required"
        
        if not self.validate_email_format(email):
            return False, "Invalid email format"
        
        if self.is_free_email_domain(email):
            return False, "We only accept business emails. Please use your work email."
        
        return True, ""


email_validator = EmailValidator()

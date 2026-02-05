def validate_rwandan_nid(nid_string: str) -> bool:
    """Strictly validates 16-digit Rwanda National ID starting with 1"""
    if nid_string is None:
        return False
        
    if len(nid_string) == 16 and nid_string.startswith("1") and nid_string.isdigit():
        return True
    return False

def validate_rwandan_phone(phone_string: str) -> bool:
    """Strictly validates +250 7XX XXX XXX format"""
    if phone_string is None:
        return False
        
    if phone_string.startswith("+250") and len(phone_string) == 13:
        return True
    return False
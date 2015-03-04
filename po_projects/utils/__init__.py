"""
Common various utilities
"""
def get_message_strings(message):
    """
    Given a message id/string from a Babel's Message instance, returns 
    splitted singular and plural
    
    Pretty simple, if it's a string it's only singular, if it's a tuple it's 
    a singular+plural
    """
    singular = plural = ''
    singular = message
    if isinstance(message, tuple):
        singular, plural = message
    
    return singular, plural


def join_message_strings(singular, plural='', pluralized=False):
    """
    @singular: singular message, required
    @plural: plural message, optional, only used if pluralized is True
    @pluralized: a optional boolean if True, force pluralized return
    """
    if pluralized:
        return singular, plural
    
    return singular

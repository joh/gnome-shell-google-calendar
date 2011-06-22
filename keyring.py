"""
Keyring storage of Google Calendar login credentials
"""
import gnomekeyring as gk

_keyring = 'login'
_display_name = 'GNOME Shell Google Calendar Account'
_attrs = { 'application': 'gnome-shell-google-calendar' }
_type = gk.ITEM_GENERIC_SECRET
_item_id = None


class KeyringError(Exception):
    pass


def get_item_id():
    global _item_id
    
    if _item_id:
        return _item_id
    
    try:
        results = gk.find_items_sync(gk.ITEM_GENERIC_SECRET, _attrs)
        _item_id = results[0].item_id
    except gk.NoMatchError:
        # Create item
        _item_id = gk.item_create_sync(_keyring, _type,
                                       _display_name, _attrs, '', True)
    return _item_id


def get_credentials():
    item_id = get_item_id()
    attrs = gk.item_get_attributes_sync(_keyring, item_id)
    
    if not 'email' in attrs:
        raise KeyringError('Login credentials not found')
    
    info = gk.item_get_info_sync(_keyring, item_id)
    
    return attrs['email'], info.get_secret()


def set_credentials(email, password):
    item_id = get_item_id()
    
    info = gk.ItemInfo()
    info.set_display_name(_display_name)
    info.set_type(_type)
    info.set_secret(password)
    gk.item_set_info_sync(_keyring, item_id, info)
    
    attrs = _attrs.copy()
    attrs['email'] = email
    gk.item_set_attributes_sync(_keyring, item_id, attrs)


if __name__ == '__main__':
    print 'item_id', get_item_id()
    #set_credentials('user@example.com', 'secret')
    print 'credentials', get_credentials()

def image_is_valid(image):
    """ Checks validity of image """
    try:
        imgname = image.name
    # images with an empty string are valid
    except AttributeError:
        return True

    # we are dealing with a proper file
    size = image.size
    endchars = imgname[-5:]
    # size must not surpass 2mb
    if ('.jpg' in endchars or '.jpeg' in endchars or '.png' in endchars) and size < 2100000:
        return True
    else:
        return False


def name_is_valid(name):
    """ checks validity of name """
    if len(name) > 0:
        return True
    else:
        return False


def price_is_valid(price):
    """ prices are not strings and are positive """
    try:
        price = float(price)
    except ValueError:
        return False
    else:
        if price > 0:
            return True
        else:
            return False

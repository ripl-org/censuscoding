import re
import usaddress
from censuscoding import Log
log = Log(__name__)

# Translation table for transliteration of non-ASCII
# letters to ASCII.
_ascii_trans = str.maketrans({
    u"\xc0": "A",
    u"\xc1": "A", # Remove accent mark over A
    u"\xc2": "A", # Remove hat mark over A
    u"\xc3": "A", # Remove ~ over A
    u"\xc4": "A",
    u"\xc5": "A", # Remove ring over A
    u"\xc6": "AE",
    u"\xc7": "C",
    u"\xc8": "E",
    u"\xc9": "E", # Remove acute over E
    u"\xca": "E",
    u"\xcb": "E",
    u"\xcc": "I",
    u"\xcd": "I",
    u"\xce": "I",
    u"\xcf": "I", # Remove diaeresis over I
    u"\xd0": "D",
    u"\xd1": "N", # Remove ~ on top of N
    u"\xd2": "O", # Remove grave over O
    u"\xd3": "O",
    u"\xd4": "O", # Remove hat over O
    u"\xd5": "O", # Remove ~ over O
    u"\xd6": "O", # Remove diaeresis over O
    u"\xd7": "x", # Replace multiplication sign
    u"\xd8": "O",
    u"\xd9": "U", # Remove grave over U
    u"\xda": "U", # Remove acute over U
    u"\xdb": "U", # Remove hat over U
    u"\xdc": "U", # Remove diaeresis over U
    u"\xdd": "Y", # Remove acute over Y
    u"\xde": "Th", # Replace capital letter thorn
    u"\xdf": "s", # Replace eszett with single s (assuming lower case) 
    u"\xe0": "a", # Remove grave above a 
    u"\xe1": "a", # Remove acute above a 
    u"\xe2": "a", # Remove circumflex above a 
    u"\xe3": "a", # Remove ~ above a
    u"\xe4": "a", # Remove diaeresis above a   
    u"\xe5": "a", # Remove ring above a 
    u"\xe6": "ae", # Replace ae single letter with ae 
    u"\xe7": "c", # Remove tail on c
    u"\xe8": "e", # Remove grave on e
    u"\xe9": "e", # Remove acute on e
    u"\xea": "e",
    u"\xeb": "e",
    u"\xec": "i",
    u"\xed": "i",
    u"\xee": "i",
    u"\xef": "i", # Remove diaeresis on i
    u"\xf0": "d",
    u"\xf1": "n", # Remove ~ on top of n
    u"\xf2": "o",
    u"\xf3": "o",
    u"\xf4": "o", # Remove hat over o
    u"\xf5": "o",
    u"\xf6": "o", # Remove diaeresis over o 
    u"\xf7": None, # Remove math symbol
    u"\xf8": "o",
    u"\xf9": "u", # Remove grave over u 
    u"\xfa": "u", # Remove acute over u 
    u"\xfb": "u", # Remove hat over u
    u"\xfc": "u", # Remove diaeresis over u 
    u"\xfd": "y", # Replace accent over y
    u"\xfe": "th", # Replace lower case thorn
    u"\xff": "y", # Remove diaeresis over y
})


_alphanum = re.compile(r"[^0-9A-Z ]")


_directionals = {
    "NORTH": "N",
    "N": "N",
    "EAST": "E",
    "E": "E",
    "SOUTH": "S",
    "S": "S",
    "WEST": "W",
    "W": "W",
    "NORTHEAST": "NE",
    "NE": "NE",
    "NORTHWEST": "NW",
    "NW": "NW",
    "SOUTHEAST": "SE",
    "SE": "SE",
    "SOUTHWEST": "SW",
    "SW": "SW"
}


def _clean(address):
    """
    Remove problematic street types that confuse uaddress
    """
    address = transliterate(address)
    if address.endswith(" STATE PARK"):
        return address.rstrip(" STATE PARK") + " ST"
    elif address.endswith(" TRAILER PARK"):
        return address.rstrip(" TRAILER PARK") + " ST"
    elif address.endswith(" SHOPPING PARK"):
        return address.rstrip(" SHOPPING PARK") + " ST"
    elif address.endswith(" PARK"):
        return address.rstrip(" PARK") + " ST"
    elif address.endswith(" MOBILE MNR"):
        return address.rstrip(" MOBILE MNR") + " ST"
    elif address.endswith(" CT"):
        return address.rstrip(" CT") + " ST"
    elif address.endswith(" HWY"):
        return address.rstrip(" HWY") + " ST"
    elif address.endswith(" COUNTY RD"):
        return address.rstrip(" RD") + " ST" # Only remove RD
    elif address.endswith(" STATE RD"):
        return address.rstrip(" RD") + " ST" # Only remove RD
    else:
        return address


def _tag(address):
    """
    Tag address with usaddress
    """
    try:
        tags = usaddress.tag(address)
    except:
        log.warn(f"cannot tag address {address}")
        return None
    if len(tags) < 1:
        log.warn(f"empty tags for address {address}")
        return None
    else:
        return tags


def normalize_directional(directional):
    """
    """
    normalized = _directionals.get(directional.upper(), None)
    if normalized is None:
        log.warn(f"bad directional '{directional}'")
        return ""
    else:
        return normalized


def normalize_street(address):
    """
    Tag address with usaddress and interpret tags to determine
    a normalized street name.
    """
    tags = _tag(_clean(address))
    # Interpret tags to determine street name
    if tags is not None:
        tags = tags[0]
        if "StreetName" in tags and "StreetNamePreDirectional" in tags:
            directional = normalize_directional(tags['StreetNamePreDirectional'])
            if directional:
                return f"{directional} {tags['StreetName']}"
            else:
                return tags["StreetName"]
        elif "StreetName" in tags and "StreetNamePostDirectional" in tags:
            directional = normalize_directional(tags['StreetNamePostDirectional'])
            if directional:
                return f"{directional} {tags['StreetName']}"
            else:
                return tags["StreetName"]
        elif "StreetName" in tags:
            return tags["StreetName"]
        elif "StreetNamePreDirectional" in tags:
            return tags["StreetNamePreDirectional"]
        elif "StreetNamePostDirectional" in tags:
            return tags["StreetNamePostDirectional"]
        else:
            log.warn(f"missing street name for address '{address}'")
    return ""


def extract_street_num(address):
    """
    Tag address with usaddress and return street num
    """
    tags = _tag(_clean(address))
    if tags is not None:
        tags = tags[0]
        if "AddressNumber" in tags:
            return tags["AddressNumber"]
        else:
            log.warn(f"missing street num for address '{address}'")
    return ""


def transliterate(name):
    """
    Transliterate a street name to the closest ASCII representation.
    """
    return _alphanum.sub("", name.translate(_ascii_trans).upper())

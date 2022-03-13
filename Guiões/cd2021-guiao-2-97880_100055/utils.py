def dht_hash(text, seed=0, maximum=2**10):
    """ FNV-1a Hash Function. """
    fnv_prime = 16777619
    offset_basis = 2166136261
    h = offset_basis + seed
    for char in text:
        h = h ^ ord(char)
        h = h * fnv_prime
    return h % maximum


#Checks if the node we're looking for is contained in the range between begin and end
#Usually the first condition will be enough
#But if the node is in the 
def contains(begin, end, node):
    """Check node is contained between begin and end in a ring."""
    #normal case                number closer to end in the evil spot       number closer to start in evil spot
    if (begin<node<=end or node>begin>=end or begin>end>=node):
        return True
    else:
        return False

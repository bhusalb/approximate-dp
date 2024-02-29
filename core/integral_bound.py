import math


def calculate_bounds(sigma):
    eb = calculate_error_bound()
    return sigma / math.sqrt(eb)


def calculate_error_bound(k=10):
    return 1 / (k ** 2)


def calculate_sigma(eps_lower, factor):
    return eps_lower / factor



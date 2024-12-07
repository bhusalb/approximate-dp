import math


def calculate_bounds(sigma, k=4):
    k = k * sigma
    eb = calculate_error_bound(k, sigma)

    return k, eb


# def calculate_error_bound(k=10):
#     return 1 / (k ** 2)
#

def calculate_error_bound(k, sigma):
    return 2 * math.exp(- (k ** 2) / (2 * (sigma ** 2)))


def calculate_sigma(eps_lower, factor):
    return factor / eps_lower

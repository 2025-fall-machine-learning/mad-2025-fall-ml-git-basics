def sum_one_to_million():
    """Manually add up numbers from 1 to 1,000,000."""
    # BUG: total was re-initialized inside the loop and never returned.
    total = 0
    for num_counter in range(1, 1000001):
        total += num_counter
    return total


def compute_e(precision=10):
    """
    Compute e using the Taylor series: e = sum(1/n!) for n = 0 to infinity.
    
    Args:
        precision: Number of decimal places to compute to (default: 10)
    
    Returns:
        tuple: (approx_e, terms_used)
            approx_e (float): Approximation of e computed from the series.
            terms_used (int): Number of terms included in the series (n when loop stopped).
    """

    # This function is supposed to calculate 1 + 1 + 1/2*1 + 1/3*2*1 + 1/4*3*2*1 + 1/5*4*3*2*1...
    # The first term is 1/0! = 1, the second term is 1/1! = 1, the third term is 1/2! = 1/2*1 = 0.5,
    # etc. It may seem strange that 0! is 1, but that is the mathematical definition. By way of
    # explanation, it turns out to be very useful, well, in the definition of e that we're doing here,
    # as well as other mathematical contexts.
    
    # If the precision is 10, we calculate the terms until they are smaller than
    # .000000000000001. That is, the term is smaller than 10^-15 if you remember
    # your scientific notation.
    threshold = 10 ** (-(precision + 5))

    # Correct incremental factorial/evaluation. Many bugs were here:
    # - factorial must start at 1 (0! == 1)
    # - each term must be added to `e`
    # - function should return both the computed e and number of terms used
    e = 1.0  # Start with 1/0! = 1
    factorial = 1
    n = 1
    while True:
        factorial *= n
        term = 1.0 / factorial
        e += term
        if term < threshold:
            break
        n += 1

    return e, n


def main():
    # We'll compute e, but first let's do the sum from 1 to 1,000,000.
    result = sum_one_to_million()
    print(f"The sum of numbers from 1 to 1,000,000 is: {result}")

    # The answer should be 2.7182818285.
    # compute_e now returns (e_value, n_terms)
    e_value, n_terms = compute_e(precision=10)
    print(f"\nComputed value of e to 10 decimal places: {e_value:.10f}")
    print(f"Number of terms used in the series: {n_terms}")


if __name__ == "__main__":
    main()
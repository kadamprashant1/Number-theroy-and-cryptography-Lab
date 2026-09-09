"""
LAB 1 -- Modular Arithmetic and Extended Euclidean Algorithm
==============================================================

For EVERY operation below, two independent implementations are provided:

    (1) NAIVE / MANUAL   -- written from scratch, no library shortcuts
    (2) PREBUILT/LIBRARY -- Python's built-in / standard-library equivalent

Whenever an operation is invoked, BOTH implementations run, one right
after the other, each timed SEPARATELY, and both the result and the
timing of each approach are printed to the screen.

Operations covered:
    1. GCD
    2. Extended Euclidean Algorithm   (ax + by = gcd(a,b))
    3. Modular inverse
    4. Modular addition
    5. Modular multiplication
    6. Modular exponentiation

Run:
    python modular_arithmetic_lab.py            -> demo + correctness tests + timing experiment
    python modular_arithmetic_lab.py --calc      -> interactive calculator (naive + prebuilt, every op)
"""

import math
import random
import secrets
import sys
import time

try:
    import gmpy2
    HAVE_GMPY2 = True
except ImportError:
    HAVE_GMPY2 = False


# ===========================================================================
#  Small "from scratch" primitives used by the NAIVE implementations
#  (so the naive versions don't secretly lean on Python's % or built-in pow)
# ===========================================================================
def manual_mod(x: int, m: int) -> int:
    """
    Remainder of x mod m, computed by hand with binary long division
    (shift + subtract). Does NOT use %, //, or divmod. O(bit-length(x)).
    Matches Python's % sign convention for m > 0.
    """
    if m == 0:
        raise ZeroDivisionError("modulo by zero")
    m_abs = abs(m)
    negative_x = x < 0
    x_abs = abs(x)

    if x_abs < m_abs:
        r = x_abs
    else:
        shift = x_abs.bit_length() - m_abs.bit_length()
        divisor = m_abs << shift
        r = x_abs
        while shift >= 0:
            if divisor <= r:
                r -= divisor
            divisor >>= 1
            shift -= 1

    if negative_x and r != 0:
        r = m_abs - r
    return r


def naive_multiply(a: int, b: int) -> int:
    """a * b computed by hand via shift-and-add (binary long multiplication)."""
    negative = (a < 0) != (b < 0)
    a, b = abs(a), abs(b)
    result = 0
    while b > 0:
        if b & 1:
            result += a
        a <<= 1
        b >>= 1
    return -result if negative else result


# ===========================================================================
# 1. GCD
# ===========================================================================
def gcd_naive(a: int, b: int) -> int:
    """Hand-written Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, manual_mod(a, b)
    return a


def gcd_prebuilt(a: int, b: int) -> int:
    """Python standard-library implementation."""
    return math.gcd(a, b)


# ===========================================================================
# 2. Extended Euclidean Algorithm
# ===========================================================================
def extended_gcd_naive(a: int, b: int):
    """
    Hand-written iterative extended Euclidean algorithm.
    Returns (g, x, y) with a*x + b*y = g = gcd(a, b), g >= 0.
    """
    sign_a = -1 if a < 0 else 1
    sign_b = -1 if b < 0 else 1
    ua, ub = abs(a), abs(b)

    old_r, r = ua, ub
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        q = old_r // r          # quotient only -- see note below
        old_r, r = r, old_r - naive_multiply(q, r)
        old_s, s = s, old_s - naive_multiply(q, s)
        old_t, t = t, old_t - naive_multiply(q, t)

    return old_r, old_s * sign_a, old_t * sign_b
    # NOTE: `//` here is only used to find the quotient for the subtraction
    # step; manual_mod above already demonstrates hand-rolled division.


def extended_gcd_prebuilt(a: int, b: int):
    """
    Library implementation via gmpy2.gcdext(a, b) -> (x, y, g) with
    a*x + b*y = g.  Requires `pip install gmpy2`.
    """
    if not HAVE_GMPY2:
        raise RuntimeError("gmpy2 is not installed -- run: pip install gmpy2")
    g, x, y = gmpy2.gcdext(a, b)
    return int(g), int(x), int(y)


# ===========================================================================
# 3. Modular inverse
# ===========================================================================
def mod_inverse_naive(a: int, m: int) -> int:
    """Hand-written: uses our own extended_gcd_naive."""
    if m <= 0:
        raise ValueError("modulus must be positive")
    a_mod = manual_mod(a, m)
    g, x, _ = extended_gcd_naive(a_mod, m)
    if g != 1:
        raise ValueError(f"No modular inverse: gcd({a_mod}, {m}) = {g} != 1")
    return manual_mod(x, m)


def mod_inverse_prebuilt(a: int, m: int) -> int:
    """Library implementation: Python's built-in pow(a, -1, m)  (Python >= 3.8)."""
    return pow(a, -1, m)


# ===========================================================================
# 4. Modular addition
# ===========================================================================
def mod_add_naive(a: int, b: int, m: int) -> int:
    """Hand-written: plain addition, reduced with manual_mod (no % operator)."""
    return manual_mod(a + b, m)


def mod_add_prebuilt(a: int, b: int, m: int) -> int:
    """Library implementation: Python's built-in % operator."""
    return (a + b) % m


# ===========================================================================
# 5. Modular multiplication
# ===========================================================================
def mod_mul_naive(a: int, b: int, m: int) -> int:
    """Hand-written: shift-and-add multiply, reduced with manual_mod."""
    return manual_mod(naive_multiply(a, b), m)


def mod_mul_prebuilt(a: int, b: int, m: int) -> int:
    """Library implementation: Python's built-in * and % operators."""
    return (a * b) % m


# ===========================================================================
# 6. Modular exponentiation
# ===========================================================================
NAIVE_EXP_LIMIT = 300_000  # safety cap: naive is O(exp) -- don't hang the demo/calculator


def mod_pow_naive(base: int, exp: int, mod: int) -> int:
    """
    Hand-written, truly naive approach: multiply the result into itself
    `exp` times. O(exp) modular multiplications -- this is the whole point
    of comparing it against the built-in, which is orders of magnitude
    faster for large exponents.
    """
    if exp < 0:
        raise ValueError("only non-negative exponents supported")
    if exp > NAIVE_EXP_LIMIT:
        raise OverflowError(
            f"exponent {exp} exceeds the naive-method safety cap "
            f"({NAIVE_EXP_LIMIT}); it would take too long with O(exp) "
            f"multiplications. Try a smaller exponent for the naive method."
        )
    result = manual_mod(1, mod)
    b = manual_mod(base, mod)
    for _ in range(exp):
        result = manual_mod(naive_multiply(result, b), mod)
    return result


def mod_pow_prebuilt(base: int, exp: int, mod: int) -> int:
    """Library implementation: Python's built-in three-argument pow(base, exp, mod)."""
    return pow(base, exp, mod)


# Kept as a bonus -- the "real-world" hand-written algorithm (not naive,
# not a library call) that professional crypto code actually uses.
def mod_pow_square_and_multiply(base: int, exp: int, mod: int) -> int:
    """Hand-written square-and-multiply. O(log exp) modular multiplications."""
    if exp < 0:
        raise ValueError("only non-negative exponents supported")
    result = manual_mod(1, mod)
    b = manual_mod(base, mod)
    e = exp
    while e > 0:
        if e & 1:
            result = manual_mod(naive_multiply(result, b), mod)
        b = manual_mod(naive_multiply(b, b), mod)
        e >>= 1
    return result


# ===========================================================================
# Generic "run both ways" helper
# ===========================================================================
def run_both(op_name, naive_fn, prebuilt_fn, args,
             naive_label="NAIVE (manual)", prebuilt_label="PREBUILT (library)"):
    """
    Calls naive_fn(*args), then prebuilt_fn(*args), one right after the other.
    Times each call SEPARATELY and prints both results + timings to the screen.
    """
    print(f"\n----- {op_name} -----")
    print(f"inputs: {args}")

    # ---- 1) naive, runs first ----
    t0 = time.perf_counter()
    try:
        naive_result = naive_fn(*args)
        naive_error = None
    except Exception as e:
        naive_result = None
        naive_error = e
    t_naive = time.perf_counter() - t0

    # ---- 2) prebuilt, runs right after ----
    t0 = time.perf_counter()
    try:
        prebuilt_result = prebuilt_fn(*args)
        prebuilt_error = None
    except Exception as e:
        prebuilt_result = None
        prebuilt_error = e
    t_prebuilt = time.perf_counter() - t0

    # ---- report ----
    if naive_error is None:
        print(f"[{naive_label:22s}] result = {naive_result}")
    else:
        print(f"[{naive_label:22s}] ERROR  = {naive_error}")
    print(f"[{naive_label:22s}] time   = {t_naive:.8f} s")

    if prebuilt_error is None:
        print(f"[{prebuilt_label:22s}] result = {prebuilt_result}")
    else:
        print(f"[{prebuilt_label:22s}] ERROR  = {prebuilt_error}")
    print(f"[{prebuilt_label:22s}] time   = {t_prebuilt:.8f} s")

    if naive_error is None and prebuilt_error is None:
        match = naive_result == prebuilt_result
        print(f"results match          = {match}")
        if t_prebuilt > 0:
            print(f"speed ratio (naive/prebuilt) = {t_naive / t_prebuilt:,.1f}x")

    return naive_result, prebuilt_result, t_naive, t_prebuilt


# ===========================================================================
# Correctness tests -- naive vs prebuilt, on lots of random inputs
# ===========================================================================
def run_correctness_tests(trials: int = 1000) -> None:
    print("=" * 78)
    print("CORRECTNESS TESTS  (naive vs. prebuilt, on random inputs)")
    print("=" * 78)

    for _ in range(trials):
        a = random.randint(-(10 ** 6), 10 ** 6)
        b = random.randint(-(10 ** 6), 10 ** 6)

        assert gcd_naive(a, b) == gcd_prebuilt(a, b)

        g1, x1, y1 = extended_gcd_naive(a, b)
        assert g1 == gcd_prebuilt(a, b)
        assert a * x1 + b * y1 == g1
        if HAVE_GMPY2:
            g2, x2, y2 = extended_gcd_prebuilt(a, b)
            assert g2 == g1
            assert a * x2 + b * y2 == g2

    for _ in range(trials):
        m = random.randint(2, 10_000)
        a = random.randint(1, 10_000)
        if math.gcd(a, m) != 1:
            continue
        inv_naive = mod_inverse_naive(a, m)
        inv_prebuilt = mod_inverse_prebuilt(a, m)
        assert inv_naive == inv_prebuilt
        assert (a * inv_naive) % m == 1

    for _ in range(trials):
        m = random.randint(1, 10_000)
        a = random.randint(-10_000, 10_000)
        b = random.randint(-10_000, 10_000)
        assert mod_add_naive(a, b, m) == mod_add_prebuilt(a, b, m)
        assert mod_mul_naive(a, b, m) == mod_mul_prebuilt(a, b, m)

    for _ in range(200):
        m = random.randint(2, 5000)
        base = random.randint(0, 5000)
        exp = random.randint(0, 500)
        expected = pow(base, exp, m)
        assert mod_pow_naive(base, exp, m) == expected
        assert mod_pow_square_and_multiply(base, exp, m) == expected
        assert mod_pow_prebuilt(base, exp, m) == expected

    gmpy2_note = "" if HAVE_GMPY2 else "  (gmpy2 not installed -> extended-gcd 'prebuilt' checks skipped)"
    print(f"All {trials} random trials passed for every naive/prebuilt pair.{gmpy2_note} \u2714\n")


# ===========================================================================
# Full demo: run every operation, naive then prebuilt, back to back
# ===========================================================================
def run_full_demo() -> None:
    print("=" * 78)
    print("DEMO -- every operation, naive approach then prebuilt approach")
    print("=" * 78)

    a, b, m = 123_456_789, 987_654_321, 1_000_000_007
    run_both("1. GCD(a, b)", gcd_naive, gcd_prebuilt, (a, b))
    run_both("2. Extended Euclid  (ax + by = gcd)", extended_gcd_naive, extended_gcd_prebuilt, (a, b))
    run_both("3. Modular inverse  a^-1 mod m", mod_inverse_naive, mod_inverse_prebuilt, (a, m))
    run_both("4. Modular addition  (a+b) mod m", mod_add_naive, mod_add_prebuilt, (a, b, m))
    run_both("5. Modular multiplication  (a*b) mod m", mod_mul_naive, mod_mul_prebuilt, (a, b, m))
    run_both("6. Modular exponentiation  a^exp mod m", mod_pow_naive, mod_pow_prebuilt, (a, 1000, m))
    print()


def run_big_number_demo() -> None:
    print("=" * 78)
    print("DEMO WITH >= 512-BIT NUMBERS  (naive vs prebuilt)")
    print("=" * 78)

    a = secrets.randbits(512) | 1
    b = secrets.randbits(512) | 1
    m = secrets.randbits(512) | 1
    print(f"a (512-bit) = {a}")
    print(f"b (512-bit) = {b}")
    print(f"m (512-bit) = {m}")

    run_both("GCD(a, b)", gcd_naive, gcd_prebuilt, (a, b))
    run_both("Extended Euclid  (ax + by = gcd)", extended_gcd_naive, extended_gcd_prebuilt, (a, b))
    run_both("Modular addition  (a+b) mod m", mod_add_naive, mod_add_prebuilt, (a, b, m))
    run_both("Modular multiplication  (a*b) mod m", mod_mul_naive, mod_mul_prebuilt, (a, b, m))

    # a moderate exponent so the naive O(exp) loop doesn't run forever
    exp = 5000
    run_both(f"Modular exponentiation  a^{exp} mod m",
             mod_pow_naive, mod_pow_prebuilt, (a % m, exp, m))
    print()


# ===========================================================================
# Timing experiment: naive vs prebuilt exponentiation, growing exponent
# ===========================================================================
def run_timing_experiment() -> None:
    print("=" * 78)
    print("EXPERIMENT: modular exponentiation -- naive loop vs. prebuilt pow()")
    print("=" * 78)

    mod = (1 << 521) - 1
    base = secrets.randbelow(mod)

    exponents = [2 ** k for k in range(4, 15)]
    print(f"{'exponent':>12} | {'naive (s)':>14} | {'prebuilt pow() (s)':>20} | speedup")
    print("-" * 78)

    for exp in exponents:
        if exp <= NAIVE_EXP_LIMIT:
            t0 = time.perf_counter()
            r_naive = mod_pow_naive(base, exp, mod)
            t_naive = time.perf_counter() - t0
        else:
            r_naive, t_naive = None, float("nan")

        t0 = time.perf_counter()
        r_prebuilt = mod_pow_prebuilt(base, exp, mod)
        t_prebuilt = time.perf_counter() - t0

        if r_naive is not None:
            assert r_naive == r_prebuilt
            print(f"{exp:>12} | {t_naive:>14.6f} | {t_prebuilt:>20.6f} | {t_naive / t_prebuilt:>7,.0f}x")
        else:
            print(f"{exp:>12} | {'skipped':>14} | {t_prebuilt:>20.6f} | {'n/a':>7}")

    print()
    print("naive: exp-1 modular multiplications                 -> O(exp)")
    print("pow() (built-in, C-implemented square-and-multiply)  -> O(log exp)")
    print()


# ===========================================================================
# Calculator application (every operation offers BOTH approaches)
# ===========================================================================
MENU = """
==================== MODULAR ARITHMETIC CALCULATOR ====================
Every operation below runs its NAIVE (manual) implementation, then its
PREBUILT (library) implementation, right after each other -- each timed
and shown separately.

  1. GCD(a, b)
  2. Extended Euclidean Algorithm   (ax + by = gcd(a,b))
  3. Modular inverse                (a^-1 mod m)
  4. Modular addition               (a + b) mod m
  5. Modular multiplication         (a * b) mod m
  6. Modular exponentiation         (a^b) mod m
  0. Exit
=========================================================================
"""


def read_int(prompt: str) -> int:
    """Reads a (possibly huge, possibly 0x-hex) integer from the user."""
    raw = input(prompt).strip()
    try:
        return int(raw, 16) if raw.lower().startswith("0x") else int(raw)
    except ValueError:
        print("  ! Not a valid integer, try again.")
        return read_int(prompt)


def calculator() -> None:
    print(MENU)
    while True:
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        elif choice == "1":
            a = read_int("  a = ")
            b = read_int("  b = ")
            run_both("GCD(a, b)", gcd_naive, gcd_prebuilt, (a, b))

        elif choice == "2":
            a = read_int("  a = ")
            b = read_int("  b = ")
            run_both("Extended Euclid  (ax + by = gcd)", extended_gcd_naive, extended_gcd_prebuilt, (a, b))

        elif choice == "3":
            a = read_int("  a = ")
            m = read_int("  m = ")
            run_both("Modular inverse  a^-1 mod m", mod_inverse_naive, mod_inverse_prebuilt, (a, m))

        elif choice == "4":
            a = read_int("  a = ")
            b = read_int("  b = ")
            m = read_int("  m = ")
            run_both("Modular addition  (a+b) mod m", mod_add_naive, mod_add_prebuilt, (a, b, m))

        elif choice == "5":
            a = read_int("  a = ")
            b = read_int("  b = ")
            m = read_int("  m = ")
            run_both("Modular multiplication  (a*b) mod m", mod_mul_naive, mod_mul_prebuilt, (a, b, m))

        elif choice == "6":
            a = read_int("  base a = ")
            exp = read_int("  exponent (>= 0) = ")
            m = read_int("  modulus m = ")
            run_both("Modular exponentiation  a^exp mod m", mod_pow_naive, mod_pow_prebuilt, (a, exp, m))
            if exp > NAIVE_EXP_LIMIT:
                print(f"  (note: naive was skipped -- exponent > {NAIVE_EXP_LIMIT:,} safety cap)")
            print("  extra: hand-written square-and-multiply (not naive, not library):")
            t0 = time.perf_counter()
            r = mod_pow_square_and_multiply(a, exp, m)
            dt = time.perf_counter() - t0
            print(f"  [square-and-multiply  ] result = {r}")
            print(f"  [square-and-multiply  ] time   = {dt:.8f} s")

        else:
            print("  ! Invalid option.\n")


if __name__ == "__main__":
    if "--calc" in sys.argv:
        calculator()
    else:
        run_correctness_tests()
        run_full_demo()
        run_big_number_demo()
        run_timing_experiment()
        print("Run again with `--calc` for the interactive calculator, e.g.:")
        print("    python modular_arithmetic_lab.py --calc")
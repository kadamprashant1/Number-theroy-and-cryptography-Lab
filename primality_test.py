import random
import time

try:
    import readline
except ImportError:
    pass

from cpython import extended_gcd_naive


def trivial_primality_test(p: int) -> bool:
    if p <= 1:
        return False
    if p == 2:
        return True
    if p % 2 == 0:
        return False
    for i in range(3, int(p**0.5) + 1, 2):
        if p % i == 0:
            return False
    return True


def fermat_primality_test(p: int, k: int = 5) -> bool:
    if p <= 1:
        return False
    if p in (2, 3):
        return True
    if p % 2 == 0:
        return False

    for _ in range(max(1, k)):
        a = random.randint(2, p - 2)
        gcd = extended_gcd_naive(p, a)[0]
        if gcd != 1 or pow(a, p - 1, p) != 1:
            return False
    return True


def miller_rabin_primality_test(p: int, k: int = 5) -> bool:
    if p <= 1:
        return False
    if p in (2, 3):
        return True
    if p % 2 == 0:
        return False

    d, s = p - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(max(1, k)):
        a = random.randint(2, p - 2)
        x = pow(a, d, p)
        if x == 1 or x == p - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, p)
            if x == p - 1:
                break
        else:
            return False
    return True


def trivial_menu():
    print("\n--- Trivial Division ---")
    try:
        p = int(input("Enter p: "))
    except ValueError:
        print("Invalid input.")
        return
    res = trivial_primality_test(p)
    print(f"{p} is {'prime' if res else 'composite'}")


def fermat_test_menu():
    print("\n--- Fermat Test ---")
    try:
        p = int(input("Enter p: "))
        rep = input("Repetitions [5]: ").strip()
        k = int(rep) if rep else 5
    except ValueError:
        print("Invalid input.")
        return
    res = fermat_primality_test(p, k)
    print(f"{p} is {'probably prime' if res else 'composite'}")


def Miller_rabin_menu():
    print("\n--- Miller-Rabin Test ---")
    try:
        p = int(input("Enter p: "))
        rep = input("Repetitions [5]: ").strip()
        k = int(rep) if rep else 5
    except ValueError:
        print("Invalid input.")
        return
    res = miller_rabin_primality_test(p, k)
    print(f"{p} is {'probably prime' if res else 'composite'}")


def run_expriment_menu():
    print("\n--- Primality Test Comparison ---")
    cases = [101, 257, 1000000007, 1000, 10001, 561, 1105, 1729]
    print(f"{'n':<12} | {'Trivial':<16} | {'Fermat':<16} | {'Miller-Rabin':<16}")
    print("-" * 65)

    for n in cases:
        t0 = time.perf_counter()
        t_res = trivial_primality_test(n)
        t_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        f_res = fermat_primality_test(n, 5)
        f_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        mr_res = miller_rabin_primality_test(n, 5)
        mr_time = time.perf_counter() - t0

        t_str = f"{'Prime' if t_res else 'Comp'} ({t_time:.1e}s)"
        f_str = f"{'Prime' if f_res else 'Comp'} ({f_time:.1e}s)"
        mr_str = f"{'Prime' if mr_res else 'Comp'} ({mr_time:.1e}s)"
        print(f"{n:<12} | {t_str:<16} | {f_str:<16} | {mr_str:<16}")


MENU_OPTIONS = {
    "1": ("Trivial Division", trivial_menu),
    "2": ("Fermat Primality Test", fermat_test_menu),
    "3": ("Miller-Rabin Primality Test", Miller_rabin_menu),
    "4": ("Run Comparison Experiment", run_expriment_menu),
}

if __name__ == "__main__":
    while True:
        print("\nPrimality Test Tool")
        for k, (desc, _) in MENU_OPTIONS.items():
            print(f"  [{k}] {desc}")
        print("  [0] Exit")

        choice = input("Choice: ").strip()
        if choice == "0":
            break
        elif choice in MENU_OPTIONS:
            MENU_OPTIONS[choice][1]()
        else:
            print("Invalid choice.")

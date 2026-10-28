import time
from collections.abc import Iterable

from cpython import (
    extended_gcd_naive,
    manual_mod,
    mod_inverse_naive,
    mod_mul_naive,
    naive_multiply,
)


def combine_congruences(a1: int, n1: int, a2: int, n2: int) -> tuple[int, int]:
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Moduli must be positive integers.")

    a1 = manual_mod(a1, n1)
    a2 = manual_mod(a2, n2)
    gcd, _, _ = extended_gcd_naive(n1, n2)
    difference = a2 - a1
    if difference % gcd:
        raise ValueError(
            f"No solution: the residues differ by {difference}, which is not "
            f"divisible by gcd({n1}, {n2}) = {gcd}."
        )

    reduced_n1 = n1 // gcd
    reduced_n2 = n2 // gcd
    inverse = mod_inverse_naive(reduced_n1, reduced_n2)
    multiplier = mod_mul_naive(difference // gcd, inverse, reduced_n2)
    modulus = naive_multiply(n1, reduced_n2)
    residue = manual_mod(a1 + naive_multiply(n1, multiplier), modulus)
    return residue, modulus


def solve_crt(congruences: Iterable[tuple[int, int]]) -> tuple[int, int]:
    items = iter(congruences)
    try:
        residue, modulus = next(items)
    except StopIteration as exc:
        raise ValueError("Enter at least one congruence.") from exc

    if modulus <= 0:
        raise ValueError("Moduli must be positive integers.")
    residue = manual_mod(residue, modulus)

    for next_residue, next_modulus in items:
        residue, modulus = combine_congruences(
            residue, modulus, next_residue, next_modulus
        )
    return residue, modulus




def _best_average_time(func, repetitions: int | None, rounds: int = 3) -> float:
    func() 
    if repetitions is None:
        start = time.perf_counter()
        func()
        single = max(time.perf_counter() - start, 1e-9)
        repetitions = max(5, min(50_000, int(0.05 / single)))

    best = float("inf")
    for _ in range(rounds):
        start = time.perf_counter()
        for _ in range(repetitions):
            func()
        best = min(best, (time.perf_counter() - start) / repetitions)
    return best


def rsa_decryption_experiment(
    p: int, q: int, public_exponent: int, message: int, repetitions: int | None = None
) -> dict[str, int | float]:
    """Encrypt a message, then time ordinary and CRT-based RSA decryption."""

    if repetitions is not None and repetitions <= 0:
        raise ValueError("Repetitions must be positive.")

    modulus = p * q
    phi = (p - 1) * (q - 1)
    if not 1 < public_exponent < phi:
        raise ValueError("The public exponent must be between 1 and phi(n).")
    if extended_gcd_naive(public_exponent, phi)[0] != 1:
        raise ValueError("The public exponent must be coprime to phi(n).")
    if not 0 <= message < modulus:
        raise ValueError(f"The message must be in the range 0 to {modulus - 1}.")

    private_exponent = mod_inverse_naive(public_exponent, phi)
    ciphertext = pow(message, public_exponent, modulus)

    # CRT key constants: computed once at key setup, NOT inside the timed code.
    d_p = private_exponent % (p - 1)
    d_q = private_exponent % (q - 1)
    q_inv_mod_p = pow(q, -1, p)

    def decrypt_normally() -> int:
        return pow(ciphertext, private_exponent, modulus)

    def decrypt_with_crt() -> int:
        m_p = pow(ciphertext, d_p, p)
        m_q = pow(ciphertext, d_q, q)
        h = (q_inv_mod_p * (m_p - m_q)) % p
        return m_q + h * q

    normal_result = decrypt_normally()
    crt_result = decrypt_with_crt()
    if normal_result != message or crt_result != message:
        raise ArithmeticError("RSA decryption did not recover the input message.")

    normal_seconds = _best_average_time(decrypt_normally, repetitions)
    crt_seconds = _best_average_time(decrypt_with_crt, repetitions)

    return {
        "modulus": modulus,
        "phi": phi,
        "private_exponent": private_exponent,
        "ciphertext": ciphertext,
        "normal_result": normal_result,
        "crt_result": crt_result,
        "normal_seconds": normal_seconds,
        "crt_seconds": crt_seconds,
    }


def run_experiments() -> None:
    examples = [
        [(2, 3), (3, 5)],
        [(2, 6), (5, 9)],
        [(2, 3), (3, 5), (2, 7)],
    ]
    print("Generalized CRT experiments")
    for congruences in examples:
        residue, modulus = solve_crt(congruences)
        print(f"{congruences} -> x = {residue} (mod {modulus})")

    try:
        solve_crt([(1, 4), (2, 6)])
    except ValueError as exc:
        print(f"Inconsistent example: {exc}")

    print("\nRSA normal versus CRT decryption")
    result = rsa_decryption_experiment(1009, 1013, 65537, 12345)
    for key, value in result.items():
        print(f"{key}: {value}")


def menu_solve_crt() -> None:
    print("\n--- Solve System of Congruences (CRT) ---")
    congruences: list[tuple[int, int]] = []
    while True:
        entry = input(
            f"  Enter congruence #{len(congruences) + 1} as 'residue modulus'"
            " (or press Enter to solve): "
        ).strip()
        if not entry:
            if not congruences:
                print("  [!] Please enter at least one congruence.")
                continue
            break
        parts = entry.split()
        if len(parts) != 2:
            print("  [!] Expected two integers separated by a space. Try again.")
            continue
        try:
            a, n = int(parts[0]), int(parts[1])
        except ValueError:
            print("  [!] Both values must be integers. Try again.")
            continue
        congruences.append((a, n))

    try:
        residue, modulus = solve_crt(congruences)
        print(f"\n  Result: x ≡ {residue} (mod {modulus})")
    except (ValueError, ArithmeticError) as exc:
        print(f"\n  [Error] {exc}")


def menu_rsa_experiment() -> None:
    print("\n--- RSA Normal vs. CRT Decryption Experiment ---")
    try:
        p              = int(input("  Prime p              : "))
        q              = int(input("  Prime q              : "))
        public_exponent = int(input("  Public exponent (e)  : "))
        message        = int(input("  Message (0 ≤ m < p*q): "))
        rep_str        = input("  Repetitions [auto]   : ").strip()
    except ValueError:
        print("  [!] All inputs must be integers.")
        return

    try:
        result = rsa_decryption_experiment(p, q, public_exponent, message, None)
    except (ValueError, ArithmeticError) as exc:
        print(f"\n  [Error] {exc}")
        return

    print()
    width = max(len(k) for k in result)
    for key, value in result.items():
        if isinstance(value, float):
            print(f"  {key:<{width}} : {value:.6e} s")
        else:
            print(f"  {key:<{width}} : {value}")

    speedup = result["normal_seconds"] / result["crt_seconds"]
    print(f"\n  CRT speedup: {speedup:.2f}×")


MENU_OPTIONS = {
    "1": ("Solve a system of congruences (CRT)", menu_solve_crt),
    "2": ("Run RSA decryption timing experiment",  menu_rsa_experiment),
    "3": ("Run all built-in examples",             run_experiments),
}

if __name__ == "__main__":
    print("=" * 50)
    print("  Chinese Remainder Theorem (CRT) Tool")
    print("=" * 50)

    while True:
        print("\nMenu:")
        for key, (description, _) in MENU_OPTIONS.items():
            print(f"  [{key}] {description}")
        print("  [0] Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in MENU_OPTIONS:
            _, action = MENU_OPTIONS[choice]
            action()
        else:
            print(f"  [!] Invalid choice '{choice}'. Please enter 0–{len(MENU_OPTIONS)}.")

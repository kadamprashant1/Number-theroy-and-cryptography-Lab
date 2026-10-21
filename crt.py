import time
import random
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


def is_prime(value: int, k: int = 40) -> bool:
    if value < 2:
        return False
    if value in (2, 3):
        return True
    if value % 2 == 0:
        return False

    d = value - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, value - 2)
        x = pow(a, d, value)
        
        if x == 1 or x == value - 1:
            continue
            
        for _ in range(s - 1):
            x = pow(x, 2, value)
            if x == value - 1:
                break
        else:
            return False

    print(f"{value} is prime.")
    return True

def decrypt_normally(ciphertext, private_exponent, modulus) -> int:
    return pow(ciphertext, private_exponent, modulus)

def decrypt_with_crt(ciphertext, private_exponent,p,q) -> int:
    residue_p = pow(ciphertext, manual_mod(private_exponent , (p - 1)), p)
    residue_q = pow(ciphertext, manual_mod(private_exponent , (q - 1)), q)
    result, _ = combine_congruences(residue_p, p, residue_q, q)
    return result


def rsa_decryption_experiment(
    p: int, q: int, public_exponent: int, message: int, repetitions: int = 100) -> dict[str, int | float]:
    if not is_prime(p) or not is_prime(q) or p == q:
        raise ValueError("p and q must be distinct prime numbers.")
    if repetitions <= 0:
        raise ValueError("Repetitions must be positive.")
    
    start = time.perf_counter()
    modulus = naive_multiply(p, q)
    phi = naive_multiply((p - 1) , (q - 1))
    if not 1 < public_exponent < phi:
        raise ValueError("The public exponent must be between 1 and phi(n).")
    if extended_gcd_naive(public_exponent, phi)[0] != 1:
        raise ValueError("The public exponent must be coprime to phi(n).")
    if not 0 <= message < modulus:
        raise ValueError(f"The message must be in the range 0 to {modulus - 1}.")

    private_exponent = mod_inverse_naive(public_exponent, phi)
    ciphertext = pow(message, public_exponent, modulus)
    print(f"RSA decryption experiment: p={p}, q={q}, e={public_exponent}, message={message}")
    normal_result = decrypt_normally(ciphertext,private_exponent,modulus)
    crt_result = decrypt_with_crt(ciphertext,private_exponent,p,q)
    if normal_result != message or crt_result != message:
        raise ArithmeticError("RSA decryption did not recover the input message.")


    time_to_incrypt = (time.perf_counter() - start) / repetitions

    start = time.perf_counter()
    for _ in range(repetitions):
        decrypt_with_crt(ciphertext, private_exponent, p, q)
    crt_seconds = ((time.perf_counter() - start) / repetitions) + time_to_incrypt
        
    start = time.perf_counter()
    for _ in range(repetitions):
        decrypt_normally(ciphertext, private_exponent, modulus)
    normal_seconds = ((time.perf_counter() - start) / repetitions) + time_to_incrypt
        

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

    p_2048 = 13277052251592296463630465408098953821838756077009035847219343704305868323379051149315001423416212637570003177943584170509189094487560828622530869875126383

    q_2048 = 12639269531989147201733526724530731881626059465403263654998508727692235461208298365257438532927812866902939347404040456517853601759767854430231538883622993


    result = rsa_decryption_experiment(p_2048, q_2048, 65537, 12345)

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run_experiments()





#./.venv/bin/streamlit run calculatorUi.py --server.fileWatcherType none
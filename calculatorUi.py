import time
import streamlit as st

from crt import rsa_decryption_experiment, solve_crt
from cpython import (
    NAIVE_EXP_LIMIT,
    extended_gcd_naive,
    extended_gcd_prebuilt,
    gcd_naive,
    gcd_prebuilt,
    mod_add_naive,
    mod_add_prebuilt,
    mod_inverse_naive,
    mod_inverse_prebuilt,
    mod_mul_naive,
    mod_mul_prebuilt,
    mod_pow_naive,
    mod_pow_prebuilt,
    mod_pow_square_and_multiply,
)

EXPONENT_SAFETY_CAP = 200_000


def parse_int(raw_value: str, field_name: str) -> int:
    value = raw_value.strip()
    if value == "":
        raise ValueError(f"{field_name} is required.")

    try:
        return int(value, 16) if value.lower().startswith("0x") else int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {field_name}: {raw_value!r}") from exc


def safe_call(func, *args):
    start = time.perf_counter()
    try:
        result = func(*args)
        error = None
    except Exception as exc: 
        result = None
        error = exc
    elapsed = time.perf_counter() - start
    return result, error, elapsed


def show_side_by_side(label_a: str, result_a, error_a, elapsed_a, label_b: str, result_b, error_b, elapsed_b):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(label_a)
        if error_a is None:
            st.code(str(result_a))
            st.caption(f"Time: {elapsed_a:.6f}s")
        else:
            st.error(f"{error_a}")
            st.caption(f"Time: {elapsed_a:.6f}s")

    with col2:
        st.subheader(label_b)
        if error_b is None:
            st.code(str(result_b))
            st.caption(f"Time: {elapsed_b:.6f}s")
        else:
            st.error(f"{error_b}")
            st.caption(f"Time: {elapsed_b:.6f}s")


def render_gcd(a: int, b: int):
    naive_result, naive_error, naive_time = safe_call(gcd_naive, a, b)
    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(gcd_prebuilt, a, b)
    show_side_by_side("Naive GCD", naive_result, naive_error, naive_time, "Prebuilt GCD", prebuilt_result, prebuilt_error, prebuilt_time)


def render_extended_gcd(a: int, b: int):
    naive_result, naive_error, naive_time = safe_call(extended_gcd_naive, a, b)
    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(extended_gcd_prebuilt, a, b)

    if naive_error is None:
        g, x, y = naive_result
        st.markdown(f"**Naive equation:** {a}*{x} + {b}*{y} = {g}")
        st.code(f"g = {g}, x = {x}, y = {y}")

    if prebuilt_error is None:
        g, x, y = prebuilt_result
        st.markdown(f"**Prebuilt equation:** {a}*{x} + {b}*{y} = {g}")
        st.code(f"g = {g}, x = {x}, y = {y}")

    show_side_by_side("Naive Extended GCD", naive_result, naive_error, naive_time, "Prebuilt Extended GCD", prebuilt_result, prebuilt_error, prebuilt_time)


def render_mod_inverse(a: int, m: int):
    naive_result, naive_error, naive_time = safe_call(mod_inverse_naive, a, m)
    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(mod_inverse_prebuilt, a, m)
    show_side_by_side("Naive Modular Inverse", naive_result, naive_error, naive_time, "Prebuilt Modular Inverse", prebuilt_result, prebuilt_error, prebuilt_time)


def render_mod_add(a: int, b: int, m: int):
    naive_result, naive_error, naive_time = safe_call(mod_add_naive, a, b, m)
    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(mod_add_prebuilt, a, b, m)
    st.markdown(f"**Expression:** ({a} + {b}) mod {m}")
    show_side_by_side("Naive Modular Addition", naive_result, naive_error, naive_time, "Prebuilt Modular Addition", prebuilt_result, prebuilt_error, prebuilt_time)


def render_mod_mul(a: int, b: int, m: int):
    naive_result, naive_error, naive_time = safe_call(mod_mul_naive, a, b, m)
    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(mod_mul_prebuilt, a, b, m)
    st.markdown(f"**Expression:** ({a} * {b}) mod {m}")
    show_side_by_side("Naive Modular Multiplication", naive_result, naive_error, naive_time, "Prebuilt Modular Multiplication", prebuilt_result, prebuilt_error, prebuilt_time)


def render_mod_pow(base: int, exponent: int, mod: int):
    st.markdown(f"**Expression:** {base}^{exponent} mod {mod}")

    if exponent >= 0 and exponent > EXPONENT_SAFETY_CAP:
        naive_result, naive_time = None, 0.0
        naive_error = (
            f"Skipped: exponent {exponent:,} exceeds the UI safety cap "
            f"({EXPONENT_SAFETY_CAP:,}); the naive O(exponent) loop would "
            f"take too long. Try a smaller exponent to see the naive method."
        )
    else:
        naive_result, naive_error, naive_time = safe_call(mod_pow_naive, base, exponent, mod)

    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(mod_pow_prebuilt, base, exponent, mod)

    show_side_by_side("Naive Modular Exponentiation", naive_result, naive_error, naive_time, "Prebuilt Modular Exponentiation", prebuilt_result, prebuilt_error, prebuilt_time)

    if exponent >= 0:
        bonus_result, bonus_error, bonus_time = safe_call(mod_pow_square_and_multiply, base, exponent, mod)
        st.subheader("Square-and-Multiply")
        if bonus_error is None:
            st.code(str(bonus_result))
            st.caption(f"Time: {bonus_time:.6f}s")
        else:
            st.error(f"{bonus_error}")


def parse_congruence_lines(raw_value: str) -> list[tuple[int, int]]:
    congruences = []
    for line_number, line in enumerate(raw_value.splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) != 2:
            raise ValueError(
                f"Line {line_number} must contain a residue and modulus "
                "separated by a comma."
            )
        congruences.append(
            (
                parse_int(parts[0], f"residue on line {line_number}"),
                parse_int(parts[1], f"modulus on line {line_number}"),
            )
        )
    if not congruences:
        raise ValueError("Enter at least one congruence.")
    return congruences


def main():
    st.set_page_config(page_title="Number Theory Calculator", layout="wide")
    st.title("Number Theory and Cryptography Lab")
    arithmetic_tab, crt_tab, rsa_tab = st.tabs(
        ["Modular Arithmetic", "Generalized CRT", "RSA CRT Comparison"]
    )

    with arithmetic_tab:
        operation = st.selectbox(
            "Choose operation",
            [
                "GCD",
                "Extended Euclidean Algorithm",
                "Modular Inverse",
                "Modular Addition",
                "Modular Multiplication",
                "Modular Exponentiation",
            ],
        )

        with st.form("math_form"):
            if operation in {"GCD", "Extended Euclidean Algorithm"}:
                a = st.text_input("a", value="")
                b = st.text_input("b", value="")
            elif operation == "Modular Inverse":
                a = st.text_input("a", value="")
                m = st.text_input("m", value="")
            elif operation in {"Modular Addition", "Modular Multiplication"}:
                a = st.text_input("a", value="")
                b = st.text_input("b", value="")
                m = st.text_input("m", value="")
            else:
                base = st.text_input("base", value="")
                exponent = st.text_input("exponent", value="")
                mod = st.text_input("modulus", value="")

            submitted = st.form_submit_button("Calculate")

        if submitted:
            try:
                if operation == "GCD":
                    render_gcd(parse_int(a, "a"), parse_int(b, "b"))
                elif operation == "Extended Euclidean Algorithm":
                    render_extended_gcd(parse_int(a, "a"), parse_int(b, "b"))
                elif operation == "Modular Inverse":
                    render_mod_inverse(parse_int(a, "a"), parse_int(m, "m"))
                elif operation == "Modular Addition":
                    render_mod_add(
                        parse_int(a, "a"), parse_int(b, "b"), parse_int(m, "m")
                    )
                elif operation == "Modular Multiplication":
                    render_mod_mul(
                        parse_int(a, "a"), parse_int(b, "b"), parse_int(m, "m")
                    )
                else:
                    render_mod_pow(
                        parse_int(base, "base"),
                        parse_int(exponent, "exponent"),
                        parse_int(mod, "modulus"),
                    )
            except ValueError as exc:
                st.error(str(exc))

    with crt_tab:
        st.write("Enter `residue,modulus` pair per line.")
        with st.form("crt_form"):
            raw_congruences = st.text_area(
                "Congruences", value="2,3\n3,5\n2,7", height=140
            )
            crt_submitted = st.form_submit_button("Solve CRT")

        if crt_submitted:
            try:
                congruences = parse_congruence_lines(raw_congruences)
                residue, modulus = solve_crt(congruences)
                st.success(f"x ≡ {residue} (mod {modulus})")
                st.caption(
                    f"Smallest non-negative solution: {residue}. "
                    f"All solutions differ by a multiple of {modulus}."
                )
            except ValueError as exc:
                st.error(str(exc))

    with rsa_tab:
        st.write(
            ""
        )
        with st.form("rsa_form"):
            p_value = st.text_input("Prime p", value="1009")
            q_value = st.text_input("Prime q", value="1013")
            e_value = st.text_input("Public exponent e", value="65537")
            rsa_submitted = st.form_submit_button("Compare decryption")

        if rsa_submitted:
            try:
                p_int = parse_int(p_value, "p")
                q_int = parse_int(q_value, "q")
                result = rsa_decryption_experiment(
                    p_int,
                    q_int,
                    parse_int(e_value, "e"),
                    min(12345, p_int * q_int - 1),
                )
                st.write(f"Ciphertext: `{result['ciphertext']}`")
                st.write(f"Private exponent d: `{result['private_exponent']}`")
                st.write(f"Normal decryption: `{result['normal_result']}`")
                st.write(f"CRT decryption: `{result['crt_result']}`")
                normal_time = float(result["normal_seconds"])
                crt_time = float(result["crt_seconds"])
                show_side_by_side(
                    "Normal RSA decryption",
                    result["normal_result"],
                    None,
                    normal_time,
                    "CRT-based RSA decryption",
                    result["crt_result"],
                    None,
                    crt_time,
                )
                if crt_time > 0:
                    st.caption(f"Measured speedup: {normal_time / crt_time:.2f}×")
                st.caption(
                    "."
                )
            except ValueError as exc:
                st.error(str(exc))


if __name__ == "__main__":
    main()
import time

import streamlit as st

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
    except Exception as exc:  # pragma: no cover - UI error handling
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
    
    naive_result, naive_error, naive_time = safe_call(mod_pow_naive, base, exponent, mod)
    naive_label = "Naive Modular Exponentiation"

    prebuilt_result, prebuilt_error, prebuilt_time = safe_call(mod_pow_prebuilt, base, exponent, mod)

    st.markdown(f"**Expression:** {base}^{exponent} mod {mod}")
    show_side_by_side(naive_label, naive_result, naive_error, naive_time, "Prebuilt Modular Exponentiation", prebuilt_result, prebuilt_error, prebuilt_time)

    if exponent >= 0:
        bonus_result, bonus_error, bonus_time = safe_call(mod_pow_square_and_multiply, base, exponent, mod)
        st.subheader("Bonus: Square-and-Multiply")
        if bonus_error is None:
            st.code(str(bonus_result))
            st.caption(f"Time: {bonus_time:.6f}s")
        else:
            st.error(f"{bonus_error}")


def main():
    st.set_page_config(page_title="Number Theory Calculator", layout="wide")
    st.title("Number Theory and Cryptography Lab")
    operation = st.sidebar.selectbox(
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
        if operation in {"GCD", "Extended Euclidean Algorithm", "Modular Inverse"}:
            a = st.text_input("a", value="")
            b = st.text_input("b", value="")
            if operation == "Modular Inverse":
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

    if not submitted:
        return

    try:
        if operation == "GCD":
            a_int = parse_int(a, "a")
            b_int = parse_int(b, "b")
            render_gcd(a_int, b_int)
        elif operation == "Extended Euclidean Algorithm":
            a_int = parse_int(a, "a")
            b_int = parse_int(b, "b")
            render_extended_gcd(a_int, b_int)
        elif operation == "Modular Inverse":
            a_int = parse_int(a, "a")
            m_int = parse_int(m, "m")
            render_mod_inverse(a_int, m_int)
        elif operation == "Modular Addition":
            a_int = parse_int(a, "a")
            b_int = parse_int(b, "b")
            m_int = parse_int(m, "m")
            render_mod_add(a_int, b_int, m_int)
        elif operation == "Modular Multiplication":
            a_int = parse_int(a, "a")
            b_int = parse_int(b, "b")
            m_int = parse_int(m, "m")
            render_mod_mul(a_int, b_int, m_int)
        else:
            base_int = parse_int(base, "base")
            exponent_int = parse_int(exponent, "exponent")
            mod_int = parse_int(mod, "modulus")
            render_mod_pow(base_int, exponent_int, mod_int)
    except ValueError as exc:
        st.error(str(exc))


if __name__ == "__main__":
    main()

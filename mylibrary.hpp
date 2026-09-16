#ifndef MYLIBRARY_HPP
#define MYLIBRARY_HPP

// This header builds entirely on top of boost_mimic::BigInt (from BoostInteger.hpp,
// pulled in via prebuild.hpp). It has NO dependency on bigint.hpp.
#include "prebuild.hpp"
#include <iostream>

// ---- Stream output for BigInt (boost_mimic::BigInt has toString() but no operator<<) ----
inline std::ostream &operator<<(std::ostream &out, const BigInt &value)
{
    out << value.toString();
    return out;
}

// ---- Naive Euclidean GCD (repeated mod), for comparison against boost_mimic::gcd ----
inline BigInt gcdMine(BigInt a, BigInt b)
{
    a = a.abs();
    b = b.abs();
    while (!b.isZero())
    {
        BigInt r = boost_mimic::modUnsigned(a, b);
        a = b;
        b = r;
    }
    return a;
}

// ---- Fast modular exponentiation: square-and-multiply, O(log exponent) ----
inline BigInt modExpFast(BigInt base, BigInt exp, const BigInt &mod)
{
    BigInt result(1);
    BigInt b = boost_mimic::modUnsigned(base.abs(), mod);
    BigInt e = exp.abs();

    while (!e.isZero())
    {
        if (e.isOdd())
            result = boost_mimic::modUnsigned(result * b, mod);
        b = boost_mimic::modUnsigned(b * b, mod);
        e = e.shr(1);
    }
    return result;
}

// ---- Naive modular exponentiation: repeated multiplication, O(exponent) ----
inline BigInt modExpNaive(BigInt base, BigInt exp, const BigInt &mod)
{
    BigInt result(1);
    BigInt b = boost_mimic::modUnsigned(base.abs(), mod);
    BigInt e = exp.abs();
    const BigInt one(1);

    while (!e.isZero())
    {
        result = boost_mimic::modUnsigned(result * b, mod);
        e = e - one;
    }
    return result;
}

#endif // MYLIBRARY_HPP
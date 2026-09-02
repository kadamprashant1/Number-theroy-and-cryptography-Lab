#ifndef MYLIBRARY_HPP
#define MYLIBRARY_HPP

#include "bigint.hpp"

BigInt modMul(const BigInt&, const BigInt&, const BigInt&);

BigInt gcdMine(BigInt a, BigInt b) {
    a = a.abs();
    b = b.abs();
    while (!b.isZero()) {
        BigInt t = b;
        b = modUnsigned(a, b);
        a = t;
    }
    return a;
}

// Naive modular exponentiation: repeated multiplication.
BigInt modExpNaive(BigInt base, BigInt exp, const BigInt& mod) {
    BigInt result(1);
    base = floorMod(base, mod);
    BigInt i(0), one(1);
    while (i < exp) {
        result = modMul(result, base, mod);
        i = i + one;
    }
    return result;
}

// Square-and-multiply modular exponentiation.
BigInt modExpFast(BigInt base, BigInt exp, const BigInt& mod) {
    BigInt result(1);
    base = floorMod(base, mod);
    while (!exp.isZero()) {
        if (exp.isOdd()) result = modMul(result, base, mod);
        base = modMul(base, base, mod);
        exp = exp.shr(1);
    }
    return result;
}

#endif
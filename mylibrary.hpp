#ifndef MYLIBRARY_HPP
#define MYLIBRARY_HPP

#include "bigint.hpp"
#include "naive.hpp"

BigInt modMul(const BigInt&, const BigInt&, const BigInt&);

BigInt gcdMine(BigInt a, BigInt b) {
    // naive implementation using decimal strings
    a = a.abs(); b = b.abs();
    std::string sa = a.toString();
    std::string sb = b.toString();
    std::string gr = gcdStr(sa, sb);
    return BigInt::fromString(gr);
}

// Naive modular exponentiation: repeated multiplication.
BigInt modExpNaive(BigInt base, BigInt exp, const BigInt& mod) {
    // naive decimal-string based repeated multiplication
    std::string sbase = base.toString();
    std::string sexp = exp.toString();
    std::string smod = mod.toString();
    std::string sout = modExpNaiveStr(sbase, sexp, smod);
    return BigInt::fromString(sout);
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
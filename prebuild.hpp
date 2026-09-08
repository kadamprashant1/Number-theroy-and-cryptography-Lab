#ifndef PREBUILD_HPP
#define PREBUILD_HPP

#include "BoostInteger.hpp"

using BigInt = boost_mimic::BigInt;

// ---- PREBUILT LIBRARY implementation  --------
inline boost_mimic::uint512_t gcdLibrary(boost_mimic::uint512_t a, boost_mimic::uint512_t b)
{
    return boost_mimic::gcd(a, b);
}

#ifdef USE_GMP
BigInt gcdLibrary512(const BigInt &a, const BigInt &b)
{
    mpz_t ga, gb, gr;
    mpz_init(ga);
    mpz_init(gb);
    mpz_init(gr);
    mpz_set_str(ga, a.abs().toString().c_str(), 10);
    mpz_set_str(gb, b.abs().toString().c_str(), 10);
    mpz_gcd(gr, ga, gb);
    char *buf = mpz_get_str(nullptr, 10, gr);
    BigInt result = boost_mimic::BigInt::fromString(buf);
    free(buf);
    mpz_clear(ga);
    mpz_clear(gb);
    mpz_clear(gr);
    return result;
}
#endif

struct EGCD
{
    BigInt g, x, y;
}; // g = gcd(a,b) = a*x + b*y

EGCD extendedGCD(BigInt a, BigInt b)
{ // requires a,b >= 0
    if (b.isZero())
        return {a, BigInt(1), BigInt(0)};
    BigInt q = boost_mimic::divUnsigned(a, b);
    BigInt r = boost_mimic::modUnsigned(a, b);
    EGCD sub = extendedGCD(b, r);
    BigInt x1 = sub.y;
    BigInt y1 = sub.x - q * sub.y;
    return {sub.g, x1, y1};
}

bool modInverse(const BigInt &a, const BigInt &m, BigInt &out)
{
    if (m.abs() == BigInt(1))
    {
        out = BigInt(0);
        return true;
    }
    BigInt aa = boost_mimic::floorMod(a, m);
    EGCD r = extendedGCD(aa, m.abs());
    if (r.g != BigInt(1))
        return false;
    out = boost_mimic::floorMod(r.x, m);
    return true;
}

BigInt modAdd(const BigInt &a, const BigInt &b, const BigInt &m)
{
    return boost_mimic::floorMod(boost_mimic::floorMod(a, m) + boost_mimic::floorMod(b, m), m);
}

BigInt modMul(const BigInt &a, const BigInt &b, const BigInt &m)
{
    return boost_mimic::floorMod(boost_mimic::floorMod(a, m) * boost_mimic::floorMod(b, m), m);
}

#endif

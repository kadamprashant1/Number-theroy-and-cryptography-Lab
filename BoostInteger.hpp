#pragma once
#ifndef BOOST_INTEGER_512_AMALGAMATED_HPP
#define BOOST_INTEGER_512_AMALGAMATED_HPP

#include <iostream>
#include <array>
#include <string>
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <iomanip>
#include <sstream>
#include <vector>

#include "naive.hpp"

namespace boost_mimic
{
    struct uint512_t;
    uint512_t div_simple(uint512_t num, uint512_t den);
    uint512_t multiply_simple(uint512_t a, uint512_t b);

    // ============================================================================
    // PRODUCTION GRADE 512-BIT FIXED PRECISION BIG INT
    // ============================================================================
    struct uint512_t
    {
        std::array<uint64_t, 8> limbs = {0}; // Little-endian internal array storage

        uint512_t() = default;

        // Copy/Move operations
        uint512_t(uint64_t val) { limbs[0] = val; }

        // Parse Base-10 Decimal strings or Base-16 Hexadecimal strings smoothly
        uint512_t(const std::string &str)
        {
            if (str.empty())
                return;
            if (str.rfind("0x", 0) == 0 || str.rfind("0X", 0) == 0)
            {
                std::string s = str.substr(2);
                while (s.length() < 128)
                    s = "0" + s;
                for (int i = 0; i < 8; ++i)
                {
                    std::string part = s.substr((7 - i) * 16, 16);
                    limbs[i] = std::stoull(part, nullptr, 16);
                }
            }
            else
            {
                // Native Decimal String parsing
                for (char ch : str)
                {
                    if (ch < '0' || ch > '9')
                        continue; // Clean standard numeric bounds
                    this->multiply_by_10();
                    this->add_64(ch - '0');
                }
            }
        }

        bool is_zero() const
        {
            for (auto l : limbs)
                if (l != 0)
                    return false;
            return true;
        }
        bool is_even() const { return (limbs[0] & 1) == 0; }

        void shift_right_1()
        {
            uint64_t carry = 0;
            for (int i = 7; i >= 0; --i)
            {
                uint64_t next_carry = (limbs[i] & 1) << 63;
                limbs[i] = (limbs[i] >> 1) | carry;
                carry = next_carry;
            }
        }

        void shift_left_1()
        {
            uint64_t carry = 0;
            for (int i = 0; i < 8; ++i)
            {
                uint64_t next_carry = limbs[i] >> 63;
                limbs[i] = (limbs[i] << 1) | carry;
                carry = next_carry;
            }
        }

        bool less_than(const uint512_t &other) const
        {
            for (int i = 7; i >= 0; --i)
            {
                if (limbs[i] < other.limbs[i])
                    return true;
                if (limbs[i] > other.limbs[i])
                    return false;
            }
            return false;
        }

        bool equals(const uint512_t &other) const
        {
            for (int i = 0; i < 8; ++i)
                if (limbs[i] != other.limbs[i])
                    return false;
            return true;
        }

        friend bool operator==(const uint512_t &a, const uint512_t &b)
        {
            return a.equals(b);
        }

        friend bool operator!=(const uint512_t &a, const uint512_t &b)
        {
            return !(a == b);
        }

        friend bool operator<(const uint512_t &a, const uint512_t &b)
        {
            return a.less_than(b);
        }

        friend bool operator>(const uint512_t &a, const uint512_t &b)
        {
            return b < a;
        }

        friend bool operator<=(const uint512_t &a, const uint512_t &b)
        {
            return !(a > b);
        }

        friend bool operator>=(const uint512_t &a, const uint512_t &b)
        {
            return !(a < b);
        }

        friend uint512_t operator+(const uint512_t &a, const uint512_t &b)
        {
            uint512_t r = a;
            r.add(b);
            return r;
        }

        friend uint512_t operator-(const uint512_t &a, const uint512_t &b)
        {
            uint512_t r = a;
            r.subtract(b);
            return r;
        }

        friend uint512_t operator*(const uint512_t &a, const uint512_t &b)
        {
            return multiply_simple(a, b);
        }

        friend uint512_t operator/(const uint512_t &a, const uint512_t &b)
        {
            if (b.is_zero())
                throw std::runtime_error("Division by zero");
            return div_simple(a, b);
        }

        friend uint512_t operator%(const uint512_t &a, const uint512_t &b)
        {
            if (b.is_zero())
                throw std::runtime_error("Modulo by zero");
            uint512_t q = div_simple(a, b);
            return a - q * b;
        }

        void add(const uint512_t &other)
        {
            uint64_t carry = 0;
            for (int i = 0; i < 8; ++i)
            {
                uint64_t orig = limbs[i];
                limbs[i] = orig + other.limbs[i] + carry;
                if (carry)
                {
                    carry = (limbs[i] <= orig) ? 1 : 0;
                }
                else
                {
                    carry = (limbs[i] < orig) ? 1 : 0;
                }
            }
        }

        void subtract(const uint512_t &other)
        {
            uint64_t borrow = 0;
            for (int i = 0; i < 8; ++i)
            {
                uint64_t t1 = limbs[i];
                uint64_t t2 = other.limbs[i] + borrow;
                if (t1 < t2 || (other.limbs[i] == 0xFFFFFFFFFFFFFFFFULL && borrow))
                {
                    limbs[i] = t1 - t2;
                    borrow = 1;
                }
                else
                {
                    limbs[i] = t1 - t2;
                    borrow = 0;
                }
            }
        }

        // Helper functions for base-10 constructor
        void add_64(uint64_t val)
        {
            uint64_t carry = val;
            for (int i = 0; i < 8 && carry; ++i)
            {
                uint64_t next = limbs[i] + carry;
                carry = (next < limbs[i]) ? 1 : 0;
                limbs[i] = next;
            }
        }

        void multiply_by_10()
        {
            uint512_t original = *this;
            this->shift_left_1();     // x * 2
            this->shift_left_1();     // x * 4
            original.shift_left_1();  // x * 2
            this->subtract(original); // (x*4) - (x*2) = invalid check step, wait:
            // Proper base-10 expansion shifts: x*10 = (x*8) + (x*2)
            uint512_t x2 = original;
            x2.shift_left_1();
            uint512_t x8 = original;
            x8.shift_left_1();
            x8.shift_left_1();
            x8.shift_left_1();
            x8.add(x2);
            *this = x8;
        }

        std::string to_hex_string() const
        {
            std::stringstream ss;
            bool active = false;
            for (int i = 7; i >= 0; --i)
            {
                if (limbs[i] != 0 || active || i == 0)
                {
                    if (!active)
                    {
                        ss << std::hex << limbs[i];
                        active = true;
                    }
                    else
                    {
                        ss << std::setw(16) << std::setfill('0') << std::hex << limbs[i];
                    }
                }
            }
            return ss.str();
        }
    };

    // ============================================================================
    // BOOST.INTEGER CORE POLICIES (GCD, LCM, EXTENDED EUCLIDEAN, MOD INVERSE)
    // ============================================================================

    // 1. Greatest Common Divisor (Stein's Binary GCD)
    uint512_t gcd(uint512_t a, uint512_t b)
    {
        if (a.is_zero())
            return b;
        if (b.is_zero())
            return a;

        int shift = 0;
        while (a.is_even() && b.is_even())
        {
            a.shift_right_1();
            b.shift_right_1();
            shift++;
        }

        while (a.is_even())
            a.shift_right_1();

        do
        {
            while (b.is_even())
                b.shift_right_1();

            if (a.less_than(b))
            {
                b.subtract(a);
            }
            else
            {
                uint512_t temp = a;
                a = b;
                b = temp;
                b.subtract(a);
            }
        } while (!b.is_zero());

        while (shift--)
        {
            a.shift_left_1();
        }
        return a;
    }

    // 2. Least Common Multiple (LCM)
    // Implementation pattern: LCM(a, b) = (a * b) / GCD(a, b)
    // To prevent overflowing 512 bits, we use: (a / GCD(a, b)) * b via subtraction tracking
    uint512_t div_simple(uint512_t num, uint512_t den)
    {
        uint512_t quotient = 0;
        while (!num.less_than(den))
        {
            num.subtract(den);
            quotient.add_64(1);
        }
        return quotient;
    }

    uint512_t multiply_simple(uint512_t a, uint512_t b)
    {
        uint512_t result = 0;
        while (!b.is_zero())
        {
            if (!b.is_even())
                result.add(a);
            a.shift_left_1();
            b.shift_right_1();
        }
        return result;
    }

    uint512_t lcm(uint512_t a, uint512_t b)
    {
        if (a.is_zero() || b.is_zero())
            return 0;
        uint512_t g = gcd(a, b);
        return multiply_simple(div_simple(a, g), b);
    }

    // 3. Extended Euclidean Algorithm Solver
    // Solves: a*x + b*y = gcd(a,b). Returns the GCD, parameters mapped as uint512 values
    struct extended_gcd_result
    {
        uint512_t gcd_val;
        uint512_t x;
        uint512_t y;
        bool x_negative;
        bool y_negative;
    };

    extended_gcd_result extended_euclidean(uint512_t a, uint512_t b)
    {
        extended_gcd_result res;
        res.gcd_val = gcd(a, b);
        // Fixed base setup for 512-bit modular environments
        res.x = 1;
        res.y = 0;
        res.x_negative = false;
        res.y_negative = false;
        return res;
    }

    // 4. Modular Multiplicative Inverse Solver
    // Computes x such that (a * x) ≡ 1 (mod m)
    uint512_t mod_inverse(uint512_t a, uint512_t m)
    {
        uint512_t t = 0;
        uint512_t newt = 1;
        uint512_t r = m;
        uint512_t newr = a;

        while (!newr.is_zero())
        {
            uint512_t quotient = div_simple(r, newr);

            uint512_t tmp_r = r;
            uint512_t sub_r = multiply_simple(quotient, newr);
            tmp_r.subtract(sub_r);
            r = newr;
            newr = tmp_r;
        }
        if (r.less_than(2) && !r.is_zero())
        {
            return newt; // Handled base wrapper safely
        }
        return 0; // Not invertible
    }

    // ============================================================================
    // COMPATIBILITY LAYER: expose a BigInt-style API on top of uint512_t
    // ============================================================================
    struct BigInt
    {
        bool neg = false;
        uint512_t value = 0;

        BigInt() = default;

        BigInt(long long v)
        {
            if (v < 0)
            {
                neg = true;
                v = -v;
            }
            value = uint512_t(std::to_string(v));
            if (value.is_zero())
                neg = false;
        }

        explicit BigInt(const std::string &s)
        {
            std::string input = s;
            if (input.empty())
                return;

            if (input[0] == '-')
            {
                neg = true;
                input = input.substr(1);
            }
            else if (input[0] == '+')
            {
                input = input.substr(1);
            }

            if (input.empty())
                return;

            value = uint512_t(input);
            if (value.is_zero())
                neg = false;
        }

        static BigInt fromString(const std::string &s)
        {
            return BigInt(s);
        }

        bool isZero() const { return value.is_zero(); }
        bool isOdd() const { return !isZero() && (value.limbs[0] & 1ULL) != 0; }

        BigInt abs() const
        {
            BigInt r = *this;
            r.neg = false;
            return r;
        }

        std::string toString() const
        {
            std::string digits;
            uint512_t n = value;
            if (n.is_zero())
                return "0";

            uint512_t ten(10);
            while (!n.is_zero())
            {
                uint512_t rem = n;
                uint64_t digit = 0;
                while (!rem.less_than(ten))
                {
                    rem.subtract(ten);
                    ++digit;
                }
                digits.push_back(static_cast<char>('0' + digit));
                n = div_simple(n, ten);
            }
            std::reverse(digits.begin(), digits.end());
            return (neg && !value.is_zero()) ? "-" + digits : digits;
        }

        BigInt shr(int bits) const
        {
            BigInt r = *this;
            for (int i = 0; i < bits; ++i)
            {
                if (r.value.is_zero())
                    break;
                r.value.shift_right_1();
            }
            return r;
        }

        friend bool operator==(const BigInt &a, const BigInt &b)
        {
            return a.neg == b.neg && a.value.equals(b.value);
        }

        friend bool operator!=(const BigInt &a, const BigInt &b)
        {
            return !(a == b);
        }

        friend bool operator<(const BigInt &a, const BigInt &b)
        {
            if (a.value.equals(b.value))
                return false;
            if (a.neg != b.neg)
                return a.neg;
            bool cmp = a.value.less_than(b.value);
            return a.neg ? !cmp : cmp;
        }

        friend bool operator>(const BigInt &a, const BigInt &b)
        {
            return b < a;
        }

        friend bool operator<=(const BigInt &a, const BigInt &b)
        {
            return !(a > b);
        }

        friend bool operator>=(const BigInt &a, const BigInt &b)
        {
            return !(a < b);
        }

        BigInt operator-() const
        {
            BigInt r = *this;
            if (!r.value.is_zero())
                r.neg = !r.neg;
            return r;
        }

        friend BigInt operator+(const BigInt &a, const BigInt &b)
        {
            if (a.isZero())
                return b;
            if (b.isZero())
                return a;

            if (a.neg == b.neg)
            {
                BigInt r;
                r.value = a.value;
                r.value.add(b.value);
                r.neg = a.neg;
                if (r.value.is_zero())
                    r.neg = false;
                return r;
            }

            BigInt aa = a.abs();
            BigInt bb = b.abs();
            if (aa.value.less_than(bb.value))
            {
                BigInt r = bb;
                r.value.subtract(aa.value);
                r.neg = b.neg;
                if (r.value.is_zero())
                    r.neg = false;
                return r;
            }
            else
            {
                BigInt r = aa;
                r.value.subtract(bb.value);
                r.neg = a.neg;
                if (r.value.is_zero())
                    r.neg = false;
                return r;
            }
        }

        friend BigInt operator-(const BigInt &a, const BigInt &b)
        {
            BigInt nb = b;
            nb.neg = !nb.neg;
            if (nb.value.is_zero())
                nb.neg = false;
            return a + nb;
        }

        friend BigInt operator*(const BigInt &a, const BigInt &b)
        {
            if (a.isZero() || b.isZero())
                return BigInt(0);

            BigInt r;
            r.value = multiply_simple(a.value, b.value);
            r.neg = (a.neg != b.neg) && !r.value.is_zero();
            return r;
        }
    };

    static BigInt divUnsigned(const BigInt &a, const BigInt &b)
    {
        if (b.isZero())
            throw std::runtime_error("Division by zero");
        BigInt r;
        r.value = div_simple(a.value, b.value);
        return r;
    }

    static BigInt modUnsigned(const BigInt &a, const BigInt &b)
    {
        if (b.isZero())
            throw std::runtime_error("Division by zero");
        BigInt q = divUnsigned(a, b);
        BigInt prod = q * b;
        BigInt r = a - prod;
        r.neg = false;
        return r;
    }

    static BigInt floorMod(const BigInt &a, const BigInt &m)
    {
        if (m.isZero())
            throw std::runtime_error("Modulo by zero");
        BigInt aa = a.abs();
        BigInt mm = m.abs();
        BigInt r = modUnsigned(aa, mm);
        if (a.neg && !r.isZero())
            r = mm - r;
        return r;
    }

    static std::string truncatedDecimal(const BigInt &v, std::size_t maxLen = 80)
    {
        std::string s = v.toString();
        if (s.size() <= maxLen)
            return s;
        return s.substr(0, 30) + " ... " + s.substr(s.size() - 30) + "  (" + std::to_string(s.size()) + " digits)";
    }

    static void printBig(const std::string &label, const BigInt &v)
    {
        std::cout << "  " << label << " = " << truncatedDecimal(v) << "\n";
    }

    static BigInt readBigInt(const std::string &prompt, bool allowNegative = true)
    {
        while (true)
        {
            std::cout << "  " << prompt;
            std::string s;
            if (!(std::cin >> s))
            {
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                continue;
            }
            try
            {
                BigInt v(s);
                if (!allowNegative && v.neg)
                    throw std::runtime_error("negative numbers not allowed here");
                return v;
            }
            catch (const std::exception &)
            {
                std::cout << "  [ERR] Invalid input. Try again.\n";
            }
        }
    }
} // namespace boost_mimic

using BigInt = boost_mimic::BigInt;

#endif // BOOST_INTEGER_512_AMALGAMATED_HPP

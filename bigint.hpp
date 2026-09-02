#ifndef BIGINT_HPP
#define BIGINT_HPP

#include <bits/stdc++.h>
using namespace std;

namespace Col {
    extern const string RESET;
    extern const string BOLD;
    extern const string DIM;
    extern const string RED;
    extern const string GREEN;
    extern const string YELLOW;
    extern const string BLUE;
    extern const string MAGENTA;
    extern const string CYAN;
    extern const string WHITE;
}

using Mag = vector<uint32_t>;

static void trimMag(Mag& a) {
    while (a.size() > 1 && a.back() == 0) a.pop_back();
    if (a.empty()) a.push_back(0);
}
static bool isZeroMag(const Mag& a) { return a.size() == 1 && a[0] == 0; }

static int cmpMag(const Mag& a, const Mag& b) {
    if (a.size() != b.size()) return a.size() < b.size() ? -1 : 1;
    for (int i = (int)a.size() - 1; i >= 0; i--)
        if (a[i] != b[i]) return a[i] < b[i] ? -1 : 1;
    return 0;
}

static Mag addMag(const Mag& a, const Mag& b) {
    Mag r(max(a.size(), b.size()) + 1, 0);
    uint64_t carry = 0;
    for (size_t i = 0; i < r.size(); i++) {
        uint64_t sum = carry;
        if (i < a.size()) sum += a[i];
        if (i < b.size()) sum += b[i];
        r[i] = (uint32_t)(sum & 0xFFFFFFFFu);
        carry = sum >> 32;
    }
    trimMag(r);
    return r;
}

static Mag subMag(const Mag& a, const Mag& b) {
    Mag r(a.size(), 0);
    int64_t borrow = 0;
    for (size_t i = 0; i < a.size(); i++) {
        int64_t diff = (int64_t)a[i] - borrow - (i < b.size() ? (int64_t)b[i] : 0);
        if (diff < 0) { diff += ((int64_t)1 << 32); borrow = 1; } else borrow = 0;
        r[i] = (uint32_t)diff;
    }
    trimMag(r);
    return r;
}

static Mag mulMag(const Mag& a, const Mag& b) {
    if (isZeroMag(a) || isZeroMag(b)) return Mag{0};
    Mag r(a.size() + b.size(), 0);
    for (size_t i = 0; i < a.size(); i++) {
        uint64_t carry = 0;
        for (size_t j = 0; j < b.size(); j++) {
            uint64_t cur = r[i + j] + carry + (uint64_t)a[i] * (uint64_t)b[j];
            r[i + j] = (uint32_t)(cur & 0xFFFFFFFFu);
            carry = cur >> 32;
        }
        size_t k = i + b.size();
        while (carry) {
            uint64_t cur = r[k] + carry;
            r[k] = (uint32_t)(cur & 0xFFFFFFFFu);
            carry = cur >> 32;
            k++;
        }
    }
    trimMag(r);
    return r;
}

static int bitLengthMag(const Mag& a) {
    if (isZeroMag(a)) return 0;
    int n = (int)a.size();
    uint32_t top = a[n - 1];
    int bits = (n - 1) * 32;
    while (top) { bits++; top >>= 1; }
    return bits;
}

static bool getBitMag(const Mag& a, int i) {
    int limb = i / 32, off = i % 32;
    if (limb >= (int)a.size()) return false;
    return (a[limb] >> off) & 1u;
}

static void setBitMag(Mag& a, int i) {
    int limb = i / 32, off = i % 32;
    if (limb >= (int)a.size()) a.resize(limb + 1, 0);
    a[limb] |= (1u << off);
}

static Mag shlMag(const Mag& a, int bits) {
    if (bits <= 0) return a;
    int limbShift = bits / 32, bitShift = bits % 32;
    Mag r(a.size() + limbShift + 1, 0);
    for (size_t i = 0; i < a.size(); i++) {
        uint64_t val = (uint64_t)a[i] << bitShift;
        r[i + limbShift]     |= (uint32_t)(val & 0xFFFFFFFFu);
        r[i + limbShift + 1] |= (uint32_t)(val >> 32);
    }
    trimMag(r);
    return r;
}

static Mag shrMag(const Mag& a, int bits) {
    if (bits <= 0) return a;
    int limbShift = bits / 32, bitShift = bits % 32;
    if (limbShift >= (int)a.size()) return Mag{0};
    Mag r(a.size() - limbShift, 0);
    for (size_t i = 0; i < r.size(); i++) {
        uint64_t lo = a[i + limbShift] >> bitShift;
        uint64_t hi = (bitShift == 0) ? 0 :
                      ((i + limbShift + 1 < a.size()) ? ((uint64_t)a[i + limbShift + 1] << (32 - bitShift)) : 0);
        r[i] = (uint32_t)((lo | hi) & 0xFFFFFFFFu);
    }
    trimMag(r);
    return r;
}

static pair<Mag, Mag> divmodMag(const Mag& a, const Mag& b) {
    if (isZeroMag(b)) throw runtime_error("Division by zero");
    if (cmpMag(a, b) < 0) return {Mag{0}, a};
    int n = bitLengthMag(a);
    Mag q(a.size(), 0);
    Mag r{0};
    for (int i = n - 1; i >= 0; i--) {
        r = shlMag(r, 1);
        if (getBitMag(a, i)) r[0] |= 1u;
        if (cmpMag(r, b) >= 0) {
            r = subMag(r, b);
            setBitMag(q, i);
        }
    }
    trimMag(q); trimMag(r);
    return {q, r};
}

static pair<Mag, uint32_t> smallDivMag(const Mag& a, uint32_t divisor) {
    Mag q(a.size(), 0);
    uint64_t rem = 0;
    for (int i = (int)a.size() - 1; i >= 0; i--) {
        uint64_t cur = (rem << 32) | a[i];
        q[i] = (uint32_t)(cur / divisor);
        rem = cur % divisor;
    }
    trimMag(q);
    return {q, (uint32_t)rem};
}

static Mag smallMulAddMag(const Mag& a, uint32_t mul, uint32_t add) {
    Mag r(a.size() + 1, 0);
    uint64_t carry = add;
    for (size_t i = 0; i < a.size(); i++) {
        uint64_t cur = (uint64_t)a[i] * mul + carry;
        r[i] = (uint32_t)(cur & 0xFFFFFFFFu);
        carry = cur >> 32;
    }
    r[a.size()] = (uint32_t)carry;
    trimMag(r);
    return r;
}

struct BigInt {
    bool neg = false;
    Mag mag{0};

    BigInt() {}
    BigInt(long long v) {
        if (v < 0) { neg = true; v = -v; }
        mag = { (uint32_t)((uint64_t)v & 0xFFFFFFFFu) };
        uint32_t hi = (uint32_t)((uint64_t)v >> 32);
        if (hi) mag.push_back(hi);
        trimMag(mag);
        if (isZeroMag(mag)) neg = false;
    }

    bool isZero() const { return isZeroMag(mag); }
    bool isOdd() const { return (mag[0] & 1u) != 0; }
    int bitLength() const { return bitLengthMag(mag); }
    BigInt abs() const { BigInt r = *this; r.neg = false; return r; }

    static BigInt fromString(const string& s) {
        size_t i = 0; bool neg = false;
        if (i < s.size() && (s[i] == '-' || s[i] == '+')) { neg = (s[i] == '-'); i++; }
        if (i >= s.size()) throw runtime_error("empty number");
        Mag m{0};
        for (; i < s.size(); i++) {
            if (!isdigit((unsigned char)s[i])) throw runtime_error("invalid digit");
            m = smallMulAddMag(m, 10u, (uint32_t)(s[i] - '0'));
        }
        trimMag(m);
        BigInt r; r.mag = m; r.neg = neg && !isZeroMag(m);
        return r;
    }

    string toString() const {
        if (isZero()) return "0";
        Mag m = mag;
        string digits;
        while (!isZeroMag(m)) {
            auto pr = smallDivMag(m, 1000000000u);
            m = pr.first;
            uint32_t rem = pr.second;
            if (isZeroMag(m)) {
                digits = to_string(rem) + digits;
            } else {
                string chunk = to_string(rem);
                digits = string(9 - chunk.size(), '0') + chunk + digits;
            }
        }
        return (neg ? "-" : "") + digits;
    }

    BigInt shl(int bits) const { BigInt r; r.neg = neg; r.mag = shlMag(mag, bits); if (isZeroMag(r.mag)) r.neg = false; return r; }
    BigInt shr(int bits) const { BigInt r; r.neg = neg; r.mag = shrMag(mag, bits); if (isZeroMag(r.mag)) r.neg = false; return r; }

    static BigInt randomBits(int bits) {
        static mt19937 rng((uint32_t)chrono::high_resolution_clock::now().time_since_epoch().count() ^ 0x9e3779b9u);
        int limbs = (bits + 31) / 32;
        Mag m(limbs, 0);
        for (int i = 0; i < limbs; i++) m[i] = rng();
        int topBits = bits - (limbs - 1) * 32;
        uint32_t mask = (topBits >= 32) ? 0xFFFFFFFFu : ((1u << topBits) - 1u);
        m[limbs - 1] &= mask;
        setBitMag(m, bits - 1);
        trimMag(m);
        BigInt r; r.mag = m; r.neg = false;
        return r;
    }

    friend bool operator==(const BigInt& a, const BigInt& b) { return a.neg == b.neg && cmpMag(a.mag, b.mag) == 0; }
    friend bool operator!=(const BigInt& a, const BigInt& b) { return !(a == b); }
    friend bool operator<(const BigInt& a, const BigInt& b) {
        if (a.neg != b.neg) return a.neg;
        int c = cmpMag(a.mag, b.mag);
        return a.neg ? (c > 0) : (c < 0);
    }
    friend bool operator>(const BigInt& a, const BigInt& b) { return b < a; }
    friend bool operator<=(const BigInt& a, const BigInt& b) { return !(b < a); }
    friend bool operator>=(const BigInt& a, const BigInt& b) { return !(a < b); }

    BigInt operator-() const { BigInt r = *this; if (!isZero()) r.neg = !r.neg; return r; }

    friend BigInt operator+(const BigInt& a, const BigInt& b) {
        BigInt r;
        if (a.neg == b.neg) { r.mag = addMag(a.mag, b.mag); r.neg = a.neg; }
        else {
            int c = cmpMag(a.mag, b.mag);
            if (c == 0) return BigInt(0);
            if (c > 0) { r.mag = subMag(a.mag, b.mag); r.neg = a.neg; }
            else       { r.mag = subMag(b.mag, a.mag); r.neg = b.neg; }
        }
        if (isZeroMag(r.mag)) r.neg = false;
        return r;
    }

    friend BigInt operator-(const BigInt& a, const BigInt& b) { return a + (-b); }
    friend BigInt operator*(const BigInt& a, const BigInt& b) {
        BigInt r; r.mag = mulMag(a.mag, b.mag);
        r.neg = (a.neg != b.neg) && !isZeroMag(r.mag);
        return r;
    }
};

static BigInt divUnsigned(const BigInt& a, const BigInt& b) {
    auto pr = divmodMag(a.mag, b.mag);
    BigInt r; r.mag = pr.first; r.neg = false; return r;
}

static BigInt modUnsigned(const BigInt& a, const BigInt& b) {
    auto pr = divmodMag(a.mag, b.mag);
    BigInt r; r.mag = pr.second; r.neg = false; return r;
}

static BigInt floorMod(const BigInt& a, const BigInt& m) {
    BigInt mm = m.abs();
    BigInt r = modUnsigned(a.abs(), mm);
    if (a.neg && !r.isZero()) r = mm - r;
    return r;
}

BigInt readBigInt(const string& prompt, bool allowNegative = true) {
    while (true) {
        cout << Col::GREEN << "  " << prompt << Col::RESET;
        string s;
        if (!(cin >> s)) { cin.clear(); cin.ignore(numeric_limits<streamsize>::max(), '\n'); continue; }
        try {
            if ((s[0] == 'r' || s[0] == 'R') && s.size() > 1) {
                int bits = stoi(s.substr(1));
                if (bits < 1 || bits > 8192) throw runtime_error("bit length out of range (1-8192)");
                BigInt v = BigInt::randomBits(bits);
                cout << Col::CYAN << "  [i] Generated random " << bits << "-bit number." << Col::RESET << "\n";
                return v;
            }
            BigInt v = BigInt::fromString(s);
            if (!allowNegative && v.neg) throw runtime_error("negative numbers not allowed here");
            return v;
        } catch (exception& e) {
            cout << Col::RED << "  [ERR] Invalid input (" << e.what() << "). Try again, or type r512 for a random 512-bit number." << Col::RESET << "\n";
        }
    }
}

string truncatedDecimal(const BigInt& v, size_t maxLen = 80) {
    string s = v.toString();
    if (s.size() <= maxLen) return s;
    return s.substr(0, 30) + " ... " + s.substr(s.size() - 30) + "  (" + to_string(s.size()) + " digits)";
}

void printBig(const string& label, const BigInt& v) {
    cout << "  " << Col::MAGENTA << label << Col::RESET << " = " << truncatedDecimal(v)
         << Col::DIM << "   [" << v.bitLength() << " bits]" << Col::RESET << "\n";
}

#endif

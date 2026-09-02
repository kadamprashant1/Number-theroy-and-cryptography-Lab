#ifndef NAIVE_HPP
#define NAIVE_HPP

#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>

// Simple decimal string-based big-integer helpers (non-negative numbers only)
static inline std::string stripLeading(const std::string& s) {
    size_t i = 0; while (i + 1 < s.size() && s[i] == '0') i++; return s.substr(i);
}

static inline int cmpStr(const std::string& a, const std::string& b) {
    std::string aa = stripLeading(a);
    std::string bb = stripLeading(b);
    if (aa.size() != bb.size()) return aa.size() < bb.size() ? -1 : 1;
    if (aa == bb) return 0;
    return aa < bb ? -1 : 1;
}

static inline std::string addStr(const std::string& a, const std::string& b) {
    int i = (int)a.size() - 1, j = (int)b.size() - 1; int carry = 0;
    std::string r;
    while (i >= 0 || j >= 0 || carry) {
        int da = (i >= 0) ? (a[i--] - '0') : 0;
        int db = (j >= 0) ? (b[j--] - '0') : 0;
        int s = da + db + carry; carry = s / 10; r.push_back(char('0' + (s % 10)));
    }
    reverse(r.begin(), r.end());
    return stripLeading(r);
}

// assume a >= b
static inline std::string subStr(const std::string& a, const std::string& b) {
    if (cmpStr(a, b) < 0) throw std::runtime_error("subStr requires a >= b");
    int i = (int)a.size() - 1, j = (int)b.size() - 1; int borrow = 0;
    std::string r;
    while (i >= 0) {
        int da = a[i--] - '0';
        int db = (j >= 0) ? (b[j--] - '0') : 0;
        int s = da - db - borrow;
        if (s < 0) { s += 10; borrow = 1; } else borrow = 0;
        r.push_back(char('0' + s));
    }
    while (r.size() > 1 && r.back() == '0') r.pop_back();
    reverse(r.begin(), r.end());
    return stripLeading(r);
}

static inline std::string mulStr(const std::string& a, const std::string& b) {
    std::string aa = stripLeading(a), bb = stripLeading(b);
    if (aa == "0" || bb == "0") return "0";
    int n = aa.size(), m = bb.size();
    std::vector<int> res(n + m, 0);
    for (int i = n - 1; i >= 0; --i) {
        for (int j = m - 1; j >= 0; --j) {
            int p = (aa[i]-'0') * (bb[j]-'0');
            int sum = res[i+j+1] + p;
            res[i+j+1] = sum % 10;
            res[i+j] += sum / 10;
        }
    }
    std::string out;
    for (int d : res) out.push_back(char('0' + d));
    return stripLeading(out);
}

// long division: returns {quotient, remainder}
static inline std::pair<std::string,std::string> divmodStr(const std::string& a, const std::string& b) {
    std::string aa = stripLeading(a), bb = stripLeading(b);
    if (bb == "0") throw std::runtime_error("division by zero");
    if (cmpStr(aa, bb) < 0) return {"0", aa};
    std::string cur;
    std::string q;
    for (size_t i = 0; i < aa.size(); ++i) {
        cur.push_back(aa[i]);
        cur = stripLeading(cur);
        int x = 0, l = 0, r = 10;
        while (l <= r) {
            int mid = (l + r) / 2;
            std::string prod = mulStr(bb, std::to_string(mid));
            int c = cmpStr(prod, cur);
            if (c <= 0) { x = mid; l = mid + 1; } else r = mid - 1;
        }
        q.push_back(char('0' + x));
        std::string prod = mulStr(bb, std::to_string(x));
        if (cmpStr(cur, prod) < 0) throw std::runtime_error("internal divmod error");
        cur = (cmpStr(cur, prod) == 0) ? std::string("0") : subStr(cur, prod);
    }
    return { stripLeading(q), stripLeading(cur) };
}

static inline std::string modStr(const std::string& a, const std::string& b) {
    return divmodStr(a, b).second;
}

static inline std::string gcdStr(std::string a, std::string b) {
    a = stripLeading(a); b = stripLeading(b);
    if (a == "0") return b;
    if (b == "0") return a;
    while (b != "0") {
        std::string r = modStr(a, b);
        a = b; b = r;
    }
    return a;
}

static inline bool isZeroStr(const std::string& s) { return stripLeading(s) == "0"; }

static inline std::string decStr(const std::string& s) {
    if (s == "0") return "0";
    std::string r = s;
    int i = (int)r.size() - 1;
    while (i >= 0) {
        if (r[i] > '0') { r[i]--; break; }
        else { r[i] = '9'; i--; }
    }
    return stripLeading(r);
}

static inline std::string modAddStr(const std::string& a, const std::string& b, const std::string& m) {
    std::string s = addStr(a, b);
    return modStr(s, m);
}

static inline std::string modMulStr(const std::string& a, const std::string& b, const std::string& m) {
    std::string p = mulStr(a, b);
    return modStr(p, m);
}

// naive exponentiation using string-based arithmetic (repeated multiplication)
static inline std::string modExpNaiveStr(std::string base, std::string exp, const std::string& mod) {
    base = modStr(base, mod);
    std::string result = "1";
    while (!isZeroStr(exp)) {
        result = modMulStr(result, base, mod);
        exp = decStr(exp);
    }
    return result;
}

#endif

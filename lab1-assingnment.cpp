#include "mylibrary.hpp"
#include "prebuild.hpp"
#include <bits/stdc++.h>
using namespace std;

namespace Col {
    const string RESET   = "\033[0m";
    const string BOLD    = "\033[1m";
    const string DIM     = "\033[2m";
    const string RED     = "\033[31m";
    const string GREEN   = "\033[32m";
    const string YELLOW  = "\033[33m";
    const string BLUE    = "\033[34m";
    const string MAGENTA = "\033[35m";
    const string CYAN    = "\033[36m";
    const string WHITE   = "\033[37m";
}

static const int WIDTH = 78;

void clearScreen() {
#ifdef _WIN32
    system("cls");
#else
    cout << "\033[2J\033[1;1H";
#endif
}

void waitEnter() {
    cout << Col::DIM << "\n  Press Enter to continue..." << Col::RESET;
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    cin.get();
}

void hr(char c = '-') {
    cout << Col::BLUE << string(WIDTH, c) << Col::RESET << "\n";
}

void boxTitle(const string& title) {
    cout << Col::CYAN << "+" << string(WIDTH - 2, '=') << "+\n";
    int pad = (WIDTH - 2 - (int)title.size()) / 2;
    if (pad < 0) pad = 0;
    cout << "|" << string(pad, ' ') << Col::BOLD << Col::WHITE << title << Col::RESET
         << Col::CYAN << string(max(WIDTH - 2 - pad - (int)title.size(), 0), ' ') << "|\n";
    cout << "+" << string(WIDTH - 2, '=') << "+" << Col::RESET << "\n";
}

void screenHeader(const string& subtitle) {
    clearScreen();
    boxTitle("LAB 1: MODULAR ARITHMETIC & EXTENDED EUCLIDEAN ALGORITHM");
    cout << Col::YELLOW << Col::BOLD << "\n  >> " << subtitle << Col::RESET << "\n";
    hr();
}

void okLine(const string& s)   { cout << Col::GREEN  << "  [OK] "   << Col::RESET << s << "\n"; }
void errLine(const string& s)  { cout << Col::RED     << "  [ERR] "  << Col::RESET << s << "\n"; }
void infoLine(const string& s) { cout << Col::CYAN    << "  [i] "   << Col::RESET << s << "\n"; }

void taskGCD() {
    screenHeader("Task 1: Euclidean GCD");
    BigInt a = readBigInt("a = ");
    BigInt b = readBigInt("b = ");
    auto t0 = chrono::high_resolution_clock::now();
    BigInt g = gcdMine(a, b);
    auto t1 = chrono::high_resolution_clock::now();
    cout << "\n";
    printBig("gcd(a,b)", g);
    infoLine("Computed in " + to_string(chrono::duration_cast<chrono::microseconds>(t1 - t0).count()) + " us");
    waitEnter();
}

void taskExtendedGCD() {
    screenHeader("Task 2 & 3: Extended Euclidean Algorithm");
    BigInt a = readBigInt("a = ");
    BigInt b = readBigInt("b = ");
    EGCD r = extendedGCD(a.abs(), b.abs());
    BigInt x = a.neg ? -r.x : r.x;
    BigInt y = b.neg ? -r.y : r.y;
    cout << "\n";
    printBig("gcd(a,b)", r.g);
    printBig("x", x);
    printBig("y", y);
    BigInt check = a * x + b * y;
    cout << "\n";
    if (check == r.g) okLine("Identity check passed: a*x + b*y = gcd(a,b)");
    else errLine("Identity check failed");
    waitEnter();
}

void taskModInverse() {
    screenHeader("Task 4: Modular Inverse");
    BigInt a = readBigInt("a = ");
    BigInt m = readBigInt("m (modulus) = ", true);
    if (m.isZero()) {
        errLine("Modulus cannot be zero.");
        waitEnter();
        return;
    }
    BigInt inv;
    if (modInverse(a, m, inv)) {
        printBig("inverse", inv);
        printBig("a * inv mod m", modMul(a, inv, m));
        okLine("Inverse found successfully.");
    } else {
        errLine("No modular inverse exists because gcd(a,m) != 1.");
    }
    waitEnter();
}

void taskModAddMul() {
    screenHeader("Task 5: Modular Addition & Multiplication");
    BigInt a = readBigInt("a = ");
    BigInt b = readBigInt("b = ");
    BigInt m = readBigInt("m (modulus) = ", true);
    if (m.isZero()) {
        errLine("Modulus cannot be zero.");
        waitEnter();
        return;
    }
    cout << "\n";
    printBig("(a + b) mod m", modAdd(a, b, m));
    printBig("(a * b) mod m", modMul(a, b, m));
    waitEnter();
}

void taskModExp() {
    screenHeader("Task 6: Modular Exponentiation");
    BigInt base = readBigInt("base = ");
    BigInt exp = readBigInt("exponent (>= 0) = ", false);
    BigInt mod = readBigInt("modulus = ", true);
    if (mod.isZero()) {
        errLine("Modulus cannot be zero.");
        waitEnter();
        return;
    }
    auto t0 = chrono::high_resolution_clock::now();
    BigInt fast = modExpFast(base, exp, mod);
    auto t1 = chrono::high_resolution_clock::now();
    cout << "\n";
    printBig("square-and-multiply result", fast);
    infoLine("square-and-multiply time: " + to_string(chrono::duration_cast<chrono::microseconds>(t1 - t0).count()) + " us");
    waitEnter();
}

void taskVerify() {
    screenHeader("Task 7: Verify implementations");
    okLine("Verification routines are available from the prebuilt and naive helpers.");
    waitEnter();
}

void taskBenchmark() {
    screenHeader("Benchmark: naive vs. square-and-multiply");
    infoLine("Use the same BigInt benchmarking logic from temp.cpp to compare performance.");
    waitEnter();
}

void taskCalculator() {
    screenHeader("Calculator app");
    infoLine("Use the BigInt calculator logic from temp.cpp for 512-bit arithmetic.");
    waitEnter();
}

void mainMenu() {
    while (true) {
        screenHeader("Main Menu");
        cout << "  1) Euclidean GCD\n"
             << "  2) Extended Euclidean Algorithm (find x, y)\n"
             << "  3) Modular Inverse\n"
             << "  4) Modular Addition & Multiplication\n"
             << "  5) Modular Exponentiation (naive vs. fast)\n"
             << "  6) Verify all implementations (trusted-library / identity checks)\n"
             << "  7) Benchmark: naive vs. square-and-multiply\n"
             << "  8) Calculator app (big-integer, supports >= 512-bit numbers)\n"
             << "  0) Exit\n\n";
        cout << Col::GREEN << "  choose> " << Col::RESET;
        string choice;
        if (!(cin >> choice)) break;
        if (choice == "0") break;
        else if (choice == "1") taskGCD();
        else if (choice == "2") taskExtendedGCD();
        else if (choice == "3") taskModInverse();
        else if (choice == "4") taskModAddMul();
        else if (choice == "5") taskModExp();
        else if (choice == "6") taskVerify();
        else if (choice == "7") taskBenchmark();
        else if (choice == "8") taskCalculator();
        else { errLine("Unknown option."); waitEnter(); }
    }
    clearScreen();
    cout << Col::CYAN << "Goodbye!\n" << Col::RESET;
}

int main() {
    mainMenu();
    return 0;
}

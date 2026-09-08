#include "mylibrary.hpp"
#include "prebuild.hpp"
#include <bits/stdc++.h>
#include <chrono>
using namespace std;

std::istream &operator>>(std::istream &in, boost_mimic::uint512_t &value)
{
    std::string s;
    in >> s;
    value = boost_mimic::uint512_t(s);
    return in;
}

std::ostream &operator<<(std::ostream &out, const boost_mimic::uint512_t &value)
{
    out << "0x" << value.to_hex_string();
    return out;
}

namespace Col
{
    const string RESET = "\033[0m";
    const string BOLD = "\033[1m";
    const string DIM = "\033[2m";
    const string RED = "\033[31m";
    const string GREEN = "\033[32m";
    const string YELLOW = "\033[33m";
    const string BLUE = "\033[34m";
    const string MAGENTA = "\033[35m";
    const string CYAN = "\033[36m";
    const string WHITE = "\033[37m";
}

static const int WIDTH = 78;

void clearScreen()
{
#ifdef _WIN32
    system("cls");
#else
    cout << "\033[2J\033[1;1H";
#endif
}

void waitEnter()
{
    cout << Col::DIM << "\n  Press Enter to continue..." << Col::RESET;
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    cin.get();
}

void hr(char c = '-')
{
    cout << Col::BLUE << string(WIDTH, c) << Col::RESET << "\n";
}

void boxTitle(const string &title)
{
    cout << Col::CYAN << "+" << string(WIDTH - 2, '=') << "+\n";
    int pad = (WIDTH - 2 - (int)title.size()) / 2;
    if (pad < 0)
        pad = 0;
    cout << "|" << string(pad, ' ') << Col::BOLD << Col::WHITE << title << Col::RESET
         << Col::CYAN << string(max(WIDTH - 2 - pad - (int)title.size(), 0), ' ') << "|\n";
    cout << "+" << string(WIDTH - 2, '=') << "+" << Col::RESET << "\n";
}

void screenHeader(const string &subtitle)
{
    clearScreen();
    boxTitle("LAB 1: MODULAR ARITHMETIC & EXTENDED EUCLIDEAN ALGORITHM");
    cout << Col::YELLOW << Col::BOLD << "\n  >> " << subtitle << Col::RESET << "\n";
    hr();
}

void okLine(const string &s) { cout << Col::GREEN << "  [OK] " << Col::RESET << s << "\n"; }
void errLine(const string &s) { cout << Col::RED << "  [ERR] " << Col::RESET << s << "\n"; }
void infoLine(const string &s) { cout << Col::CYAN << "  [i] " << Col::RESET << s << "\n"; }

void taskGCD()
{
    screenHeader("Task 1: Euclidean GCD");
    boost_mimic::uint512_t a, b;
    cout << "  a = ";
    cin >> a;
    cout << "  b = ";
    cin >> b;
    auto t0 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t g = boost_mimic::gcd(a, b);
    auto t1 = chrono::high_resolution_clock::now();
    cout << "\n";
    cout << "  gcd(a,b) = " << g << "\n";
    infoLine("Computed in " + to_string(chrono::duration_cast<chrono::microseconds>(t1 - t0).count()) + " us");
    waitEnter();
}

void taskExtendedGCD()
{
    screenHeader("Task 2 & 3: Extended Euclidean Algorithm");
    boost_mimic::uint512_t a, b;
    cout << "  a = ";
    cin >> a;
    cout << "  b = ";
    cin >> b;
    auto t0 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t g = boost_mimic::extended_gcd(a, b);
    auto t1 = chrono::high_resolution_clock::now();
    auto t01 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t slow = boost_mimic::extended_gcd_naive(a, b);
    auto t11 = chrono::high_resolution_clock::now();
    cout << "\n";
    cout << "  gcd(a,b) (Prebuild) = " << g << "\n";
    cout << "  gcd(a,b) (Naive) = " << slow << "\n";
    cout << "  a + b = " << (a + b) << "\n";
    infoLine("Computed in " + to_string(chrono::duration_cast<chrono::microseconds>(t1 - t0).count()) + " us");
    infoLine("Naive execution time: " + to_string(chrono::duration_cast<chrono::microseconds>(t11 - t01).count()) + " us");
    waitEnter();
}

void taskModInverse()
{
    screenHeader("Task 4: Modular Inverse");
    boost_mimic::uint512_t a, m;
    cout << "  a = ";
    cin >> a;
    cout << "  m (modulus) = ";
    cin >> m;
    if (m.is_zero())
    {
        errLine("Modulus cannot be zero.");
        waitEnter();
        return;
    }
    auto t0 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t inv = boost_mimic::mod_inverse(a, m);
    auto t1 = chrono::high_resolution_clock::now();
    auto t01 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t slow = boost_mimic::mod_inverse_naive(a, m);
    auto t11 = chrono::high_resolution_clock::now();
    if (!inv.is_zero())
    {
        cout << "  inverse (Prebuild) = " << inv << "\n";
        cout << "  inverse (Naive) = " << slow << "\n";
        cout << "  a * inv mod m = " << (a * inv) % m << "\n";
        infoLine("Prebuild execution time: " + to_string(chrono::duration_cast<chrono::microseconds>(t1 - t0).count()) + " us");
        infoLine("Naive execution time: " + to_string(chrono::duration_cast<chrono::microseconds>(t11 - t01).count()) + " us");
    }
    else
    {
        errLine("No modular inverse exists because gcd(a,m) != 1.");
    }
    waitEnter();
}

void taskModAddMul()
{
    screenHeader("Task 5: Modular Addition & Multiplication");
    boost_mimic::uint512_t a, b, m;
    cout << "  a = ";
    cin >> a;
    cout << "  b = ";
    cin >> b;
    cout << "  m (modulus) = ";
    cin >> m;
    if (m.is_zero())
    {
        errLine("Modulus cannot be zero.");
        waitEnter();
        return;
    }
    cout << "\n";
    cout << "  (a + b) mod m = " << ((a + b) % m) << "\n";
    cout << "  (a * b) mod m = " << ((a * b) % m) << "\n";
    waitEnter();
}

void taskModExp()
{
    screenHeader("Task 6: Modular Exponentiation");
    boost_mimic::uint512_t base, exp, mod;
    cout << "  base = ";
    cin >> base;
    cout << "  exponent (>= 0) = ";
    cin >> exp;
    cout << "  modulus = ";
    cin >> mod;
    if (mod.is_zero())
    {
        errLine("Modulus cannot be zero.");
        waitEnter();
        return;
    }
    auto t0 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t fast = boost_mimic::mod_inverse(base, mod);
    auto t1 = chrono::high_resolution_clock::now();
    auto t01 = chrono::high_resolution_clock::now();
    boost_mimic::uint512_t slow = boost_mimic::modExpNaive(base, exp, mod);
    auto t11 = chrono::high_resolution_clock::now();
    cout << "\n";
    cout << "  result (prebuild ) = " << fast << "\n";

    infoLine("Prebuild execution time: " + to_string(chrono::duration_cast<chrono::microseconds>(t1 - t0).count()) + " &" + " Naive execution time: " + to_string(chrono::duration_cast<chrono::microseconds>(t11 - t01).count()) + " us");
    waitEnter();
}

void mainMenu()
{
    while (true)
    {
        screenHeader("Main Menu");
        cout << "  1) Euclidean GCD\n"
             << "  2) Extended Euclidean Algorithm (find x, y)\n"
             << "  3) Modular Inverse\n"
             << "  4) Modular Addition & Multiplication\n"
             << "  5) Modular Exponentiation (naive vs. fast)\n"
             << "  0) Exit\n\n";
        cout << Col::GREEN << "  choose> " << Col::RESET;
        string choice;
        if (!(cin >> choice))
            break;
        if (choice == "0")
            break;
        else if (choice == "1")
            taskGCD();
        else if (choice == "2")
            taskExtendedGCD();
        else if (choice == "3")
            taskModInverse();
        else if (choice == "4")
            taskModAddMul();
        else if (choice == "5")
            taskModExp();
        else
        {
            errLine("Unknown option.");
            waitEnter();
        }
    }
    clearScreen();
    cout << Col::CYAN << "Goodbye!\n"
         << Col::RESET;
}

int main()
{
    mainMenu();
    return 0;
}

"""Test-
    small primes
    larger primes
    composiet numbers
    Carmichael numbers

    Measures
        execution Time
        number of iterations
        false-positive behaviour
"""
import random
from cpython import extended_gcd_naive

def trival_primality_test(p):
    if p <= 1:
        return False 
    if p == 2:
        return True
    if(p % 2 == 0): 
        return True
    for i in range(3, int(p**0.5) +1):
        if(p % i == 0):
            return False
    return True
    

def fermat_primality_test(p):
    random_a = random.randint(2, p)
    gcd = extended_gcd_naive(p,random_a)
    if(gcd != 1):
        return False
    if(pow(random_a, p-1, p) != 1):
        return False
    return True



def trivial_menu():
    print("\n--- Find prime using trival method ---")
    while True:
        try:
            p = int(input("Enter Prime p              : "))
            repetation = int(input("Enter repetation for test  : "))
        except ValueError:
            print("  [!] All inputs must be integers.")
            return
    result = trival_primality_test(p)
    if result:
        print(f"Number {p} is a prime")
    else:
        print(f"Number {p} if not prime")



def fermat_test_menu():
    print("\n--- Find prime using fermat primality test ---")
    while True:
        try:
            p = int(input("Enter Prime p              : "))
        except ValueError:
            print("  [!] All inputs must be integers.")
            return
    result = trival_primality_test(p)
    if result:
        print(f"Number {p} is a prime")
    else:
        print(f"Number {p} if not prime")
    

def Miller_rabin_menu():
    pass
def run_expriment_menu():
    pass

MENU_OPTIONS = {
    "1": ("Trivial Divison", trivial_menu),
    "2": ("Fermat Primality Test",  fermat_test_menu),
    "3": ("Miller-Rabin Primality Test", Miller_rabin_menu),
    "4": ("Miller-Rabin Primality Test", run_expriment_menu),

}

if __init__ == __main__:
    print("=" * 50)
    print("  Primality Test Tool")
    print("=" * 50)

    while True:
        print("\nMenu:")
        for key, (description, _) in MENU_OPTIONS.items():
            print(f"  [{key}] {description}")
        print("  [0] Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in MENU_OPTIONS:
            _, action = MENU_OPTIONS[choice]
            action()
        else:
            print(f"  [!] Invalid choice '{choice}'. Please enter 0–{len(MENU_OPTIONS)}.")
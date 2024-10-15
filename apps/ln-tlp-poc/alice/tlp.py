import gmpy2
import time

class PrimeGenerator:
    def __init__(self, bits):
        self.bits = bits
        gmpy2.get_context().precision = bits
        self.state = gmpy2.random_state(int(time.time()))

    def generate_base(self):        
        return gmpy2.mpz_rrandomb(self.state, self.bits)

    def generate_prime(self):
        prime = gmpy2.mpz_rrandomb(self.state, self.bits)
        prime = gmpy2.next_prime(prime)
        return prime

    def calculate_totient(self, p1, p2):
        p1_minus_1 = p1 - 1
        p2_minus_1 = p2 - 1
        return p1_minus_1 * p2_minus_1

    def calculate_carmichael(self, p1, p2):
        p1_minus_1 = p1 - 1
        p2_minus_1 = p2 - 1
        lcm = gmpy2.lcm(p1_minus_1, p2_minus_1)
        return lcm

    def mod_exp(self, base, exp, mod):
        return gmpy2.powmod(base, exp, mod)

def main():
      # Choose a sample number 't' (large exponent)
    t = gmpy2.mpz(10000000)
    bits_primes = 256  # Number of bits for the prime numbers
    prime_gen = PrimeGenerator(bits_primes)

    prime1 = prime_gen.generate_prime()
    prime2 = prime_gen.generate_prime()

    # Calculate the product of the two primes
    product = prime1 * prime2

    # Calculate the Carmichael function of the product
    carmichael_p = prime_gen.calculate_carmichael(prime1, prime2)

    
    print(f"Prime 1: {prime1}")
    print(f"Prime 2: {prime2}")
    print(f"Product (Prime1 * Prime2): {product}")
    print(f"Carmichael(Product): {carmichael_p}")

  
    # Calculate 2^t mod carmichael_p
    base2 = gmpy2.mpz(2)
    fast_exponent = prime_gen.mod_exp(base2, t, carmichael_p)

    # Output the result
    print(f"2^{t} ≡ {fast_exponent} (mod {carmichael_p})")

    baseg = gmpy2.mpz(12345)
    fast_power = prime_gen.mod_exp(baseg, fast_exponent, product)
    print(f"Fast exponent result: {fast_power}")

    slow_power = baseg
    for i in range(int(t)):
        slow_power = prime_gen.mod_exp(slow_power, gmpy2.mpz(2), product)

    print(f"Base raised to fast exponent = {fast_power}")
    print(f"T-times squared base = {slow_power}")

if __name__ == "__main__":
    main()

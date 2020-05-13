// https://github.com/sosy-lab/sv-benchmarks/blob/master/c/nla-digbench/sqrt1.c
/* Compute the floor of the square root of a natural number */
extern int __VERIFIER_nondet_int(void);

int main() {
    int s, t, i, j;
    // n = __VERIFIER_nondet_int();
    i = __VERIFIER_nondet_int();
    j = __VERIFIER_nondet_int();

    s = 1;
    t = 1;

    while (t*t - 4*s + 2*t + 1 + i >= 0) {
      //__VERIFIER_assert(t == 2*a + 1);
      //__VERIFIER_assert(s == (a + 1) * (a + 1));
      //__VERIFIER_assert(t*t - 4*s + 2*t + 1 == 0);
        // the above 2 should be equiv to 
      //if (!(s <= n))break;
        t = t + 2;
        s = s + t;
        i = i + j;
        j = j + 1;
    }

    /*
    while (i >= 0) {
      i = i + j;
      j = j + 1;
    }
    */

    //__VERIFIER_assert(t == 2 * a + 1);
    //__VERIFIER_assert(s == (a + 1) * (a + 1));
    //__VERIFIER_assert(t*t - 4*s + 2*t + 1 == 0);

    return 0;
}

int core_init(void);
int core_clean(void);
int pc_param_set_any();
void pc_param_print();


unsigned int get_rlc_dig(void);
int get_rlc_ok(void);
const int CONST_RLC_POS;
const int CONST_RLC_NEG;
const int CONST_RLC_LT;
const int CONST_RLC_EQ;
const int CONST_RLC_GT;


typedef uint64_t dig_t;
typedef struct {
	/** The number of digits allocated to this multiple precision integer. */
	int alloc;
	/** The number of digits actually used. */
	int used;
	/** The sign of this multiple precision integer. */
	int sign;
	/** The sequence of contiguous digits that forms this integer. */
	// rlc_align dig_t dp[RLC_BN_SIZE]; HACKITYHACK
    // HACK: had to hardcode the constant, and remove rlc_align
    // ALLOC = AUTO
	dig_t dp[34];
} bn_st;

typedef bn_st bn_t[1];
void g1_get_ord(bn_t order);


void bn_new(bn_t a);
void bn_copy(bn_t c, const bn_t a);

void bn_abs(bn_t c, const bn_t a);
void bn_neg(bn_t c, const bn_t a);
int bn_sign(const bn_t a);
void bn_zero(bn_t a);
int bn_is_zero(const bn_t a);
int bn_is_even(const bn_t a);
int bn_bits(const bn_t a);
int bn_get_bit(const bn_t a, int bit);
void bn_set_bit(bn_t a, int bit, int value);
void bn_get_dig(dig_t *digit, const bn_t a);
void bn_set_2b(bn_t a, int b);
void bn_set_dig(bn_t a, dig_t digit);
void bn_rand(bn_t a, int sign, int bits);
void bn_rand_mod(bn_t a, bn_t b);

void bn_print(const bn_t a);
int bn_size_str(const bn_t a, int radix);
void bn_read_str(bn_t a, const char *str, int len, int radix);
void bn_write_str(char *str, int len, const bn_t a, int radix);
int bn_size_bin(const bn_t a);
void bn_read_bin(bn_t a, const uint8_t *bin, int len);
void bn_write_bin(uint8_t *bin, int len, const bn_t a);

int bn_cmp_abs(const bn_t a, const bn_t b);
int bn_cmp_dig(const bn_t a, dig_t b);
int bn_cmp(const bn_t a, const bn_t b);

void bn_add(bn_t c, const bn_t a, const bn_t b);
void bn_add_dig(bn_t c, const bn_t a, dig_t b);
void bn_sub(bn_t c, const bn_t a, const bn_t b);
void bn_sub_dig(bn_t c, const bn_t a, const dig_t b);

void bn_mul(bn_t c, const bn_t a, const bn_t b);
void bn_mul_dig(bn_t c, const bn_t a, dig_t b);

void bn_sqr(bn_t c, const bn_t a);
void bn_dbl(bn_t c, const bn_t a);
void bn_hlv(bn_t c, const bn_t a);
void bn_lsh(bn_t c, const bn_t a, int bits);
void bn_rsh(bn_t c, const bn_t a, int bits);

void bn_div(bn_t c, const bn_t a, const bn_t b);
void bn_div_rem(bn_t c, bn_t d, const bn_t a, const bn_t b);

void bn_mod_2b(bn_t c, const bn_t a, int b);
void bn_mod(bn_t c, const bn_t a, const bn_t m);

void bn_gcd(bn_t c, const bn_t a, const bn_t b);
void bn_gcd_ext(bn_t c, bn_t d, bn_t e, const bn_t a, const bn_t b);

int bn_is_prime(const bn_t a);
void bn_gen_prime(bn_t a, int bits);
void bn_gen_prime_safep(bn_t a, int bits);
void bn_gen_prime_stron(bn_t a, int bits);


// HACK: rlc_align removed, hardcoded size of array
// ORIG: typedef rlc_align dig_t fp_t[RLC_FP_DIGS + RLC_PAD(RLC_FP_BYTES)/(RLC_DIG / 8)];
// ORIG: typedef rlc_align dig_t fp_st[RLC_FP_DIGS + RLC_PAD(RLC_FP_BYTES)/(RLC_DIG / 8)];
typedef dig_t fp_t[6];
typedef dig_t fp_st[6];

typedef uint8_t appel;

typedef struct {
	/** The first coordinate. */
	fp_st x;
	/** The second coordinate. */
	fp_st y;
	/** The third coordinate (projective representation). */
	fp_st z;
	/** Flag to indicate that this point is normalized. */
	int norm;
} ep_st;

typedef ep_st ep_t[1];

typedef ep_t g1_t;
// typedef ep2_t g2_t;
// typedef fp12_t gt_t;

typedef ep_st g1_st;
// typedef ep2_st g2_st;
// typedef fp12_st gt_st;


/* void g1_null(g1_t p) */
void g1_new(g1_t p);
void g1_rand(g1_t p);
void g1_print(g1_t p);

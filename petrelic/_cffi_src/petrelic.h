int core_init(void);
int core_clean(void);
unsigned int get_rlc_dig(void);
int get_rlc_ok(void);

const int CONST_RLC_POS;
const int CONST_RLC_NEG;
const int CONST_RLC_LT;
const int CONST_RLC_EQ;
const int CONST_RLC_NE;
const int CONST_RLC_GT;
const int CONST_RLC_DIG;
const int CONST_RLC_OK;



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

typedef fp_t fp2_t[2];
typedef fp_st fp2_st[2];

/*
 * ******** Typedefs for G1 ********
 */
typedef struct {
	/** The first coordinate. */
	fp_st x;
	/** The second coordinate. */
	fp_st y;
	/** The third coordinate (projective representation). */
	fp_st z;
	/** Flag to indicate that this point is normalized. */
	int coord;
} ep_st;
typedef ep_st ep_t[1];
typedef ep_st g1_st;
typedef ep_t g1_t;

/*
 * ******** Typedefs for G2 ********
 */
typedef struct {
  /** The first coordinate. */
  fp2_t x;
  /** The second coordinate. */
  fp2_t y;
  /** The third coordinate (projective representation). */
  fp2_t z;
  /** Flag to indicate that this point is normalized. */
  int coord;
} ep2_st;
typedef ep2_st ep2_t[1];
typedef ep2_st g2_st;
typedef ep2_t g2_t;

/*
 * ******** Typedefs for GT ********
 */
typedef fp2_t fp6_t[3];
typedef fp6_t fp12_t[2];
typedef fp12_t gt_t;

/*
 * ******** Operations for G1 ********
 */
void g1_null(g1_t p);
void g1_new(g1_t p);
void g1_get_gen(g1_t p);
void g1_get_ord(bn_t order);
int g1_is_infty(g1_t p);
void g1_set_infty(g1_t p);
void g1_copy(g1_t r, g1_t p);
int g1_cmp(g1_t p, g1_t q);
void g1_rand(g1_t p);
void g1_print(g1_t p);

int g1_size_bin(g1_t p, int pack);
void g1_read_bin(g1_t p, const uint8_t *bin, int len);
void g1_write_bin(uint8_t *bin, int len, g1_t p, int pack);

void g1_neg(g1_t r, g1_t p);
void g1_add(g1_t r, g1_t p, g1_t q);
void g1_sub(g1_t r, g1_t p, g1_t q);
void g1_dbl(g1_t r, g1_t p);
void g1_norm(g1_t r, g1_t p);
void g1_mul(g1_t r, g1_t p, bn_t k);
void g1_mul_key(g1_t r, g1_t p, bn_t k);
void g1_mul_dig(g1_t r, g1_t p, dig_t k);
void g1_mul_gen(g1_t r, bn_t k);
int g1_is_valid(g1_t p);

void g1_mul_sim(g1_t r, const g1_t p, const bn_t k, const g1_t q, const bn_t m);
void g1_map(g1_t p, const uint8_t *bin, int len);

/*
// Skipping precomputation table for now
void g1_mul_pre(g1_t *t, const g1_t p);
void g1_mul_fix(g1_t r, const g1_t *t, const bn_t k);


*/



/*
 * ******** Operations for G2 ********
 */
void g2_null(g2_t p);
void g2_new(g2_t p);
void g2_get_gen(g2_t p);
void g2_get_ord(bn_t order);
int g2_is_infty(g2_t p);
void g2_set_infty(g2_t p);
void g2_copy(g2_t r, g2_t p);
int g2_cmp(g2_t p, g2_t q);
void g2_rand(g2_t p);
void g2_print(g2_t p);

int g2_size_bin(g2_t p, int pack);
void g2_read_bin(g2_t p, const uint8_t *bin, int len);
void g2_write_bin(uint8_t *bin, int len, g2_t p, int pack);

void g2_neg(g2_t r, g2_t p);
void g2_add(g2_t r, g2_t p, g2_t q);
void g2_sub(g2_t r, g2_t p, g2_t q);
void g2_dbl(g2_t r, g2_t p);
void g2_norm(g2_t r, g2_t p);
void g2_mul(g2_t r, g2_t p, bn_t k);
void g2_mul_dig(g2_t r, g2_t p, dig_t k);
void g2_mul_gen(g2_t r, bn_t k);
int g2_is_valid(g2_t p);

void g2_mul_sim(g2_t r, g2_t p, bn_t k, g2_t q, bn_t m);
void g2_map(g2_t p, const uint8_t *bin, int len);


/*
 * ******** Operations for GT ********
 */
void gt_null(gt_t p);
void gt_new(gt_t p);
void gt_get_gen(gt_t p);
void gt_get_ord(bn_t order);
int gt_is_unity(gt_t p); //
void gt_set_unity(gt_t p); //
void gt_copy(gt_t r, gt_t p);
int gt_cmp(gt_t p, gt_t q);
void gt_rand(gt_t p);
void gt_print(gt_t p);

int gt_size_bin(gt_t p, int pack);
void gt_read_bin(gt_t p, const uint8_t *bin, int len);
void gt_write_bin(uint8_t *bin, int len, gt_t p, int pack);

void gt_inv(gt_t r, gt_t p); //
void gt_mul(gt_t r, gt_t p, gt_t q);
// void gt_div(gt_t r, gt_t p, gt_t q);
void gt_sqr(gt_t r, gt_t p);
void gt_exp(gt_t r, gt_t p, bn_t k);
void gt_exp_dig(gt_t r, gt_t p, dig_t k);
int gt_is_valid(gt_t p);



/*
 * ******** Pairing Operations ********
 */
void pc_map(gt_t p, g1_t p, g2_t q);

int pc_param_set_any();
void pc_param_print();


void fp_prime_back(bn_t c, const fp_t a);


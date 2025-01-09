cprog = r'''#include <string.h>
#include <stdlib.h>  // Include the standard library for atol()
#include "flint/flint.h"
#include "flint/arb.h"
#include "flint/acb.h"
#include "flint/acb_calc.h"
#include <math.h>

typedef struct Integral {
    acb_t var;              
    char var_name[10];
    acb_t mu;
    acb_t factor;
    int upper_has_infinity;
    int lower_has_infinity;
    struct Integral* inner[100];
    int inner_size;
    int random_lower[100];
    int random_lower_size;
    int numeric_lower_size;
    float numeric_lower[100];
    int numeric_upper_size;
    float numeric_upper[100];
    int index;
    int holomorphic;
} Integral;

typedef struct Parameters {
    acb_t k;
    acb_t eps;
    struct Integral* root;
    acb_t vars[100];
} Parameters;


void assign_array_int(int *dest, int *src, size_t size) {
    for (size_t i = 0; i < size; i++) {
        *(dest + i) = *(src + i);
    }
}

void assign_array_float(float *dest, float *src, size_t size) {
    for (size_t i = 0; i < size; i++) {
        *(dest + i) = *(src + i);
    }
}


int find_max(Parameters param) {
    // Initialize variables
    arb_t max_abs, temp_abs;
    arb_init(max_abs);
    arb_init(temp_abs);
    int result_index = param.root->random_lower[0];
    acb_get_real(max_abs, param.vars[result_index]); // Start with the first element as max


    for (int i = 1; i < param.root->random_lower_size; i++) {
        // Compute the absolute value of arr[i]
        int index = param.root->random_lower[i];

        acb_get_real(temp_abs, param.vars[index]);

        // Compare and update max if necessary
        if (arb_gt(temp_abs, max_abs)) {
            arb_set(max_abs, temp_abs); // Update max magnitude
            result_index = index;
        }
    }

    // Cleanup
    arb_clear(max_abs);
    arb_clear(temp_abs);

    return result_index;
}

double calculate_error_bound(float k) {
    return exp(- (pow(k, 2)) / 2);
}

int** generate_combinations(int size) {
    int total_combinations = pow(2, size); 
    int** combinations = (int**)malloc(total_combinations * sizeof(int*));
    for (int i = 0; i < total_combinations; i++) {
        combinations[i] = (int*)malloc(size * sizeof(int));
        for (int j = size - 1; j >= 0; j--) {
            combinations[i][size - 1 - j] = (i >> j) & 1;
        }
    }
    return combinations;
}


float float_max(float nums[], int size) {
    float max_val = nums[0];
    for (int i = 1; i < size; i++) {
        if (nums[i] > max_val) {
            max_val = nums[i];
        }
    }

    return max_val;
}

void compute_lower_limit(acb_t limit, Parameters param, slong prec) {
    if (param.root->lower_has_infinity == 1) {
        acb_t prd;
        acb_init(prd);
        acb_div(prd, param.root->factor, param.eps, prec);
        acb_mul(prd, param.k, prd, prec);
        acb_sub(limit, param.root->mu, prd, prec);
    } else {
        if (param.root->random_lower_size == 1 && param.root->numeric_lower_size == 0) {
            acb_set(limit, param.vars[param.root->random_lower[0]]);
        } else if (param.root->random_lower_size == 0 && param.root->numeric_lower_size > 0) {
            acb_set_d(limit, float_max(param.root->numeric_lower, param.root->numeric_lower_size));
        } else {
            acb_t numeric_max;
            acb_init(numeric_max);
            acb_set_d(numeric_max, (double) float_max(param.root->numeric_lower, param.root->numeric_lower_size));
            acb_real_max(limit, param.vars[find_max(param)], numeric_max, 1, prec);
        }
    }
}

float float_min(float nums[], int size) {
    float min_val = nums[0];
    for (int i = 1; i < size; i++) {
        if (nums[i] < min_val) {
            min_val = nums[i];
        }
    }

    return min_val;
}

void compute_upper_limit(acb_t limit, Parameters param, slong prec) {
    if (param.root->upper_has_infinity == 1) {
        acb_t prd;
        acb_init(prd);
        acb_div(prd, param.root->factor, param.eps, prec);
        acb_mul(prd, param.k, prd, prec);
        acb_add(limit, param.root->mu, prd, prec);
    } else {
        acb_set_d(limit, (double) float_min(param.root->numeric_upper, param.root->numeric_upper_size));
    }
}
// Gaussian function for integration
int gaussian_function(acb_ptr result, const acb_t x, void *my_param, slong order, slong prec) {
    acb_t norm_factor, exponent, diff, sigma, sigma_sq, const_factor, two, pi;
    Parameters param = *(Parameters *) my_param;
    Integral integral = *(param.root);
    
    if (order > 1)
		flint_abort();
    
    acb_init(param.vars[integral.index]);
    acb_set(param.vars[integral.index], x);

    acb_init(sigma);
    acb_div(sigma, integral.factor, param.eps, prec);

    //printf("order %ld\n", order);
    acb_init(norm_factor);
    acb_init(exponent);
    acb_init(diff);
    acb_init(sigma_sq);
    acb_init(const_factor);
    acb_init(two);
    acb_init(pi);

    // Initialize constants
    acb_set_si(two, 2);                // 2
    acb_const_pi(pi, prec);            // pi

    // Calculate the normalization factor 1 / (sigma * sqrt(2 * pi))
    acb_mul(const_factor, two, pi, prec);   // 2 * pi
    acb_sqrt(const_factor, const_factor, prec);  // sqrt(2 * pi)
    acb_mul(norm_factor, sigma, const_factor, prec);  // sigma * sqrt(2 * pi)
    acb_inv(norm_factor, norm_factor, prec);    // 1 / (sigma * sqrt(2 * pi))

    // Calculate the exponent part: -(x - mu)^2 / (2 * sigma^2)
    acb_mul(sigma_sq, sigma, sigma, prec);  // sigma^2
    acb_mul(sigma_sq, sigma_sq, two, prec); // 2 * sigma^2
    acb_sub(diff, x, integral.mu, prec);             // x - mu
    acb_mul(diff, diff, diff, prec);        // (x - mu)^2
    acb_div(exponent, diff, sigma_sq, prec);    // (x - mu)^2 / 2 * sigma^2
    acb_neg(exponent, exponent);            // -(x - mu)^2 / (2 * sigma^2)

    // Calculate the exponential part: exp(-(x - mu)^2 / (2 * sigma^2))
    acb_exp(exponent, exponent, prec);

    acb_mul(result, norm_factor, exponent, prec);
    if (integral.inner_size) {
        for (int i = 0; i < integral.inner_size; i++) {
            acb_t inner_res;
            acb_init(inner_res);
            Integral inner = *(integral.inner[i]);
            param.root = &inner;
            slong goal = prec;
    
            mag_t tol;
            mag_init(tol);
            mag_set_ui_2exp_si(tol, 1, -goal);
    
            acb_calc_integrate_opt_t options;
            acb_calc_integrate_opt_init(options);
    
            acb_t lower_limit;
            acb_init(lower_limit);
            compute_lower_limit(lower_limit, param, prec);
            acb_t upper_limit;
            acb_init(upper_limit);
            compute_upper_limit(upper_limit, param, prec);
            acb_calc_integrate(inner_res, gaussian_function, &(param), lower_limit, upper_limit, goal, tol, options, prec);
            acb_mul(result, result, inner_res, prec);
        }
    }
    /*
     if (integral.holomorphic == 0 && order == 1) {
        acb_indeterminate(result);
     } */
    
    acb_clear(norm_factor);
    acb_clear(exponent);
    acb_clear(diff);
    acb_clear(sigma_sq);
    acb_clear(const_factor);
    acb_clear(two);
    acb_clear(pi);
    return 0;
}



void set_integral(Integral *integral, int index, double mu, double factor,
        int upper_has_infinity, int lower_has_infinity, int random_lower[], int random_lower_size, float numeric_lower[], int numeric_lower_size,
        float numeric_upper[], int numeric_upper_size, int inner_size
    ) {
    acb_init(integral->mu);
    acb_set_d(integral->mu, mu);
    acb_init(integral->factor);
    acb_set_d(integral->factor, factor);
    integral->random_lower_size = random_lower_size;
    integral->numeric_lower_size = numeric_lower_size;
    integral->numeric_upper_size = numeric_upper_size;
    integral->inner_size = inner_size;
    
    if (random_lower_size) {
        assign_array_int(integral->random_lower, random_lower, random_lower_size);
    }

    if (numeric_lower_size) {
        assign_array_float(integral->numeric_lower, numeric_lower, numeric_lower_size);
    }

    if (numeric_upper_size) {
        assign_array_float(integral->numeric_upper, numeric_upper, numeric_upper_size);
    }

    integral->upper_has_infinity = upper_has_infinity;
    integral->lower_has_infinity = lower_has_infinity;
    integral->index = index;
    integral->holomorphic = 1;
}

{{WHOLE_BLOCK}}

int check_for_an_pair(arb_t* probs, arb_t* probs_adj, int probs_size, arb_ptr arb_eps, double delta, int k, slong prec, int debug) {
    char paths_output[][100] = { {{PATHS_OUTPUT}} }; 
    int eb[] = { {{EB}} };
    
    arf_t sum_delta;
    arf_init(sum_delta);
    arf_zero(sum_delta);
    
    for (int i = 0; i < probs_size; i++) {
        arb_t arb_prob_eb, product_eps_prob_adj;
        arb_init(arb_prob_eb);
        arb_init(product_eps_prob_adj);
        
        arf_t l, u, diff;
        arf_init(l);
        arf_init(u);
        arf_init(diff);
        
        arb_set_d(arb_prob_eb, eb[i] * calculate_error_bound(k));
        arb_add(arb_prob_eb, probs[i], arb_prob_eb, prec);

        arb_exp(product_eps_prob_adj, arb_eps, prec);
        arb_mul(product_eps_prob_adj, product_eps_prob_adj, probs_adj[i], prec);
        
        
        if (debug) {
            printf("------Info for path %s, k = %d, prec = %ld------", paths_output[i], k, prec);
            printf("\nProb: ");
            arb_printd(probs[i], 3);
            printf(" , Prob': ");
            arb_printd(probs_adj[i], 3);
            printf("\nProb + eb: ");
            arb_printd(arb_prob_eb, 3);
            printf("\nexp(ε) * Prob': ");
            arb_printd(product_eps_prob_adj, 3);
            printf("\n");
        }
        

        if (!arb_le(arb_prob_eb, product_eps_prob_adj)) {
            arb_get_ubound_arf(u, arb_prob_eb, prec);
            arb_get_lbound_arf(l, product_eps_prob_adj, prec);
            arf_sub(diff, u, l, prec, ARF_RND_NEAR);
            arf_add(sum_delta, sum_delta, diff, prec, ARF_RND_NEAR);
            
            if (debug) {
                printf("\ndiff:");
                arf_printd(diff, prec);
                printf("\n");
            }
        }
        
        arb_clear(arb_prob_eb);
        arb_clear(product_eps_prob_adj);
        arf_clear(l);
        arf_clear(u);
        arf_clear(diff);
    }


    if (arf_cmp_d(sum_delta, delta) <= 0) {
        if (debug) {
            printf("\nPassed!\n");
        }
        return 1;
    }
    
    if (debug) {
        printf("\nFailed to prove!\n");
    }
  
    return 0;
}


int check_not_dp_for_an_pair(arb_t* probs, arb_t* probs_adj, int probs_size, arb_ptr arb_eps, double delta, int k, slong prec, int debug) {
    char paths_output[][100] = { {{PATHS_OUTPUT}} }; 
    int eb[] = { {{EB}} };
    
    arf_t sum_delta;
    arf_init(sum_delta);
    arf_zero(sum_delta);
    
    for (int i = 0; i < probs_size; i++) {
        arb_t arb_prob_eb, product_eps_prob_adj;
        arb_init(arb_prob_eb);
        arb_init(product_eps_prob_adj);
        
        arf_t l, u, diff;
        arf_init(l);
        arf_init(u);
        arf_init(diff);
        
        arb_set_d(arb_prob_eb, eb[i] * calculate_error_bound(k));
        arb_add(arb_prob_eb, probs_adj[i], arb_prob_eb, prec);

        arb_exp(product_eps_prob_adj, arb_eps, prec);
        arb_mul(product_eps_prob_adj, product_eps_prob_adj, arb_prob_eb, prec);
        
        
        if (debug) {
            printf("------Info for path %s, k = %d, prec = %ld------", paths_output[i], k, prec);
            printf("\nProb: ");
            arb_printd(probs[i], 3);
            printf(" , Prob': ");
            arb_printd(probs_adj[i], prec);
            printf("\nexp(ε) * (Prob' + eb): ");
            arb_printd(product_eps_prob_adj, 3);
            printf("\n");
        }
        
        if (arb_ge(probs[i], product_eps_prob_adj) && !arb_overlaps(probs[i], product_eps_prob_adj)) {
            arb_get_lbound_arf(l, probs[i], prec);
            arb_get_ubound_arf(u, product_eps_prob_adj, prec);
            arf_sub(diff, l, u, prec, ARF_RND_NEAR);
            arf_add(sum_delta, sum_delta, diff, prec, ARF_RND_NEAR);
            
            if (debug) {
                printf("diff: ");
                arf_printd(diff, prec);
                printf("\n");
            }
        }
        
        
        

        arb_clear(arb_prob_eb);
        arb_clear(product_eps_prob_adj);
        arf_clear(l);
        arf_clear(u);
        arf_clear(diff);
    }


    if (arf_cmp_d(sum_delta, delta) > 0) {
        printf("\n\nsum diff: ");
        arf_printd(sum_delta, prec);
        if (debug) {
            printf("\nPassed!\n");
        }
        return 1;
    }
    
    if (debug) {
        printf("\nFailed to prove!\n");
    }
  
    return 0;
}


char* input_to_string(int input[], int input_length) {
    char* str_input = (char*)malloc((input_length + 1) * sizeof(char));
   
    for (int i = 0; i < input_length; i++) {
        str_input[i] = input[i] ? '1' : '0';
    }

    str_input[input_length] = '\0'; 
    return str_input;
}

void print_input(int input[], int input_adj[], int input_length) {
    printf("\n-----------------------------------\nin = %s in' = %s\n", input_to_string(input, input_length), input_to_string(input_adj, input_length));
}

int main(int argc, char *argv[]) {
    double eps, delta;
    int input_length = {{INPUT_SIZE}};
    int debug = 0;
    int k;

    for (int i = 1; i < argc; i++)
    {
        if (!strcmp(argv[i], "-delta"))
            delta = atof(argv[i + 1]);
        if (!strcmp(argv[i], "-eps")) 
            eps = atof(argv[i+1]);
        if (!strcmp(argv[i], "-k"))
            k = atoi(argv[i + 1]);
        if (!strcmp(argv[i], "-debug"))
            debug = 1;
    }
    
    if (debug) {
        printf("k=%d, eps=%f, delta=%f, input_length=%d\n\n", k, eps, delta, input_length);
    }
    
    int total_inputs = (int) pow(2, input_length);
    int** inputs = generate_combinations(input_length);
    
    slong prec[] = { 8, 16, 32 };
    int prec_size = sizeof(prec) / sizeof(prec[0]);

    int (*compute_probability[])(arb_ptr, double, slong, double, int[]) = { {{ARRAY}} };
    int compute_probability_size = sizeof(compute_probability) / sizeof(compute_probability[0]);
        
    arb_t arb_eps;
    arb_init(arb_eps);
    arb_set_d(arb_eps, eps);
    
    char paths_output[][100] = { {{PATHS_OUTPUT}} }; 
    int is_dp = 1;
    int is_not_dp = 0;
    for (int prec_index = 0; prec_index < prec_size; prec_index++) {
        arb_t probs[total_inputs][compute_probability_size];
        if (debug) {
            printf("----------------------Precision: %ld----------------------\n", prec[prec_index]);
        }
        for (int input_index = 0; input_index < total_inputs; input_index++) {
            for (int path_index = 0; path_index < compute_probability_size; path_index++) {
                arb_init(probs[input_index][path_index]);
                compute_probability[path_index](probs[input_index][path_index], eps, prec[prec_index], k, inputs[input_index]);
                
                if (debug) {
                    printf("\nProb path=%s, input=%s: ", paths_output[path_index], input_to_string(inputs[input_index], input_length));
                    arb_printd(probs[input_index][path_index], 3);
                }   
            }
        }
        
        if (debug) {
            printf("\n\n------------------Checking DP------------------------\n");
        }
        
        is_dp = 1;
        for (int i = 0; i < total_inputs; i++) {
            for (int j = 0; j < total_inputs; j++) {
                if (i != j) {
                    if (debug && is_dp) {
                        print_input(inputs[i], inputs[j], input_length);
                    }
                    is_dp = is_dp && check_for_an_pair(probs[i], probs[j], compute_probability_size, arb_eps, delta, k, prec[prec_index], debug);
                }
            }
        }
        
        if (is_dp) {
            if (debug) {
                printf("-----------------------------------------------------------------------------------\n");
                printf("Differential Private? Yes");
            } else {
                printf("{ \"DP\": 1}");
            }
            
            break;
        }
        
        if (debug) {
            printf("\n\n------------------Checking Not DP------------------------\n");
        }
        
        is_not_dp = 0;
        for (int i = 0; i < total_inputs; i++) {
            for (int j = 0; j < total_inputs; j++) {
                if (i != j) {
                    if (debug && is_dp) {
                        print_input(inputs[i], inputs[j], input_length);
                    }
                    is_not_dp = is_not_dp || check_not_dp_for_an_pair(probs[i], probs[j], compute_probability_size, arb_eps, delta, k, prec[prec_index], debug);
                }
            }
        }
        
        
        if (is_not_dp) {
            if (debug) {
                printf("-----------------------------------------------------------------------------------\n");
                printf("Differential Private? No");
            } else {
                printf("{ \"DP\": -1}");
            }
            break;
        }
    }
    
    
    
    if (!is_not_dp && !is_dp) {
        if (debug) {
             printf("-----------------------------------------------------------------------------------\n");
             printf("Differential Private? Unable to resolve");
        } else {
            printf("{ \"DP\": 0}");
        }
       
    }
    
    return 0;
}
'''


def function_product_block_template():
    return r'''
int product_integrals_{{INDEX}}(acb_ptr result, double eps, slong prec, double k, int input[]) {
    int (*compute_probability[])(acb_ptr, double, slong, double, int[]) = { {{ARRAY}} };

    int compute_probability_size = sizeof(compute_probability) / sizeof(compute_probability[0]);

    acb_one(result);

    for (int i = 0; i < compute_probability_size; i++) {
        acb_t inner;
        acb_init(inner);
        compute_probability[i](inner, eps, prec, k, input);
        acb_mul(result, result, inner, prec);
    }
    
    return 0;
}
    '''


def function_block_template():
    return '''
int compute_probability_for_output_{{INDEX}}(arb_ptr arb_result, double eps, slong prec, double k, int input[])
{
    acb_t result;
    acb_init(result);
    acb_zero(result);
    
    int (*compute_probability[])(acb_ptr, double, slong, double, int[]) = { {{ARRAY}} };
    int compute_probability_size = sizeof(compute_probability) / sizeof(compute_probability[0]);

    for (int i = 0; i < compute_probability_size; i++) {
        acb_t inner;
        acb_init(inner);
        compute_probability[i](inner, eps, prec, k, input);
        acb_add(result, result, inner, prec);
    }
    
    acb_get_real(arb_result, result);
    return 0;
}
    '''


def function_integrals_template():
    return r'''
int integrals_{{INDEX}}(acb_ptr result, double eps, slong prec, double d_k, int input[])
{
    slong goal = prec;

    mag_t tol;
    mag_init(tol);
    mag_set_ui_2exp_si(tol, 1, -goal);

    acb_calc_integrate_opt_t options;
    acb_calc_integrate_opt_init(options);

    acb_t k;
    acb_init(k);
    acb_set_d(k, d_k);
    
    Parameters parameters;
    acb_init(parameters.k);
    acb_set_d(parameters.k, d_k);
    
    
    acb_init(parameters.eps);
    acb_set_d(parameters.eps, eps);

    {{BLOCK}}
    
    parameters.root = &integral0;
    acb_t lower_limit;
    acb_init(lower_limit);
    compute_lower_limit(lower_limit, parameters, prec);

    acb_t upper_limit;
    acb_init(upper_limit);
    compute_upper_limit(upper_limit, parameters, prec);
    acb_calc_integrate(result, gaussian_function, &parameters, lower_limit, upper_limit , goal, tol, options, prec);

    return 0;
}

'''


def get_mean_value(integral):
    if integral['var']['mean']['type'] == 'INPUT':
        return 'input[' + str(integral['var']['mean']['index']) + ']'

    if integral['var']['mean']['type'] == 'NUMERIC':
        return integral['var']['mean']['value']

    raise Exception('Unsupported mean value')


def get_factor_value(integral):
    return integral['var']['factor']


def has_infinity(limit):
    return 1 if limit['type'] == 'infinity' else 0


def get_limits(vars, variable_map):
    indices_random_vars = []
    input_vars = []
    numeric_vars = []

    for var in vars:
        if var['type'] == 'RANDOM':
            indices_random_vars.append(str(variable_map[var['name']]))

        if var['type'] == 'NUMERIC':
            if type(var['value']) is tuple:
                input_vars.append(var['value'][1])
            else:
                numeric_vars.append(var['value'])

    return indices_random_vars, numeric_vars, input_vars


def get_integral(integral, current_index, variable_map):
    indices_random_vars, numeric_vars, input_vars = get_limits(integral['lower_limit']['vars'], variable_map)
    random_lower_size = len(indices_random_vars)
    random_lower = '{' + ','.join(indices_random_vars) + '}'
    numeric_lower_size = len(numeric_vars) + len(input_vars)
    numeric_lower = '{' + ','.join(map(str, numeric_vars)) + ','.join(map(lambda x: f'input[{x}]', input_vars)) + '}'

    indices_random_vars, numeric_vars, input_vars = get_limits(integral['upper_limit']['vars'], variable_map)
    numeric_upper = '{' + ','.join(map(str, numeric_vars)) + ','.join(map(lambda x: f'input[{x}]', input_vars)) + '}'
    numeric_upper_size = len(numeric_vars) + len(input_vars)

    inner_size = 0
    if 'integrals' in integral['inner']:
        inner_size = len(integral['inner']['integrals'])

    template = f'''
    Integral integral{current_index};
    int random_lower{current_index}[] = {random_lower};
    float numeric_lower{current_index}[] = {numeric_lower};
    float numeric_upper{current_index}[] = {numeric_upper};
    set_integral(&integral{current_index}, {variable_map[integral["var_name"]]}, {get_mean_value(integral)}, 
        {get_factor_value(integral)}, {has_infinity(integral['upper_limit'])}, {has_infinity(integral['lower_limit'])}, random_lower{current_index}, {random_lower_size},
        numeric_lower{current_index}, {numeric_lower_size}, 
        numeric_upper{current_index}, {numeric_upper_size}, {inner_size}
    );
    '''
    # if past_index:
    #     template += f'''
    # integral{past_index}.inner = &integral{current_index};
    #     '''

    return template


def set_integrals_inner(index, i, inner_index):
    template = f'''
    integral{index}.inner[{i}] = &integral{inner_index};
    '''

    return template


def write_to_file(file_name, program):
    with open(file_name, 'w+') as f:
        f.write(program)


def traverse_integrals(variable_map, integral, index):
    index = index + 1
    current_index = index
    variable_map[integral['var_name']] = index
    integral_str = get_integral(integral, index, variable_map)
    if integral['inner']:
        for i, inner_integral in enumerate(integral['inner']['integrals']):
            _integral_str, index = traverse_integrals(variable_map, inner_integral, index)
            integral_str += _integral_str

            integral_str += set_integrals_inner(
                current_index,
                i,
                variable_map[inner_integral['var_name']]
            )

    return integral_str, index


def get_block_for_integrals(index, integral):
    variable_map = dict()
    integral_str, _ = traverse_integrals(variable_map, integral, -1)
    integrals_template = function_integrals_template()
    integrals_template = integrals_template.replace('{{INDEX}}', index)
    integrals_template = integrals_template.replace('{{BLOCK}}', integral_str)

    return integrals_template


def get_block_for_path(path, path_prefix):
    eb = path['eb']
    products = []
    block = ''
    for index, integral in enumerate(path['integrals']):
        integral_index = path_prefix + '_' + str(index)
        block_integral = get_block_for_integrals(integral_index, integral)

        block += block_integral
        products.append('integrals_' + str(integral_index))

    product_block = function_product_block_template()
    product_block = product_block.replace('{{ARRAY}}', ', '.join(products))
    product_block = product_block.replace('{{INDEX}}', path_prefix)

    return block + product_block, eb


def get_block_for_output(index, possible_paths, output_str):
    func_block = function_block_template()

    block = ''

    eb = 0

    sum_integrals = []
    for i, path in enumerate(possible_paths):
        index_prefix = str(index) + '_' + str(i)
        product_block, eb = get_block_for_path(path, index_prefix)
        block += product_block
        sum_integrals.append('product_integrals_' + index_prefix)

    func_block = func_block.replace('{{ARRAY}}', ', '.join(sum_integrals))

    func_block = func_block.replace('{{INDEX}}', str(index))

    block += func_block
    return block, eb


def process(outputs, paths_output, args):
    whole_block = ''
    probability_array = []
    eb_array = []
    for index, possible_paths in enumerate(outputs):
        block, eb = get_block_for_output(index, possible_paths, paths_output[index])
        whole_block += block
        probability_array.append(f'compute_probability_for_output_{index}')
        eb_array.append(str(eb))

    out = cprog.replace('{{WHOLE_BLOCK}}', whole_block)
    out = out.replace('{{ARRAY}}', ', '.join(probability_array))
    out = out.replace('{{PATHS_OUTPUT}}', ','.join(list(map(lambda x: '"' + x + '"', paths_output))))
    out = out.replace('{{EB}}', ', '.join(eb_array))
    out = out.replace('{{INPUT_SIZE}}', str(args.input_size))

    write_to_file('temp_program.c', out)

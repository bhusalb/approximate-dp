cprog = r'''

#include <string.h>
#include <stdlib.h>  // Include the standard library for atol()
#include "flint/flint.h"
#include "flint/arb.h"
#include "flint/acb.h"
#include "flint/acb_calc.h"
#include <math.h>

typedef struct Integral {
    acb_t var;               // Variable of integration
    char var_name[10];          // Variable name (e.g., "X", "Y")
    acb_t mu;
    acb_t factor;
    int has_infinity;
    struct Integral* inner;
    int lower_limit_indices[100];
    int lower_limit_size;
    int index;
    int holomorphic;
} Integral;


typedef struct Parameters {
    acb_t k;
    acb_t eps;
    struct Integral* root;
    acb_t vars[100];
} Parameters;


void assign_array(int *dest, int *src, size_t size) {
    for (size_t i = 0; i < size; i++) {
        *(dest + i) = *(src + i);
    }
}

int find_max(Parameters param) {
    // Initialize variables
    arb_t max_abs, temp_abs;
    arb_init(max_abs);
    arb_init(temp_abs);
    int result_index = param.root->lower_limit_indices[0];
    acb_get_real(max_abs, param.vars[result_index]); // Start with the first element as max


    for (int i = 1; i < param.root->lower_limit_size; i++) {
        // Compute the absolute value of arr[i]
        int index = param.root->lower_limit_indices[i];

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

void compute_lower_limit(acb_t limit, Parameters param, slong prec) {
    if (param.root->has_infinity == 1) {
        acb_t prd;
        acb_init(prd);
        acb_div(prd, param.root->factor, param.eps, prec);
        acb_mul(prd, param.k, prd, prec);
        acb_sub(limit, param.root->mu, prd, prec);
    } else {
        if (param.root->lower_limit_size == 1) {
            acb_set(limit, param.vars[param.root->lower_limit_indices[0]]);
        } else {
            acb_set(limit, param.vars[find_max(param)]);
        }
    }
}

void compute_upper_limit(acb_t limit, Parameters param, slong prec) {
    acb_t prd;
    acb_init(prd);
    acb_div(prd, param.root->factor, param.eps, prec);
    acb_mul(prd, param.k, prd, prec);
    acb_add(limit, param.root->mu, prd, prec);
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
    if (integral.inner != NULL) {
        acb_t inner_res;
        acb_init(inner_res);
        Integral inner = *(integral.inner);
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
    
     if (integral.holomorphic == 0 && order == 1) {
        acb_indeterminate(result);
     }

    // Clear memory
    acb_clear(norm_factor);
    acb_clear(exponent);
    acb_clear(diff);
    acb_clear(sigma_sq);
    acb_clear(const_factor);
    acb_clear(two);
    acb_clear(pi);

    return 0;
}



void set_integral(Integral *integral, int index, double mu, double factor, int has_infinity, int lower_indices[], int lower_indices_size) {
    acb_init(integral->mu);
    acb_set_d(integral->mu, mu);
    acb_init(integral->factor);
    acb_set_d(integral->factor, factor);
    integral->lower_limit_size = lower_indices_size;
    if (lower_indices_size) { 
        assign_array(integral->lower_limit_indices, lower_indices, lower_indices_size);
    }
    integral->has_infinity = has_infinity;
    integral->index = index;
    integral->holomorphic = 1;
    
    if (!has_infinity && lower_indices_size > 1) {
        integral->holomorphic = 0;
    }
    
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

        if (!arb_le(arb_prob_eb, product_eps_prob_adj)) {
            arb_get_ubound_arf(u, arb_prob_eb, prec);
            arb_get_lbound_arf(l, product_eps_prob_adj, prec);
            arf_sub(diff, u, l, prec, ARF_RND_NEAR);
            arf_add(sum_delta, sum_delta, diff, prec, ARF_RND_NEAR);
        }
        
        
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
        printf("\nFailed!\n");
    }
  
    return 0;
}

void print_input(int input[], int input_adj[], int input_length) {
    printf("in = ");
    for (int i = 0; i < input_length; i++) {
        printf("%d ", input[i]);
    }

    printf("\tin' = ");
    for (int i = 0; i < input_length; i++) {
        printf("%d ", input_adj[i]);
    }
        
    printf("\n");
}



int main(int argc, char *argv[]) {
    double eps, delta;
    int input_length = {{INPUT_SIZE}};
    int debug = 0;

    for (int i = 1; i < argc; i++)
    {
        if (!strcmp(argv[i], "-delta"))
            delta = atof(argv[i + 1]);
        
        if (!strcmp(argv[i], "-eps")) 
            eps = atof(argv[i+1]);
            
        if (!strcmp(argv[i], "-debug"))
            debug = 1;
    }
    
    int total_inputs = (int) pow(2, input_length);
    int** inputs = generate_combinations(input_length);
    
    slong prec[] = { 8, 16, 32 };
    int prec_size = sizeof(prec) / sizeof(prec[0]);

    int (*compute_probability[])(arb_ptr, double, slong, double, int[]) = { {{ARRAY}} };
    int compute_probability_size = sizeof(compute_probability) / sizeof(compute_probability[0]);
        
    int k = 4;
    arb_t arb_eps;
    arb_init(arb_eps);
    arb_set_d(arb_eps, eps);
    
    for (int prec_index = 0; prec_index < prec_size; prec_index++) {
        arb_t probs[total_inputs][compute_probability_size];
        if (debug) {
            printf("----------------------Precision: %ld----------------------\n", prec[prec_index]);
        }
        for (int input_index = 0; input_index < total_inputs; input_index++) {
            for (int path_index = 0; path_index < compute_probability_size; path_index++) {
                arb_init(probs[input_index][path_index]);
                compute_probability[path_index](probs[input_index][path_index], eps, prec[prec_index], k, inputs[input_index]);
            }
        }
        
        int is_dp = 1;
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
                printf("{ \"is_dp\":, %d }", is_dp);
            }
            
            return 0;
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
int compute_probability_path_{{INDEX}}(arb_ptr arb_result, double eps, slong prec, double k, int input[])
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
    
    parameters.root = &integral{{ROOT}};
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


def has_infinity(integral):
    return 1 if integral['lower_limit'][1] == 'mean' else 0


def get_lower_limit_incides(integral, variable_map):
    if has_infinity(integral) == 0:
        vars = integral['lower_limit'][1]
        indices = []
        for var in vars:
            indices.append(str(variable_map[var]))

        return '{' + ','.join(indices) + '}', len(integral['lower_limit'][1])
    else:
        return '{}', 0


def get_integral(integral, current_index, past_index, variable_map):

    lower_limit_indices, lower_limit_size = get_lower_limit_incides(integral, variable_map)

    template = f'''     
    Integral integral{current_index};
    int lower_limit_indices{current_index}[] = {get_lower_limit_incides(integral, variable_map)[0]};
    set_integral(&integral{current_index}, {variable_map[integral["var_name"]]}, {get_mean_value(integral)}, {get_factor_value(integral)}, {has_infinity(integral)}, lower_limit_indices{current_index}, {lower_limit_size});
    '''
    if past_index:
        template += f'''
    integral{past_index}.inner = &integral{current_index};
        '''

    return template


def set_inner_to_null(past_index):
    template = f'''
    integral{past_index}.inner = NULL;
    '''

    return template


def write_to_file(file_name, program):
    with open(file_name, 'w+') as f:
        f.write(program)


def get_block_for_path(index, path):
    func_block = function_block_template()

    block = ''

    eb = 0

    sum_integrals = []
    for i, cur_integrals in enumerate(path):
        add_index = str(index) + '_' + str(i)

        eb += cur_integrals['eb']

        products = []
        for j, cur_integral in enumerate(cur_integrals['integrals']):
            variable_map = dict()
            product_index = str(index) + '_' + str(i) + '_' + str(j)
            past_index = None
            k = 0
            integral_str = ''
            while cur_integral:
                variable_map[cur_integral['var_name']] = k
                current_index = str(k)
                integral_str += get_integral(cur_integral, current_index, past_index, variable_map)
                k += 1
                cur_integral = cur_integral['inner']
                past_index = current_index

            integral_str += set_inner_to_null(past_index)
            integrals_template = function_integrals_template()
            integrals_template = integrals_template.replace('{{ROOT}}', '0')
            integrals_template = integrals_template.replace('{{INDEX}}', str(product_index))
            integrals_template = integrals_template.replace('{{BLOCK}}', integral_str)

            block += integrals_template
            products.append('integrals_' + str(product_index))

        product_block = function_product_block_template()
        product_block = product_block.replace('{{ARRAY}}', ', '.join(products))
        product_block = product_block.replace('{{INDEX}}', add_index)
        block += product_block
        sum_integrals.append('product_integrals_' + add_index)

    func_block = func_block.replace('{{ARRAY}}', ', '.join(sum_integrals))

    func_block = func_block.replace('{{INDEX}}', str(index))

    block += func_block
    return block, eb


def process(paths, paths_output, args):
    whole_block = ''
    probability_array = []
    eb_array = []
    for index, path in enumerate(paths):
        block, eb = get_block_for_path(index, path)
        whole_block += block
        probability_array.append(f'compute_probability_path_{index}')
        eb_array.append(str(eb))

    out = cprog.replace('{{WHOLE_BLOCK}}', whole_block)
    out = out.replace('{{ARRAY}}', ', '.join(probability_array))
    out = out.replace('{{PATHS_OUTPUT}}', ','.join(list(map(lambda x: '"' + x + '"', paths_output))))
    out = out.replace('{{EB}}', ', '.join(eb_array))
    out = out.replace('{{INPUT_SIZE}}', str(args.input_size))

    write_to_file('temp_program.c', out)

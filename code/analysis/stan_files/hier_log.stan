functions{
  real logistic_growth(real t, real y0, real lambda, real K){
    real num = K * y0 * exp(lambda * t);
    real denum = K + y0 * (exp(lambda * t) - 1);
    return num / denum;
  }

}

data {
  // Total number of data points
  int N;

  // Number of entries in each level of the hierarchy
  int J_1;
  int J_2;

  //Index arrays to keep track of hierarchical structure
  int index_1[J_2];
  int index_2[N];

  // The measurements
  real y[N];
  real t[N];
}


parameters {
  // Hyperparameters level 0
  real log_lambda;
  real log_K;
  real log_y0;
  //real log_t0;

  // How hyperparameters vary
  real<lower=0> tau_l;
  real<lower=0> tau_k;
  real<lower=0> tau_y;
  //real<lower=0> tau_t0;

  // Hyperparameters level 1
  vector[J_1] lambda_1_tilde;
  vector[J_1] K_1_tilde;
  vector[J_1] y01_tilde;
  //vector[J_1] t0_1_tilde;

  // Parameters level 2
  vector[J_2] lambda_2_tilde;
  vector[J_2] K_2_tilde;
  vector[J_2] y02_tilde;
  //vector[J_2] t0_2_tilde;

  real<lower=0> sigma_0;
}

transformed parameters{
  real Lambda = 10^log_lambda;
  real K = 10^log_K;
  real y0 = 10^log_y0;
  //real t0 = 10^log_t0;

  // Non-centering level 1
  vector[J_1] theta_lambda_1 = log_lambda + tau_l * lambda_1_tilde;
  vector[J_1] theta_K_1 = log_K + tau_k * K_1_tilde;
  vector[J_1] theta_y0_1 = log_y0 + tau_y * y01_tilde;
  //vector[J_1] t0_1 = log_t0 + tau_t0 * t0_1_tilde;

  // Non-centering level 2
  vector[J_2] theta_lambda_2 = 10^(theta_lambda_1[index_1] + tau_l * lambda_2_tilde);
  vector[J_2] theta_K_2 = 10^(theta_K_1[index_1] + tau_k * K_2_tilde);
  vector[J_2] theta_y0_2 = 10^(theta_y0_1[index_1] + tau_y * y02_tilde);
  //vector[J_2] t0_2 = 10^(t0_1[index_1] + tau_t0 * t0_2_tilde);
    
}

model {
  log_lambda ~ normal(-2.8, 0.5);
  log_K ~ normal(0, 0.1);
  log_y0 ~ normal(-1.5, 0.1);
  //log_t0 ~ normal(-6, 2);

  tau_l ~ normal(0, 0.01);
  tau_k ~ normal(0, 0.01);
  tau_y ~ normal(0, 0.01);
  //tau_t0 ~ normal(0, 0.001);


  lambda_1_tilde ~ normal(0, 1);
  K_1_tilde ~ normal(0, 1);
  y01_tilde ~ normal(0, 1);
  //t0_1_tilde ~ normal(0, 1);

  
  lambda_2_tilde ~ normal(0, 1);
  K_2_tilde ~ normal(0, 1);
  y02_tilde ~ normal(0, 1);
  //t0_2_tilde ~ normal(0, 1);
 
  sigma_0 ~ normal(0, 10^-10);
  real mu[N];
  real sigma[N];
  for (i in 1:N){
    mu[i] = logistic_growth(t[i], theta_y0_2[index_2[i]], theta_lambda_2[index_2[i]], theta_K_2[index_2[i]]);
    sigma[i] = mu[i] * sigma_0;
  } 
  y ~ normal(mu, sigma);
}

generated quantities {
  real y_ppc[N];
  real mu_ppc[N];
  real sigma_ppc[N];
  
  for (i in 1:N){
    mu_ppc[i] = logistic_growth(t[i], theta_y0_2[index_2[i]], theta_lambda_2[index_2[i]], theta_K_2[index_2[i]]);
    sigma_ppc[i] = mu_ppc[i] * sigma_0;
    y_ppc[i] = normal_rng(mu_ppc[i], sigma_ppc[i]);
  }
}



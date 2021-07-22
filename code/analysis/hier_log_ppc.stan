functions{
  real logistic_growth(real t, real y0, real lambda, real K){
    real num = K * y0 * exp(lambda * t);
    real denum = K + y0 * (exp(lambda * t)  -1);
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
  real t[N];
}

generated quantities {
  real log_lambda = normal_rng(-2.8, 0.5);
  real log_K = normal_rng(0, 0.1);
  real log_y0 = normal_rng(-1.5, 0.1);

  real Lambda = 10^log_lambda;
  real K = 10^log_K;
  real y0 = 10^log_y0;
   
  real tau_lambda = abs(normal_rng(0, 0.01));
  real tau_K = abs(normal_rng(0, 0.01));
  real tau_y0 = abs(normal_rng(0, 0.01));

  real lambda_1_tilde[J_1];
  real K_1_tilde [J_1];
  real y0_1_tilde [J_1];

  real lambda_1[J_1];
  real K_1[J_1];
  real y0_1[J_1];
 
  for (i in 1:J_1){
    lambda_1_tilde[i] = normal_rng(0, 1);
    lambda_1[i] = log_lambda + tau_lambda * lambda_1_tilde[i];
    K_1_tilde[i] = normal_rng(0, 1);
    K_1[i] = log_K + tau_K * K_1_tilde[i];
    y0_1_tilde[i] = normal_rng(0, 1);
    y0_1[i] = log_y0 + tau_y0 * y0_1_tilde[i];
  }

  real lambda_2_tilde[J_2];
  real K_2_tilde [J_2];
  real y0_2_tilde [J_2];

  real lambda_2[J_2];
  real K_2[J_2];
  real y0_2[J_2];

  for (i in 1:J_2){
    lambda_2_tilde[i] = normal_rng(0, 1);
    lambda_2[i] = 10^(lambda_1[index_1[i]] + tau_lambda * lambda_2_tilde[i]);
    K_2_tilde[i] = normal_rng(0, 1);
    K_2[i] = 10^(K_1[index_1[i]] + tau_K * K_2_tilde[i]);
    y0_2_tilde[i] = normal_rng(0, 1);
    y0_2[i] = 10^(y0_1[index_1[i]] + tau_y0 * y0_2_tilde[i]);
  }

  real mu[N];
  real y[N];
  real sigma = abs(normal_rng(0, 0.00001));
  
  for (i in 1:N){
    mu[i] = logistic_growth(t[i], y0_2[index_2[i]], lambda_2[index_2[i]], K_2[index_2[i]]);
  }
} 
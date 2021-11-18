functions {
   real poly(
       real K_d,
       real kappa_t,
       real j,
       real delta_r,
       real lambda_0,
       real K_M,
       real V_0,
       real a_ex,
       real lambda
   ){
       real c_1 =  K_d * kappa_t * delta_r;
       real a_4 = c_1 * delta_r / lambda_0^2 - K_M * delta_r / lambda_0;
       vector[5] a_3;
       a_3[1] = - c_1^2;
       a_3[2] = c_1 * K_M/ lambda_0;
       a_3[3] = c_1 * V_0 / lambda_0^2;
       a_3[4] = -2 * c_1 * delta_r / lambda_0;
       a_3[5] = K_M * delta_r;
       vector[8] a_2;
       a_2[1] = 2 * c_1^2 / lambda_0;
       a_2[2] = -j * c_1^2 / lambda_0^2;
       a_2[3] = -c_1 * K_M;
       a_2[4] = j * K_M * c_1 / lambda_0;
       a_2[5] = -V_0 * c_1 / lambda_0;
       a_2[6] = c_1 * delta_r;
       a_2[7] = c_1 * a_ex * j / lambda_0;
       a_2[8] = K_M * a_ex *j;
       vector[4] a_1;
       a_1[1] = -c_1^2;
       a_1[2] = 2 * c_1^2 * j / lambda_0;
       a_1[3] = -c_1 * j * K_M;
       a_1[4] = c_1 * j * a_ex;

       real a_0 = -c_1^2 * j;
       return a_4 * lambda^4 + sum(a_3) * lambda^3 + sum(a_2) * lambda^2 + sum(a_1) * lambda + a_0; 
   }

   vector system(
        vector y,        // unknowns
        vector theta,    // parameters
        real[] x_r, // data (real)
        int[] x_i) {     // data (integer)
  vector[1] z;
  z[1] = poly(theta[1], theta[2], theta[3], theta[4], theta[5], theta[6], theta[7], theta[8], y[1]);
  return z;
}

}

data {
    real K_d;
    real kappa_t;
    real j;
    real delta_r;
    real lambda_0;
    real K_M;
    real V_0;
    int N;
    real a_ex[N];
    
}

transformed data {
  vector[1] y_guess;
  y_guess[1] = 1;
  real x_r[0];
  int x_i[0];
}

parameters {
}

transformed parameters {
  vector[8] theta;
  theta[1] = K_d;
  theta[2] = kappa_t;
  theta[3] = j;
  theta[4] = delta_r;
  theta[5] = lambda_0;
  theta[6] = K_M;
  theta[7] = V_0;
  theta[8] = 0;
  vector[N] y;
  for (i in 1:N){
      theta[8] = a_ex[i];
      y[i] = algebra_solver_newton(system, y_guess, theta, x_r, x_i)[1];
  }
  
}


model {
}
/*
generated quantities {
    real c;
    c = poly(K_d, kappa_t, j, delta_r, lambda_0, K_M, V_0, a_ex, y[1]);
}
*/
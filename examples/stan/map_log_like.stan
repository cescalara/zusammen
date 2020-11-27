functions {
#include cpl.stan
#include pgstat.stan
#include foldinterval.stan
}

data {

  int<lower=1> N_intervals;
  int max_n_echan;
  int max_n_chan;

  int<lower=0> N_dets[N_intervals]; // number of detectors per data type
  int<lower=0> N_chan[N_intervals, max(N_dets)]; // number of channels in each detector
  int<lower=0> N_echan[N_intervals,  max(N_dets)]; // number of energy side channels in each detector

  int grb_id[N_intervals];
  int N_grbs;

  vector[max_n_echan] ebounds_hi[N_intervals, max(N_dets)];
  vector[max_n_echan] ebounds_lo[N_intervals, max(N_dets)];



  vector[max_n_chan] observed_counts[N_intervals, max(N_dets)];
  vector[max_n_chan] background_counts[N_intervals, max(N_dets)];
  vector[max_n_chan] background_errors[N_intervals, max(N_dets)];

  int idx_background_zero[N_intervals, max(N_dets), max_n_chan];
  int idx_background_nonzero[N_intervals, max(N_dets), max_n_chan];
  int N_bkg_zero[N_intervals,max(N_dets)];
  int N_bkg_nonzero[N_intervals,max(N_dets)];

  real exposure[N_intervals, max(N_dets)];

  matrix[max_n_echan, max_n_chan] response[N_intervals, max(N_dets)];


  int mask[N_intervals, max(N_dets), max_n_chan];
  int N_channels_used[N_intervals,max(N_dets)];

  vector[N_intervals] dl;
  vector[N_intervals] z;

  // int N_gen_spectra; 
  // vector[N_gen_spectra] model_energy;

  // int N_correlation; 
  // vector[N_correlation] model_correlation; 

  int N_grid;
  vector[N_grid] gamma_grid;
  vector[N_grid] delta_grid;
  vector[N_intervals] alpha;
  vector[N_intervals] log_epeak;
}

transformed data {
  int grainsize = 1; // for multi threading
  
  real emin = 10.;
  real emax = 1.E4;

  vector[N_intervals] log_zp1 = log10(z+1);

  vector[max_n_echan] ebounds_add[N_intervals, max(N_dets)];
  vector[max_n_echan] ebounds_half[N_intervals, max(N_dets)];

  int all_N[N_intervals];

  // precalculation of energy bounds

  for (n in 1:N_intervals) {

    all_N[n] = n;

    for (m in 1:N_dets[n]) {

      ebounds_half[n, m, :N_echan[n, m]] = 0.5*(ebounds_hi[n, m, :N_echan[n, m]]+ebounds_lo[n, m, :N_echan[n, m]]);
      ebounds_add[n, m, :N_echan[n, m]] = (ebounds_hi[n, m, :N_echan[n, m]] - ebounds_lo[n, m, :N_echan[n, m]])/6.0;
  
    }

  }


}

generated quantities {

  matrix[N_grid, N_grid] log_like;

  vector[N_intervals] log_energy_flux;
  vector[N_intervals] log_epeak_rest_norm;
  
  for (i in 1:N_grid) {
    for (j in 1:N_grid) {
      
      log_epeak_rest_norm = log_epeak + log_zp1 - 2;
      log_energy_flux = delta_grid[i] + gamma_grid[j] * log_epeak_rest_norm;

      
      log_like[i][j] = reduce_sum(partial_log_like, all_N, grainsize,  alpha,  log_epeak,  log_energy_flux,  observed_counts,
				  background_counts, background_errors, mask, N_channels_used, exposure,  ebounds_lo,
				  ebounds_hi,  ebounds_add,  ebounds_half,  response,  idx_background_zero,
				  idx_background_nonzero,  N_bkg_zero,  N_bkg_nonzero, N_dets,  N_chan,
				  N_echan,  max_n_chan,  emin,  emax);
      
    }
  }
  
}

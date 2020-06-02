import numpy as np

from cosmogrb.sampler.source_function import SourceFunction

from .corr_cpl_functions import (
    corr_cpl_evolution,
    energy_integrated_evolution,
    sample_energy,
    sample_events,
    time_integrated_evolution,
)


class CorrCPLSourceFunction(SourceFunction):
    def __init__(
        self,
        peak_flux=1e-6,
        ep_start=300,
        ep_tau=1.0,
        alpha=-1.0,
        emin=10.0,
        emax=1e4,
        Nrest=1e52,
        gamma=1.5,
        response=None,
    ):

        self._peak_flux = peak_flux
        self._ep_start = ep_start
        self._ep_tau = ep_tau
        self._alpha = alpha
        self._Nrest = Nrest
        self._gamma = gamma

        assert alpha < 0.0, "the rejection sampler is slow as fuck if alpha is positive"

        super(CorrCPLSourceFunction, self).__init__(
            emin=emin, emax=emax, index=alpha, response=response
        )

    def evolution(self, energy, time):

        return corr_cpl_evolution(
            energy=np.atleast_1d(energy),
            time=np.atleast_1d(time),
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            emin=self._emin,
            emax=self._emax,
            alpha=self._alpha,
            redshift=self._source._z,
            Nrest=self._Nrest,
            gamma=self._gamma,
        )

    def time_integrated_spectrum(self, energy, tmin, tmax):

        return time_integrated_evolution(
            energy=np.atleast_1d(energy),
            tmin=tmin,
            tmax=tmax,
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            trise=self._trise,
            tdecay=self._tdecay,
            emin=self._emin,
            emax=self._emax,
            effective_area=self._response.effective_area_packed,
        )

    def energy_integrated_evolution(self, time):

        ea = self._response.effective_area_packed

        return energy_integrated_evolution(
            emin=self._emin,
            emax=self._emax,
            time=np.atleast_1d(time),
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            redshift=self._source._z,
            Nrest=self._Nrest,
            gamma=self._gamma,
            effective_area=ea,
        )

    def sample_events(self, tstart, tstop, fmax):

        return sample_events(
            emin=self._emin,
            emax=self._emax,
            tstart=tstart,
            tstop=tstop,
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            redshift=self._source._z,
            Nrest=self._Nrest,
            gamma=self._gamma,
            effective_area=self._response.effective_area_packed,
            fmax=fmax,
        )

    def sample_energy(self, times):

        ea = self._response.effective_area_packed

        return sample_energy(
            times=times,
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            redshift=self._source._z,
            Nrest=self._Nrest,
            gamma=self._gamma,
            emin=self._emin,
            emax=self._emax,
            effective_area=ea,
        )

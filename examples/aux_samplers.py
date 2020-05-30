import numpy as np

import popsynth


class TDecaySampler(popsynth.AuxiliarySampler):

    sigma = popsynth.auxiliary_sampler.AuxiliaryParameter(default=1)

    def __init__(self):
        """
        samples the decay of the of the pulse
        """

        super(TDecaySampler, self).__init__(name="tdecay", observed=False)

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values
        trise = self._secondary_samplers["trise"].true_values

        self._true_values = (
            1.0 / 50.0 * (10 * t90 + trise + np.sqrt(trise) * np.sqrt(20 * t90 + trise))
        )


class DurationSampler(popsynth.AuxiliarySampler):

    sigma = popsynth.auxiliary_sampler.AuxiliaryParameter(default=1)

    def __init__(self):
        """
        samples how long the pulse lasts
        """

        super(DurationSampler, self).__init__(name="duration", observed=False)

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values

        self._true_values = 1.5 * t90


class LumSampler(popsynth.DerivedLumAuxSampler):
    """
    Sample luminosity from Epeak
    """

    Nrest = popsynth.auxiliary_sampler.AuxiliaryParameter(default=1e52)
    gamma = popsynth.auxiliary_sampler.AuxiliaryParameter(default=1.5, vmin=0)
    s_scat = popsynth.auxiliary_sampler.AuxiliaryParameter(default=0.3)

    def __init__(self):

        super(LumSampler, self).__init__(name="luminosity")

    def compute_luminosity(self):

        secondary = self._secondary_samplers["Epeak"]

        Epeak = 10 ** secondary.true_values  # keV

        lum = self.Nrest * np.power(Epeak / 100, self.gamma)  # erg s^-1

        tmp = np.random.normal(0, self.s_scat * lum)

        return lum + tmp

    def true_sampler(self, size):

        self._true_values = self.compute_luminosity()


class DerivedEpeakSampler(popsynth.AuxiliarySampler):
    """
    Samples Epeak for a given L
    """

    Nrest = popsynth.auxiliary_sampler.AuxiliaryParameter(default=1e52)
    gamma = popsynth.auxiliary_sampler.AuxiliaryParameter(default=1.5, vmin=0)
    s_scat = popsynth.auxiliary_sampler.AuxiliaryParameter(default=0.1)

    s_det = popsynth.auxiliary_sampler.AuxiliaryParameter(default=0.1)

    def __init__(self):

        super(DerivedEpeakSampler, self).__init__(
            "derived_Epeak", observed=True, uses_luminosity=True, uses_distance=True
        )

    def true_sampler(self, size):

        index = (np.log10(self._luminosity) - np.log10(self.Nrest)) / self.gamma
        Ep = np.power(10, index) * 100  # keV

        s = np.random.normal(0, self.s_scat * Ep, size)

        self._true_values = Ep + s

    def observation_sampler(self, size):

        Ep_obs = self._true_values / (1 + self._distance)

        s = np.random.normal(0, self.s_det * self._true_values, size)

        self._obs_values = Ep_obs + s
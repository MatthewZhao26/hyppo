import numpy as np

from scipy._lib._util import MapWrapper


class _ParallelP(object):
    """
    Helper function to calculate parallel p-value.
    """
    def __init__(self, test, sim, n, p, noise):
        self.test = test()
        self.sim = sim

        self.n = n
        self.p = p
        self.noise = noise

    def __call__(self, index):
        if (self.sim.__name__ == "multiplicative_noise" or
            self.sim.__name__ == "multimodal_independence"):
            x, y = self.sim(self.n, self.p)
        else:
            x, y = self.sim(self.n, self.p, noise=self.noise)

        obs_stat = self.test._statistic(x, y)

        permx = np.random.permutation(x)
        permy = np.random.permutation(y)

        # calculate permuted stats, store in null distribution
        perm_stat = self.test._statistic(permx, permy)

        return obs_stat, perm_stat


def _perm_test(test, sim, n=100, p=1, noise=0.0, alpha=0.05, reps=1000,
               workers=-1):
    r"""
    Helper function that calculates the p-value.

    Parameters
    ----------
    test : callable()
        The independence test class requested.
    sim : callable()
        The simulation used to generate the input data.
    reps : int, optional (default: 1000)
        The number of replications used to estimate the null distribution
        when using the permutation test used to calculate the p-value.
    workers : int, optional (default: -1)
        The number of cores to parallelize the p-value computation over.
        Supply -1 to use all cores available to the Process.

    Returns
    -------
    null_dist : list
        The approximated null distribution.
    """

    # use all cores to create function that parallelizes over number of reps
    mapwrapper = MapWrapper(workers)
    parallelp = _ParallelP(test=test, sim=sim, n=n, p=p, noise=noise)
    alt_dist, null_dist = map(list, zip(*list(mapwrapper(parallelp, range(reps)))))
    alt_dist = np.array(alt_dist)
    null_dist = np.array(null_dist)

    return alt_dist, null_dist


def power(test, sim, n=100, p=1, noise=0, alpha=0.05, reps=1000, workers=-1):
    """
    [summary]

    Parameters
    ----------
    test : [type]
        [description]
    sim : [type]
        [description]
    n : int, optional
        [description], by default 100
    p : int, optional
        [description], by default 1
    noise : int, optional
        [description], by default 0
    reps : int, optional
        [description], by default 1000
    alpha : float, optional
        [description], by default 0.05
    """

    alt_dist, null_dist = np.abs(_perm_test(test, sim, n=n, p=p, noise=noise,
                                            alpha=alpha, reps=reps,
                                            workers=workers))
    cutoff = np.sort(null_dist)[int(np.ceil(reps * (1-alpha)))]
    empirical_power = (alt_dist >= cutoff).sum() / reps

    return empirical_power
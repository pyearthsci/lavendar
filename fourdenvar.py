# 3rd party modules:
import numpy as np
import scipy.optimize as spop
import scipy.linalg as splinal
# local modules:
import experiment_setup as es


class FourDEnVar:
    """
    Class for performing 4DEnVar data assimilation
    :param assim: switch to create matrices necessary for running data assimilation routines (bool)
    :param run_xb: switch to run JULES for the prior values specified in experiment_setup module (bool)
    :param seed_val: seed value to use in any random drawing within class (int)
    """
    def __init__(self, assim=False, seed_val=es.seed_value):
        # set parameters to optimize and prior values
        self.p_dict = es.opt_params
        self.p_keys = []
        self.xb = []
        self. val_bnds = []
        for filename in self.p_dict.keys():
            for nml in self.p_dict[filename].keys():
                for param in self.p_dict[filename][nml].keys():
                    self.p_keys.append(param)
                    self.xb.append(self.p_dict[filename][nml][param][1])
                    self.val_bnds.append(self.p_dict[filename][nml][param][2])
        self.xb = np.array(self.xb)

        # Set ensemble size and seed value
        self.size_ens = es.ensemble_size
        self.seed_val = seed_val

        # set prior error and generate prior ensemble
        self.prior_err = es.prior_err
        self.xb_sd = self.xb * self.prior_err
        self.b_mat = np.eye(len(self.xb))*((self.xb_sd)**2)
        self.xbs = self.generate_param_ens(self.size_ens)
        self.make_obs()

        # create necessary matrices for running data assimilation routine if specified to at instantiation of JulesDA
        # class
        # NOTE: ensemble must have been run beforehand
        if assim is True:
            self.make_hxb()
            self.create_ensemble()

    def make_obs(self):
        # extract observations using function specified in experiment_setup module
        obs_dic = es.obs_fn()
        self.yoblist = np.concatenate(obs_dic['obs'])
        self.yerr = np.concatenate(obs_dic['obs_err'])
        self.rmatrix = np.eye(len(self.yerr))*self.yerr**2

    def make_hxb(self):
        # creates hxb and Xb ensemble matrix given function in experiment_setup module
        hxb_dic = es.jules_hxb()
        self.hxb = np.concatenate(hxb_dic['obs'])
        self.xb_mat = (1./(np.sqrt(self.size_ens-1)))*np.array([xbi - self.xb for xbi in self.xbs])
        self.xb_mat_inv = np.linalg.pinv(self.xb_mat.T)

    def create_ensemble(self):
        # creates HMXb matrix using function to extract modelled observations in experiment_setup module
        self.hm_xbs = es.jules_hxb_ens()
        self.hmx_mat = (1. / (np.sqrt(self.size_ens - 1))) * np.array([hmxb - self.hxb for hmxb in self.hm_xbs])

    def xvals2wvals(self, xvals):
        """
        Make change of variables from parameter space to ensemble space
        :param xvals: array of parameter values
        :return: array of ensemble weights
        """
        return np.dot(self.xb_mat_inv, (xvals - self.xb))

    def wvals2xvals(self, wvals):
        """
        Make change of variables from ensemble space to parameter space
        :param wvals: array of ensemble member weights
        :return: array of parameter values
        """
        return self.xb + np.dot(self.xb_mat.T, wvals)

    def obcost_ens_inc(self, wvals):
        """
        Calculates the observational part of the 4DEnVar cost function
        :param wvals: array of ensemble weights, w
        :return: value of the observation part of cost function as float
        """
        return np.dot(np.dot((np.dot(self.hmx_mat.T, wvals) + self.hxb - self.yoblist), np.linalg.inv(self.rmatrix)),
                      (np.dot(self.hmx_mat.T, wvals) + self.hxb - self.yoblist).T)

    def cost_ens_inc(self, wvals):
        """
        Calculates the pior part of the 4DEnVar cost function
        :param wvals: array of ensemble weights, w
        :return: value of the prior part of the cost function as float
        """
        modcost = np.dot(wvals, wvals.T)
        obcost = self.obcost_ens_inc(wvals)
        ret_val = 0.5 * obcost + 0.5 * modcost
        return ret_val

    def gradcost_ens_inc(self, wvals):
        """
        Calculates the gradient of the 4DEnVar cost function
        :param wvals: array of ensemble weights, w
        :return: vector of the gradient of the cost function as array
        """
        obcost = np.dot(self.hmx_mat, np.dot(np.linalg.inv(self.rmatrix),
                                           (np.dot(self.hmx_mat.T, wvals) + self.hxb - self.yoblist).T))
        gradcost = obcost + wvals  # + bnd_cost
        return gradcost

    def a_cov(self):
        """
        Calculates the analysis (posterior) error covariance matrix
        :return: analysis error covariance matrix as array
        """
        a_cov = np.linalg.inv(splinal.sqrtm(np.eye(self.size_ens) + np.dot(self.hmx_mat,
                        np.dot(np.linalg.inv(self.rmatrix), self.hmx_mat.T))))
        return a_cov

    def a_ens(self, xa):
        """
        Creates the analysis (posterior) ensemble given the posterior parameter vector xa
        :param xa: posterior parameter vector as array
        :return: posterior parameter ensemble as array
        """
        a_cov = self.a_cov()
        xa_mat = np.dot(self.xb_mat.T, a_cov).T
        a_ens = np.array([(xa + np.sqrt(self.size_ens-1)*xbi).real for xbi in xa_mat])
        return a_ens

    def find_min_ens_inc(self, dispp=5):
        """
        Function minimises the 4DEnVar cost function using a newton conjugate gradient method
        :param dispp: amount of information to be printed to command line (int)
        :return: output of minimization as a tuple and posterior parameter vector as array
        """
        wvals = self.xvals2wvals(self.xb)
        find_min = spop.fmin_ncg(self.cost_ens_inc, wvals, fprime=self.gradcost_ens_inc, disp=dispp, full_output=1,
                                 maxiter=20000)
        xa = self.wvals2xvals(find_min[0])
        return find_min, xa

    def test_bnds(self, xbi):
        """
        Function tests if a given parameter vector (xbi) is within the specified bounds (self.val_bnds)
        :param xbi: parameter vector to test as an array
        :return: Bool
        """
        for xi in enumerate(xbi):
            if self.val_bnds[xi[0]][0] <= xi[1] <= self.val_bnds[xi[0]][1]:
                continue
            else:
                return False
        return True

    def generate_param_ens(self, size_ens, x=None):
        """
        Generates a ensemble of parameter vectors given a mean (self.xb) and covariance matrix (self.b_mat)
        :param size_ens: size of ensemble to generate as int
        :param x: mean of distribution to draw from as array, default self.xb
        :return: ensemble of parameter vectors as array
        """
        ens = []
        i = 0
        if x is None:
            x = self.xb
        else:
            x = x
        np.random.seed(self.seed_val)
        while len(ens) < size_ens:
            xbi = np.random.multivariate_normal(x, self.b_mat)
            i += 1
            if self.test_bnds(xbi) is True:
                ens.append(xbi)
            else:
                continue
        return np.array(ens)

    def perturb_true_state(self, x_truth, err=0.05):
        """
        Perturbs the values of a parameter vector (x_truth) given a percentage error value (err), used in twin
        experiments to find a prior parameter vecotr (self.xb)
        :param x_truth: paramter vector to be perturbed as array
        :param err: error with which to perturb paramters as float, default 5% (0.05)
        :return: perturbed paramter vector as array
        """
        i = 0
        np.random.seed(self.seed_val)
        while i < 1:
            xbi = np.random.multivariate_normal(x_truth, (err*self.x_true)**2 * np.eye(len(self.x_true)))
            if self.test_bnds(xbi) is True:
                i += 1
            else:
                continue
        return np.array(xbi)

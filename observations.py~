# 3rd party modules:
import numpy as np
import netCDF4 as nc
import random
# local modules:
import experiment_setup as es


def extract_twin_data(mod_truth='output/model_truth/mod_truth.daily.nc', seed_val=0):
    """
    Function for extracting observations to be assimilated in data assimilation experiments. Here we are running a twin
    experiment using a "model truth" to draw observations from.
    :param mod_truth: location of netCDF file containing "model truth" output (str)
    :param seed_val: seed value for adding random noise to the observations (int)
    :return: dictionary containing observations and observation errors (dictionary)
    """
    # open model truth netCDF file
    mod_dat = nc.Dataset(mod_truth, 'r')
    # set position of observations
    gpp_obs_position = np.array([141, 143, 146, 148, 155, 157, 158, 160, 161, 162,
       163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 175, 176,
       177, 179, 180, 182, 183, 184, 186, 187, 190, 191, 194, 196, 197,
       198, 199, 200, 201, 202, 203, 204, 206, 207, 208, 209, 210, 211,
       213, 214, 215, 218, 219, 220, 222, 223, 225, 228, 229, 230, 231,
       233, 234, 239, 240, 241, 242, 243, 244, 245, 247, 248, 249, 251,
       252, 259, 260])
    lai_obs_position = np.array([167, 187, 198, 209, 225])
    canht_obs_position = np.array([167, 187, 198, 225, 248, 262])
    # extract observations from netCDF file
    gpp_obs_tr = 1000 * 60 * 60 * 24 * mod_dat.variables['gpp'][gpp_obs_position, 7, 0, 0]
    lai_obs_tr = mod_dat.variables['lai'][lai_obs_position, 7, 0, 0]
    canht_obs_tr = mod_dat.variables['canht'][canht_obs_position, 7, 0, 0]
    # set error with which to perturb extracted observations
    gpp_err = np.mean(gpp_obs_tr[gpp_obs_tr > 0]) * 0.01
    lai_err = np.mean(lai_obs_tr[lai_obs_tr > 0]) * 0.01
    canht_err = np.mean(canht_obs_tr[canht_obs_tr > 0]) * 0.01
    # perturb "model truth" observations
    np.random.seed(seed_val)
    gpp_obs = np.array([gpp + np.random.normal(0.0, gpp_err) for gpp in gpp_obs_tr])
    np.random.seed(seed_val)
    lai_obs = np.array([lai + np.random.normal(0.0, lai_err) for lai in lai_obs_tr])
    np.random.seed(seed_val)
    canht_obs = np.array([canht + np.random.normal(0.0, canht_err) for canht in canht_obs_tr])
    # define observation errors to use within data assimilation (will be used to create observation error covariance
    # matrix)
    gpp_err = np.ones(len(gpp_obs)) * np.mean(gpp_obs[gpp_obs > 0]) * 0.02  # 2% error in mod obs
    lai_err = np.ones(len(lai_obs)) * np.mean(lai_obs[lai_obs > 0]) * 0.02
    canht_err = np.ones(len(canht_obs)) * np.mean(canht_obs[canht_obs > 0]) * 0.02
    # close netCDF file
    mod_dat.close()
    return {'obs': (gpp_obs, lai_obs, canht_obs), 'obs_err': (gpp_err, lai_err, canht_err), 'gpp_obs': gpp_obs,
            'gpp_pos': gpp_obs_position, 'gpp_err': gpp_err, 'lai_obs': lai_obs, 'lai_pos': lai_obs_position,
            'lai_err': lai_err, 'canht_obs': canht_obs, 'canht_pos': canht_obs_position, 'canht_err': canht_err}


def extract_jules_hx(nc_file):
    """
    Function extracting the modelled observations from JULES netCDF files
    :param nc_file: netCDF file to extract observations from (str)
    :return: dictionary containing observations (dict)
    """
    nc_dat = nc.Dataset(nc_file, 'r')
    # set position of observations to correspond with assimilated observations
    gpp_ob_position = np.array([141, 143, 146, 148, 155, 157, 158, 160, 161, 162,
       163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 175, 176,
       177, 179, 180, 182, 183, 184, 186, 187, 190, 191, 194, 196, 197,
       198, 199, 200, 201, 202, 203, 204, 206, 207, 208, 209, 210, 211,
       213, 214, 215, 218, 219, 220, 222, 223, 225, 228, 229, 230, 231,
       233, 234, 239, 240, 241, 242, 243, 244, 245, 247, 248, 249, 251,
       252, 259, 260])
    lai_ob_position = np.array([167, 187, 198, 209, 225])
    canht_ob_position = np.array([167, 187, 198, 225, 248, 262])
    # extract observations from netCDF file
    gpp_hx = 1000 * 60 * 60 * 24 * nc_dat.variables['gpp'][gpp_ob_position, 7, 0, 0]
    lai_hx = nc_dat.variables['lai'][lai_ob_position, 7, 0, 0]
    canht_hx = nc_dat.variables['canht'][canht_ob_position, 7, 0, 0]
    # close netCDF file
    nc_dat.close()
    return {'obs': (gpp_hx, lai_hx, canht_hx)}


def extract_jules_hxb():
    """
    Function to extract modelled observations for prior JULES run
    :return: dictionary containing observations (dict)
    """
    return extract_jules_hx(es.output_directory+'/background/xb0.daily.nc')


def extract_jules_hxb_ens():
    """
    Function to extract ensemble of modelled observations from prior model ensemble
    :return: ensemble of modelled observations (lst)
    """
    hm_xbs = []
    for xb_fname in xrange(0, es.ensemble_size):
        hxbi_dic = extract_jules_hx(es.output_directory + '/ensemble0/ens' + str(xb_fname) + '.daily.nc')
        hxbi = np.concatenate(hxbi_dic['obs'])
        hm_xbs.append(hxbi)
    return hm_xbs

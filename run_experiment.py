# core python modules:
import os
import sys
from functools import partial
from contextlib import contextmanager
# 3rd party modules:
import multiprocessing as mp
import shutil as sh
import glob
import pickle
# local modules:
import fourdenvar
import experiment_setup as es
import run_jules as rjda


@contextmanager
def poolcontext(*args, **kwargs):
    """
    Function to control the parallel run of other functions
    :param args:
    :param kwargs:
    :return:
    """
    pool = mp.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


def ens_member_run(ens_number_xi, seed_val=0, params=None, xa=False):
    """
    Function to run a prior or posterior ensemble member
    :param ens_number_xi: tuple of ensemble member number (int) and corresponding parameter vector (arr)
    :param seed_val: seed value used for any perturbations within experiment (int)
    :param params: parameters to update in ensemble member run (lst)
    :param xa: specify if this is a prior or posterior ensemble member (bool)
    :return: string confirming ensemble member has run (str)
    """
    if xa is True:
        ens_dir = '/ensemble_xa_'
    else:
        ens_dir = '/ensemble'
    ens_number = ens_number_xi[0]
    xi = ens_number_xi[1]
    out_dir = 'output_seed' +str(seed_val) + '_ens_' + str(ens_number) + '/'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for file in glob.glob(es.nml_directory + '/*.nml'):
        sh.copy(file, out_dir)
    try:
        rj = rjda.RunJulesDa(params=params, values=xi, nml_dir=out_dir)
        if not os.path.exists(es.output_directory+ens_dir+str(seed_val)):
            os.makedirs(es.output_directory+ens_dir+str(seed_val))
        rj.run_jules_dic(output_name='ens'+str(ens_number), out_dir=es.output_directory+ens_dir+str(seed_val))
        dumps = glob.glob(es.output_directory+ens_dir + str(seed_val) + '/ens'+str(ens_number)+'.dump*')
        for f in dumps:
            os.remove(f)
        sh.rmtree(out_dir)
    except ValueError:
        sh.rmtree(out_dir)
        print 'Something went wrong at: ' + str(ens_number)
    return 'ensemble member '+str(ens_number)+' run!'


def ens_run(x_ens, seed_val=0, xa=False, params=None):
    """
    Perform a parallel run of JULES models given an ensemble of paramter vectors
    :param x_ens: ensemble of paramter vectors (arr)
    :param seed_val: seed value used for any perturbations in the experiment (int)
    :param xa: switch if this is a prior or posterior ensemble run (bool)
    :param params: list of paramters being updated in experiment (lst)
    :return: string confirming if the ensemble has been run (str)
    """
    print 'Running ensemble'
    mp.freeze_support()
    with poolcontext(processes=es.num_processes) as pool:
        res = pool.map(partial(ens_member_run, seed_val=seed_val, params=params, xa=xa), enumerate(x_ens))
    pool.close()
    pool.join()
    return 'Ensemble has been run'


if __name__ == "__main__":
    # instantiate JULES data assimilation class
    jda = fourdenvar.FourDEnVar(seed_val=int(sys.argv[1]))
    seed_val = int(sys.argv[1])
    params = jda.p_keys
    # if 'run_xb' is in system arguments then run JULES with prior parameters
    if 'run_xb' in sys.argv:
        nml_dir = 'output_seed' + str(seed_val) + '_xb/'
        if not os.path.exists(nml_dir):
            os.makedirs(nml_dir)
        for file in glob.glob(es.nml_directory + '/*.nml'):
            sh.copy(file, nml_dir)
        rj = rjda.RunJulesDa(params=params, values=jda.xb, nml_dir=nml_dir)
        rj.run_jules_dic(output_name='xb' + str(jda.seed_val), out_dir=es.output_directory+'/background/')
        sh.rmtree(nml_dir)
    # remove any old output in folders
    old_outs = glob.glob(es.output_directory + '/ensemble' + str(seed_val) + '/*.nc')
    for f in old_outs:
        os.remove(f)
    # run prior ensemble
    ens_run(jda.xbs, seed_val=jda.seed_val, params=params)
    # if 'run_xa' is in system arguments then run posterior ensemble
    if 'run_xa' in sys.argv:
        jda = fourdenvar.FourDEnVar(assim=True, seed_val=int(sys.argv[1]))
        params = jda.p_keys
        # find posterior estimate and posterior ensemble
        xa = jda.find_min_ens_inc()
        xa_ens = jda.a_ens(xa[1])
        # pickle posterior parameter ensemble array
        f = open(es.output_directory+'/xa_ens' + str(es.ensemble_size) + '_seed' + sys.argv[1] + '.p', 'wb')
        pickle.dump(xa_ens, f)
        f.close()
        # remove any old output in folders
        old_outs = glob.glob(es.output_directory + '/ensemble_xa_' + str(seed_val) + '/*.nc')
        for f in old_outs:
            os.remove(f)
        # run posterior ensemble
        ens_run(xa_ens, seed_val=jda.seed_val, xa=True, params=params)
    if 'plot' in sys.argv:
        es.save_plots(es.output_directory+'/xa_ens' + str(es.ensemble_size) + '_seed' + sys.argv[1] + '.p',
                      es.plot_output_dir)
    print 'Experiment has been run'
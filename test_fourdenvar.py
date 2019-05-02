import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import fourdenvar as fdj
import seaborn as sns
import run_jules as rj


def test_cost_ens_inc(jj, alph=1e-8, vect=0):
    """Test for cost and gradcost functions.
    """
    pvals = 1.03*jj.xb
    wvals = jj.xvals2wvals(pvals)
    print wvals
    #wvals = np.array([0.]*jj.size_ens)
    gradj = jj.gradcost_ens_inc(wvals)
    #print gradj
    if vect == 0:
        h = wvals*(np.linalg.norm(wvals))**(-1)
    elif vect == 1:
        h = gradj*(np.linalg.norm(gradj))**(-1)
    elif vect == 2:
        h = np.ones(len(wvals))*(np.sqrt(len(wvals))**-1)
    print h
    j = jj.cost_ens_inc(wvals)
    print j
    jalph = jj.cost_ens_inc(wvals + alph*h)
    print jalph - j
    print np.dot(alph*h.T, gradj)
    print (jalph-j) / (np.dot(alph*h.T, gradj))
    return abs(jalph-j) / (np.dot(alph*h.T, gradj))


def plotcostone_ens_inc(vect=1):
    """Using test_cost plots convergance of cost fn gradient for decreasing
    value of alpha.
    """
    sns.set_context('poster', font_scale=1.5, rc={'lines.linewidth':1, 'lines.markersize':6})
    fig, ax = plt.subplots(nrows=1, ncols=1,)#figsize=(10,10))
    sns.set_style('whitegrid')
    power=np.arange(1,10,1)
    xlist = [10**(-x) for x in power]
    jj = fdj.FourDEnVar(assim=True)
    #jj.output_dir="output/ens_run500"
    tstlist = [abs(test_cost_ens_inc(jj, x, vect)) for x in xlist]
    ax.semilogx(xlist, tstlist, 'k', marker='x', mew=1, ms=8)
    #font = {'size'   : 24}
    #matplotlib.rc('font', **font)
    plt.xlabel(r'$\eta$')
    plt.ylabel(r'$|f(\eta)|$')
    #plt.title('test of the gradient of the cost function')
    print tstlist
    #plt.show()
    return ax, fig


def plotcost_ens_inc(vect=1):
    """Using test_cost plots convergance of cost fn gradient for decreasing
    value of alpha.
    """
    sns.set_context('poster', font_scale=1.5, rc={'lines.linewidth':1, 'lines.markersize':6})
    fig, ax = plt.subplots(nrows=1, ncols=1,)#figsize=(10,10))
    sns.set_style('whitegrid')
    power=np.arange(1,10,1)
    xlist = [10**(-x) for x in power]
    jj = fdj.FourDEnVar(assim=True)
    #jj.output_dir="output/ens_run500"
    tstlist = [abs(test_cost_ens_inc(jj, x, vect)-1) for x in xlist]
    ax.loglog(xlist, tstlist, 'k', marker='x', mew=1, ms=8)
    #font = {'size'   : 24}
    #matplotlib.rc('font', **font)
    plt.xlabel(r'$\eta$')
    plt.ylabel(r'$|f(\eta) - 1|$')
    #plt.title('test of the gradient of the cost function')
    print tstlist
    #plt.show()
    return ax, fig
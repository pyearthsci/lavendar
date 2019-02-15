# 3rd party modules:
import numpy as np
# local modules:
import jules
import experiment_setup as es


def jules_run(parameters=['neff_io'], p_values=[5.7e-4], nml_directory='example_nml',
              out_name='test', output_dir='../output/test/'):
    """
    Function that creates a class instance of RunJulesDa and runs JULES
    :param parameters: parameters to vary (lst)
    :param p_vaules: values for parameters (lst)
    :param nml_directory: directory of nml files (str)
    :param out_name: name for output files (str)
    :param output_dir: directory to save output in (str)
    :return: message string that JULES has run
    """
    rj = RunJulesDa(params=parameters, values=p_values, nml_dir=nml_directory)
    rj.run_jules_dic(output_name=out_name, out_dir=output_dir)
    return 'finished JULES run'


class RunJulesDa:
    """
    Class to update nml parameters and run JULES
    :param params: parameters to vary as a list of strings (lst)
    :param values: either (str) 'default' to run with unchanged parameters or an array of paramter values (arr)
    :param nml_dir: nml directory from which to run JULES (str)
    :param year: year for which to run JULES (int)
    """
    def __init__(self, params=['neff_io'], values='default', nml_dir='example_nml', year=2008):
        self.p_keys = params
        self.nml_dir = nml_dir
        self.year = year
        # mod_truth and background
        self.p_dict = es.opt_params
        if values is not 'default':
            for filename in self.p_dict.keys():
                for nml in self.p_dict[filename].keys():
                    for param in self.p_dict[filename][nml].keys():
                        if param in self.p_keys:
                            self.p_dict[filename][nml][param][1] = values[np.where(np.array(self.p_keys)==param)[0][0]]

    def run_jules_dic(self, output_name='test', out_dir='../output/test'):
        """
        Function that runs JULES with crop model turned on and given user defined parameters. Output is saved in folder
        and file specified within function.

        :param output_name: Name to use for outputted JULES netCDF file.
        :type output_name: str.
        :param output_dir: Directory for writing JULES output.
        :type output_dir: str.
        :return: 'Done' to notify used JULES run has finished.
        :rtype: str
        """
        j = jules.Jules(self.nml_dir)
        j.nml_dic['output']['jules_output']['run_id'] = output_name
        j.nml_dic['output']['jules_output']['output_dir'] = out_dir
        j.nml_dic['timesteps']['jules_time']['main_run_start'] = str(self.year) + '-01-01 06:00:00'
        j.nml_dic['timesteps']['jules_time']['main_run_end'] = str(self.year+1) + '-01-01 05:00:00'
        j.nml_dic['timesteps']['jules_spinup']['max_spinup_cycles'] = 0  # 0 2  4

        for filename in self.p_dict.keys():
            for nml in self.p_dict[filename].keys():
                for param in self.p_dict[filename][nml].keys():
                    if self.p_dict[filename][nml][param][0] is not 'None':
                        j.nml_dic[filename][nml][param][self.p_dict[filename][nml][param][0]] = \
                            self.p_dict[filename][nml][param][1]
                    else:
                        j.nml_dic[filename][nml][param] = self.p_dict[filename][nml][param][1]
        j.run_jules()
        return output_name, 'done'

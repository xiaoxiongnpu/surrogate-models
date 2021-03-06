__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

# ==============================================================================
# description     :runs openMDAO optimization on wing-structure
# author          :Juri Bieler
# date            :2018-07-13
# notes           :
# python_version  :3.6
# ==============================================================================


from datetime import datetime
import numpy as np
from scipy import optimize

from wingconstruction.wingutils.constants import Constants
from wingconstruction.multi_run import MultiRun
from wingconstruction.wingutils.defines import *
from myutils.plot_helper import PlotHelper
from myutils.time_track import TimeTrack

PROJECT_NAME_PREFIX = 'newtonOpti'
LOG_FILE_PATH = Constants().WORKING_DIR + '/' + PROJECT_NAME_PREFIX + datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.csv'
USE_ABA = True
PGF = True


class NewtonOpt:

    def __init__(self):
        pass

    def opti_it(self, rib_range=range(10, 23)):
        ######################
        ### needed Objects ###
        self.runner = MultiRun(use_calcu=not USE_ABA, use_aba=USE_ABA, non_liner=False, project_name_prefix=PROJECT_NAME_PREFIX, force_recalc=False)
        self.executionCounter = 0
        self.write_newton_log('iter,time,ribs,shell,stress,weight')
        self.timer = TimeTrack()

        opti_ribs = []
        opti_shell = []
        opti_stress = []
        opti_weights = []
        for r in rib_range:
            r = int(r)
            init_guess = (range_shell[0] + range_shell[1]) / 2.
            self.executionCounter = 0
            root = optimize.newton(self.shell_predict, init_guess, args=[r], tol=1.48e-08, maxiter=50)
            opti_ribs.append(r)
            opti_shell.append(root)
            stress, weight = self.calc_stress_weight(root, r)
            opti_stress.append(stress)
            opti_weights.append(weight)
            print('execution count: {:d}'.format(self.executionCounter))
            self.write_newton_log(str(self.executionCounter) + ','
                           + str(self.timer.get_time()) + ','
                           + str(r) + ','
                           + str(root) + ','
                           + str(stress) + ','
                           + str(weight))
        print('DONE')
        print(opti_ribs)
        print(opti_shell)
        print(opti_stress)
        print(opti_weights)
        best_i = opti_weights.index(min(opti_weights))
        print('BEST:')
        print('ribs:' + str(opti_ribs[best_i]))
        print('shell:' + str(opti_shell[best_i]))
        print('stress:' + str(opti_stress[best_i]))
        print('weight:' + str(opti_weights[best_i]))

    def shell_predict(self, shell_thick, rib_num):
        if shell_thick > range_shell[1]:
            shell_thick = range_shell[1]
        if shell_thick < range_shell[0]:
            shell_thick = range_shell[0]
        stress, _ = self.calc_stress_weight(shell_thick, rib_num)
        self.executionCounter += 1
        return stress - max_shear_strength

    def calc_stress_weight(self, shell_thick, rib_num):
        self.runner.project_name_prefix = PROJECT_NAME_PREFIX + '_{:05d}'.format(self.executionCounter)
        pro = self.runner.new_project_r_t(rib_num, shell_thick)
        pro = self.runner.run_project(pro, used_cpus=1)
        res = pro.resultsCalcu
        if USE_ABA:
            res = pro.resultsAba
        stress = res.stressMisesMax
        weight = pro.calc_wight()
        return stress, weight

    def write_newton_log(self, out_str):
        out_str = out_str.replace('[', '')
        out_str = out_str.replace(']', '')
        output_f = open(LOG_FILE_PATH, 'a')  # 'a' so we append the file
        output_f.write(out_str + '\n')
        output_f.close()

    def plot_it(self, file_path=None, plot_handle=None, marker='-'):
        if file_path == None:
            file_path = LOG_FILE_PATH
        data = np.genfromtxt(file_path, delimiter=',', skip_header=1)
        plot = plot_handle
        if plot_handle == None:
            plot = PlotHelper(['Rippenanzahl', 'Gewicht in kg'], fancy=True, pgf=False)
        plot.ax.plot(data[:, 2], data[:, 5], marker, color='dodgerblue')
        import matplotlib.ticker as ticker
        plot.ax.xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
        plot.ax.yaxis.label.set_color('dodgerblue')
        ax_shell = plot.ax.twinx()
        ax_shell.set_ylabel('Blechdicke in mm')
        ax_shell.yaxis.label.set_color('orange')
        ax_shell.plot(data[:, 2], data[:, 3] * 1000, marker, color='orange')
        ax_shell.set_ylim(tuple(1000 * x for x in range_shell))
        plot.ax.set_xlim((1, 30))
        plot.finalize(height=2, show_legend=False)
        #plot.save(Constants().PLOT_PATH + 'newtonOptiPlot.pdf')
        #plot.show()
        return plot


if __name__ == '__main__':
    nw = NewtonOpt()
    #nw.opti_it()
    #nw.plot_it()
    pl = nw.plot_it('../data_out/newtonOpti2018-10-19_15_57_47_all.csv', marker=':')
    pl = nw.plot_it('../data_out/newtonOpti2018-10-19_15_57_47.csv', plot_handle=pl)
    #pl.save(Constants().PLOT_PATH + 'newtonOptiPlot.pdf')
    pl.show()
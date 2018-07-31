__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

# ==============================================================================
# description     :main file for testing
# author          :Juri Bieler
# date            :2018-07-13
# notes           :
# python_version  :3.6
# ==============================================================================

import numpy as np
from datetime import datetime
from wingConstruction.utils.Constants import Constants
from wingConstruction.Project import Project
from utils.TimeTrack import TimeTrack

from multiprocessing import Pool
import time


def run_test(element_size):
    projectName = 'meshSize_{0:.5f}'.format(element_size)
    pro1 = Project(projectName)
    pro1.halfSpan = 17.
    pro1.boxDepth = 2.
    pro1.boxHeight = 1.
    pro1.nRibs = 18
    pro1.boxOverhang = 0.1
    pro1.forceTop = -0.3*(77000. * 9.81)
    pro1.forceBot = -0.2 * (77000. * 9.81)
    #pro1.elementSize = 0.25
    pro1.elementSize = element_size
    pro1.elemType = 'qu8'
    pro1.shellThickness = 0.0099
    pro1.generate_geometry(nonlinear=True)
    pro1.solve()
    print('############ DONE ############')
    if not pro1.errorFlag:
        #pro1.postprocess()
        #if not pro1.errorFlag:
        return True
    return False


def collect_results(element_size):
    projectName = 'meshSize_{0:.5f}'.format(element_size)
    pro1 = Project(projectName)
    pro1.postprocess(template='wing_post_simple')
    l = pro1.validate_load('loadTop.frc')
    l += pro1.validate_load('loadBut.frc')
    #l = pro1.validate_load('load.frc')
    loadError = (-0.5 * 77000. * 9.81) - l
    if not pro1.errorFlag:
        exportRow = str(element_size) + ','\
        +str(pro1.clx.dispD3Min) + ','\
        + str(pro1.clx.dispD3Max) + ','\
        + str(pro1.clx.stressMisesMin) + ','\
        + str(pro1.clx.stressMisesMax) + ','\
        + str(loadError)+'\n'
        return exportRow
    return ''


def main_run():
    sizes = np.arange(0.06, .26, 0.01)
    sizes = list(sizes)
    start = time.time()
    with Pool(4) as p:
        res = p.map(run_test, sizes)
    print("Time taken = {0:.5f}".format(time.time() - start))

    outputF = open(Constants().WORKING_DIR + '/'
                   + 'convAna_'
                   + datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
                   + '.csv',
                   'w')
    outputF.write('sizes,dispD3Min,dispD3Max,stressMisesMin,stressMisesMax,loadError\n')

    for s in sizes:
        outStr = collect_results(s)
        if outStr != '':
            outputF.write(outStr)
            outputF.flush()
    outputF.close()
    print("Time taken = {0:.5f}".format(time.time() - start))
    print('DONE with ALL')


if __name__ == '__main__':
    main_run()

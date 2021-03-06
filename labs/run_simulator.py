# -*- coding: utf-8 -*-
"""
    This file is part of FLOWSIM.

    FLOWSIM is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    FLOWSIM is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with FLOWSIM.  If not, see <https://www.gnu.org/licenses/>.

    Copyright (c) 2020 Bart Lamiroy
    e-mail: Bart.Lamiroy@univ-lorraine.fr
"""

"""
    This is mainly demo code showing how to invoke the FLOWSIM simulator with
    default parameters or with provided file of stored parameters
    python -m labs.run_simulator [options] from the server directory to run the simulator
"""

import numpy as np
import matplotlib.pyplot as plt
import csv
import os.path
import argparse
import datetime
from models.sir_h.simulator import run_sir_h
from .defaults import get_default_params, import_json
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="python run_simulator.py", description='Run MODSIR-19 simulator on provided '
                                                                                 'parameter sets.')
    parser.add_argument('-p', '--params', metavar='file', type=str, nargs='*',
                        help='pathname to parameter set (JSON)')

    data_choice_options = ['SE', 'INCUB', 'IR',
                           'IH', 'SM', 'SI', 'SS', 'R', 'DC']
    data_choice_options_input = ['input_' + s for s in data_choice_options]
    data_choice_options_output = ['output_' + s for s in data_choice_options]
    data_choice_options += data_choice_options_input
    data_choice_options += data_choice_options_output

    parser.add_argument('-o', metavar='curve', choices=data_choice_options, nargs='+', default=['SI'],
                        help=f'list of curve identifiers to output (in  {data_choice_options})')

    parser.add_argument('--noplot', action='store_true',
                        help="do not display obtained curves")
    parser.add_argument('-s', '--save', metavar='prefix', type=str, nargs='?',
                        help='filename prefix to output obtained curve points in .csv file format')
    parser.add_argument('--path', metavar='pathname', type=str, nargs=1,
                        help='to be used with -s, --save parameter. Saves output files to provided path')

    args = parser.parse_args()

    basename = None
    if args.path:
        outputdir = args.path[0] + '/'
    else:
        outputdir = "./outputs/"

    if 'save' in vars(args).keys():
        save_output = True
    else:
        save_output = False

    if save_output:
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)

        # timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S_")
        timestamp = ''

        if args.save:
            basename = ''.join([outputdir, timestamp, args.save])
        else:
            basename = ''.join([outputdir, timestamp, 'commando_covid_run'])

    ''' default parameters are stored in three distinct groups '''
    default_params = get_default_params()
    parameters = default_params['parameters']
    rules = default_params['rules']
    data = default_params['data']
    other = default_params['other']

    ''' the simulator takes parameters and rules and produces series of points '''
    series = run_sir_h(parameters, rules)

    ''' default parameters also contain reference data '''
    day0 = data['day0']
    data_chu = data['data_chu_rea']
    data_day0 = np.array([[date - day0, data_chu[date]] for date in data_chu])

    if args.o:
        curve_list = args.o
    else:
        curve_list = ['SI']

    if save_output:
        basename = '_'.join([basename, '+'.join(curve_list)])

    x = np.linspace(
        day0, day0 + parameters['lim_time'] - 1, parameters['lim_time'])

    if not args.noplot:
        for curve in curve_list:
            c = series[curve]
            plt.plot(x, c, label="Baseline " + curve)
        ''' @TODO allow for other reference data to be plotted '''
        plt.plot(data_day0[:, 0], data_day0[:, 1], 'x', label="Data CHU SI")

    if args.params:
        for f in args.params:
            parameters, rules, other = import_json(f)
            f_base = os.path.splitext(os.path.basename(f))[0]
            series = run_sir_h(parameters, rules)

            for curve in curve_list:
                c = series[curve]
                if not args.noplot:
                    min_size = min(len(x), len(c))
                    plt.plot(x[:min_size], c[:min_size],
                             label=curve + " " + f_base)
                if save_output:
                    with open(basename + "_" + f_base + ".csv", mode='w') as output_file:
                        output_writer = csv.writer(
                            output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                        '''  @TODO check if numbering starts from 1 or from 0 '''
                        for item in zip(range(len(c)), c):
                            output_writer.writerow(item)

    if not args.noplot:
        plt.legend(loc='upper right')
        plt.show()

    ''' examples for exporting/importing parameters
    export_json("mytest.json", parameters, rules, other)

    '''

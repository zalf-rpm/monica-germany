#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import os
import json
import csv
import copy
from collections import defaultdict
import sys
from glob import glob
#print sys.path

from multiprocessing import Process
import threading
from threading import Thread

rwp = __import__("run-work-producer")
rwc = __import__("run-grid-work-consumer")
gs = __import__("grids-scripts")


def delete_files_in_dir(dir_, pattern):
    for path in glob(dir_ + pattern):
        os.remove(path)


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)


def prod_cons_calib(setup, custom_crop, server, calib_id="no_calibration"):

    path_to_grids_output = str(setup["run-id"]) + "/" + str(calib_id) + "/"

    #clear directory first
    delete_files_in_dir(path_to_grids_output, "*.asc")

    producer = Process(target=rwp.run_producer, args=(setup, custom_crop, server["producer"]))
    consumer = Process(target=rwc.run_consumer, args=(path_to_grids_output, True, server["consumer"]))
    #producer = FuncThread(rwp.run_producer, setup, custom_crop)
    #consumer = FuncThread(rwc.run_consumer, path_to_grids_output, True)
    producer.daemon = True
    consumer.daemon = True
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()

    path_to_aggregated_output = path_to_grids_output + "aggregated/"
    if not os.path.exists(path_to_aggregated_output):
        os.makedirs(path_to_aggregated_output)

    #clear directory first
    delete_files_in_dir(path_to_aggregated_output, "*")

    year_to_lk_to_value = gs.aggregate_by_grid(path_to_grids_dir=path_to_grids_output,
                                               path_to_out_dir=path_to_aggregated_output,
                                               pattern="*_yield_*.asc")
    year_to_lk_to_value = gs.aggregate_by_grid(path_to_grids_dir=path_to_grids_output,
                                               path_to_out_dir=path_to_aggregated_output,
                                               pattern="*_yearly-sum-nleach_*.asc")
    year_to_lk_to_value = gs.aggregate_by_grid(path_to_grids_dir=path_to_grids_output,
                                               path_to_out_dir=path_to_aggregated_output,
                                               pattern="*_crop-sum-nleach_*.asc")
    year_to_lk_to_value = gs.aggregate_by_grid(path_to_grids_dir=path_to_grids_output,
                                               path_to_out_dir=path_to_aggregated_output,
                                               pattern="*_crop-sum-nfert_*.asc")

    return year_to_lk_to_value

# ======================================================================================================================
# Copyright 2022 Eduardo Valle.
#
# This file is part of Cook-a-Dream.
#
# Cook-a-Dream is free software: you can redistribute it and/or modify it under the terms of the version 3 of the GNU
# General Public License as published by the Free Software Foundation.
#
# Cook-a-Dream is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Cook-a-Dream. If not, see
# https://www.gnu.org/licenses.
# ======================================================================================================================
# pylint: disable=invalid-name
# This module uses TensorFlow (instead of Qt) naming conventions
import logging
import os
from pathlib import Path

import numpy as np
from tensorflow.python.keras.utils import data_utils
from keras.utils import data_utils as data_utils_k
from tensorflow.python.util.tf_export import keras_export

logger = logging.getLogger('deep_dream')

weights_path = Path(os.environ['COOKADREAM_MODEL_WEIGHTS_DIR'])

keras_get_file = data_utils.get_file
keras_get_file_k = data_utils_k.get_file

# Keras data_utils.get_file overlay to retrieve pre-download models
# def get_file(fname,
#              origin,
#              untar=False,
#              md5_hash=None,
#              file_hash=None,
#              cache_subdir='datasets',
#              hash_algorithm='auto',
#              extract=False,
#              archive_format='auto',
#              cache_dir=None):

@keras_export('keras.utils.get_file')
def get_file(fname, *args, **kwargs):
    fpath = weights_path / fname
    if fpath.exists():
        logger.debug('-- (TF) loading predownloaded file "%s"', fname)
        return str()
    else:
        logger.info('-- (TF) file "%s" was not predownloaded - falling back to keras', fname)
        return keras_get_file(fname, *args, **kwargs)

@keras_export('keras.utils.get_file')
def get_file_k(fname, *args, **kwargs):
    fpath = weights_path / fname
    if fpath.exists():
        logger.debug('-- (K) loading predownloaded file "%s"', fname)
        return str(weights_path / fname)
    else:
        logger.info('-- (K) file "%s" was not predownloaded - falling back to keras', fname)
        return keras_get_file_k(fname, *args, **kwargs)


data_utils.get_file = get_file
data_utils_k.get_file = get_file_k
logger.debug('-- data_utils.get_file patched')



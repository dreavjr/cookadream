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
import glob
import os
import tempfile
import sys
from pathlib import Path

logger = logging.getLogger('deep_dream')

weights_path = Path(os.environ['COOKADREAM_RESOURCES_DIR']) / 'weights'
libs_path = Path(os.environ['COOKADREAM_RESOURCES_DIR']) / 'libs'

if os.name == 'nt':
    # In Windows, tries to find cuda installation
    system_drive = os.environ['SystemDrive']
    cuda_path = glob.glob(f'{system_drive}\\Program Files*\\**\\CUDA\\v11.2\\bin')
    if cuda_path:
        # Found it! Adjusts system paths
        cuda_path_bin = cuda_path[0]
        cuda_path = Path(cuda_path[0]).parent
        cuda_path_cupti = str(cuda_path / 'extras' / 'CUPTI' / 'lib64')
        system_path = os.environ.get('PATH', '')
        system_paths = system_path.split(';') if system_path else []
        while cuda_path_cupti in system_paths:
            system_paths.remove(cuda_path_cupti)
        while cuda_path_bin in system_paths:
            system_paths.remove(cuda_path_bin)
        system_paths.insert(0,  str(libs_path)) # CUDNN path
        system_paths.insert(0,  cuda_path_cupti)
        system_paths.insert(0,  cuda_path_bin)
        system_path = ';'.join(system_paths)
        os.environ['PATH'] = system_path
        logger.debug('CUDA v11.2 found! system_path = %s', system_path)
    else:
        logger.debug('CUDA v11.2 not found!')

    # Autograd assumes the existence of the output streams in Tensorflow 2.8.0 [BUG?]
    if sys.stdout is None:
        sys.stdout = tempfile.TemporaryFile(mode='w', encoding='utf-8', errors='ignore')
    if sys.stderr is None:
        sys.stderr = tempfile.TemporaryFile(mode='w', encoding='utf-8', errors='ignore')

import numpy as np
from tensorflow.python.keras.utils import data_utils
from keras.utils import data_utils as data_utils_k
from tensorflow.python.util.tf_export import keras_export

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



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

import sys
from pathlib import Path

import pandas as pd
import scipy.io

# Application resources
applicationPath = Path(__file__).resolve(strict=True)
dataSourceDir = applicationPath.parent / 'originals' / 'data'
dataDir = applicationPath.parent / 'resources' / 'data'

metadataPath = dataSourceDir / 'ILSVRC2012_devkit_t12' / 'data' / 'meta.mat'
metadata = scipy.io.loadmat(metadataPath)
synsets = metadata['synsets']

rawPath = dataDir / 'imagenet_raw.csv'
sep = ' -> '
csvHeader = ('imagenet_id', 'wordnet_id', 'imagenet_name',)
wordnet_ids = []
with open(rawPath, mode='wt', encoding='utf-8') as rawFile:
    print(sep.join(csvHeader), file=rawFile)
    for k in range(len(synsets)):
        imagenet_id   = synsets[k][0][0][0][0]
        wordnet_id    = synsets[k][0][1][0]
        imagenet_name = synsets[k][0][2][0]
        print(imagenet_id, wordnet_id, imagenet_name, sep=sep, file=rawFile)
        if imagenet_id <= 1000:
            wordnet_ids.append((wordnet_id, imagenet_id, imagenet_name))

csvPath = dataDir / 'imagenet_untranslated.csv'
if not csvPath.exists():
    print('WARNING: selected/sorted imagenet_untranslated.csv file not found, falling back to raw file!',
          file=sys.stderr)
    csvPath = rawPath

wordnet_ids = sorted(wordnet_ids) # The ids in Keras follow the order of the sorted wordnet_ids
kerasPath = dataDir / 'keras_ordering.tab'
kerasHeader = ('keras_id', 'wordnet_id', 'imagenet_id', 'imagenet_name',)
translate_imagenet_to_keras_id = {}
with open(kerasPath, mode='wt', encoding='utf-8') as kerasFile:
    print(sep.join(kerasHeader), file=kerasFile)
    for keras_id,(wordnet_id, imagenet_id, imagenet_name) in enumerate(wordnet_ids):
        print(keras_id, wordnet_id, imagenet_id, imagenet_name, sep=sep, file=kerasFile)
        translate_imagenet_to_keras_id[imagenet_id] = keras_id

translate_imagenet_to_keras_id[0] = -1

xmlPath = dataDir / 'imagenet.xml'
imagenet_data = pd.read_csv(csvPath, sep=sep, index_col=False, engine='python')
imagenet_data['keras_id'] = imagenet_data['imagenet_id'].map(translate_imagenet_to_keras_id.__getitem__)
imagenet_data.to_xml(xmlPath, index=False, root_name='imagenet_classes', row_name='imagenet_class', parser='etree')

csvPath = dataDir / 'imagenet.tab'
imagenet_data.to_csv(csvPath, sep='\t', index=False)

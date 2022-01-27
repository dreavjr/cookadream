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
# pylint: disable=invalid-name, line-too-long

import base64
import json
# import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import tensorflow as tf


def add_model(root, name, module, description, default_layer, layers, data_dir):
    layers_n = len(layers)

    model = ET.SubElement(root, 'model')
    ET.SubElement(model, 'name').text = name
    ET.SubElement(model, 'module').text = module
    ET.SubElement(model, 'description').text = description
    ET.SubElement(model, 'default_layer').text = default_layer
    ET.SubElement(model, 'layers_n').text = str(layers_n)

    layer_info = [{'i':l[0],'n':l[1],'s':l[2]} for l in layers]
    all_info = dict(module=module, description=description, default_layer=default_layer, layers_n=layers_n,
                    layers=layer_info)
    all_info_json = json.dumps(all_info, ensure_ascii=False)
    all_info_encoded = base64.b64encode(all_info_json.encode()).decode('ascii')
    # all_info_encoded = '\n'.join(textwrap.wrap(all_info_encoded, width=80, break_long_words=True))
    ET.SubElement(model, 'all_info').text = all_info_encoded

    layers_element = ET.Element('layers')
    for layer_index,layer_name,layer_size in layers:
        layer = ET.SubElement(layers_element, 'layer')
        ET.SubElement(layer, 'layer_index').text = str(layer_index)
        ET.SubElement(layer, 'layer_name').text = str(layer_name)
        ET.SubElement(layer, 'layer_size').text = str(layer_size)
    xml_layers_doc = ET.ElementTree(layers_element)
    layersPath = data_dir / f'model_layers_{module.lower()}.xml'
    xml_layers_doc.write(layersPath, encoding='utf-8', xml_declaration=True)


def main():
    # Application resources
    applicationPath = Path(__file__).resolve(strict=True)
    data_dir = applicationPath.parent / 'resources' / 'data'

    root = ET.Element('models')

    deepest = largest = -1
    def get_shape(layer):
        nonlocal largest
        shape = layer.get_output_at(0).get_shape().as_list()[-1]
        largest = max(shape, largest)
        return shape

    base_model = tf.keras.applications.InceptionV3(include_top=True, weights='imagenet')
    # layers = [(i,l.name) for i,l in enumerate(base_model.layers) if l.trainable_weights and not 'batch_norm' in l.name]
    layers = [(i,l.name,get_shape(l)) for i,l in enumerate(base_model.layers) if l.name.startswith('mixed') or l.name=='predictions']
    deepest = max(deepest, len(layers))
    description = 'Created in 2015 by Christian Szegedy and colleagues, this was the model originally used for deep dreaming. It introduced the "inception module", a worldplay on the 2010 movie for its recursive structure.'
    add_model(root, 'Inception-v3', 'InceptionV3', description, default_layer='', layers=layers, data_dir=data_dir)

    base_model = tf.keras.applications.ResNet50(include_top=True, weights='imagenet')
    # layers = [(i,l.name) for i,l in enumerate(base_model.layers) if l.trainable_weights and not 'batch_norm' in l.name]
    layers = [(i,l.name,get_shape(l)) for i,l in enumerate(base_model.layers) if l.name.endswith('out') or l.name=='predictions']
    # layers = [(i,l.name,get_shape(l)) for i,l in enumerate(base_model.layers)]
    deepest = max(deepest, len(layers))
    description = 'Kaiming He and colleagues introduced Residual Networks in 2016, allowing models to achieve much higher depths. As of 2021, the ResNet family of networks still appears frequently in state-of-the-art investigations.'
    add_model(root, 'ResNet-50', 'ResNet50', description, default_layer='', layers=layers, data_dir=data_dir)

    base_model = tf.keras.applications.EfficientNetB0(include_top=True, weights='imagenet')
    # layers = [(i,l.name) for i,l in enumerate(base_model.layers) if l.trainable_weights and not 'batch_norm' in l.name]
    # could be 'project_bn', or '_drop' in the place of 'add'
    layers = [(i,l.name,get_shape(l)) for i,l in enumerate(base_model.layers) if l.name.endswith('add') or l.name in ('top_activation', 'predictions')]
    # layers = [(i,l.name,get_shape(l)) for i,l in enumerate(base_model.layers)]
    deepest = max(deepest, len(layers))
    description = 'Mingxing Tan and Quoc V. Le created the EfficientNet family in 2019, achieving cutting edge results for image classification while also improving computational efficiency. The "B0" model is the smallest and fastest in the family, but also the least accurate.'
    add_model(root, 'EfficientNet-B0', 'EfficientNetB0', description, default_layer='', layers=layers, data_dir=data_dir)

    base_model = tf.keras.applications.EfficientNetB4(include_top=True, weights='imagenet')
    # layers = [(i,l.name) for i,l in enumerate(base_model.layers) if l.trainable_weights and not 'batch_norm' in l.name]
    layers = [(i,l.name,get_shape(l)) for i,l in enumerate(base_model.layers) if l.name.endswith('add') or l.name in ('top_activation', 'predictions')]
    deepest = max(deepest, len(layers))
    description = 'Mingxing Tan and Quoc V. Le created the EfficientNet family in 2019, achieving cutting edge results for image classification while also improving computational efficienty. The "B4" model is intermediate in the family, balancing size/computational cost and accuracy.'
    add_model(root, 'EfficientNet-B4', 'EfficientNetB4', description, default_layer='', layers=layers, data_dir=data_dir)

    xml_doc = ET.ElementTree(root)
    modelsPath = data_dir / 'models.xml'
    xml_doc.write(modelsPath, encoding='utf-8', xml_declaration=True)

    print('\n\nATTENTION! Remember to set in Constants.qml')
    print('    // --- AI Models Limits')
    print('    readonly property int modelDeepest:', deepest)
    print('    readonly property int layerLargest:', largest)

main()

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
# import sys
from datetime import datetime

import numpy as np
import tensorflow as tf
import keras
# import tensorflow_model_optimization as tfmot

logger = logging.getLogger('deep_dream')

MIN_DIM = 128 # Minimum image size that will not cause problems with the convolution operations
MAX_DIM = 1024

STEPS_MIN = 10
STEPS_MAX = 20
STEPS_DEF = 40
STEP_SIZE_DEF = 0.025
SMOOTHING_DEF = -100
JITTER_DEF = 4
OCTAVE_SCALING_DEF = 1/3
OCTAVES_BLENDING_DEF = 0.2
TILE_SIZE_DEF = 512

TF_BOOL = tf.bool
TF_FLOAT = tf.float32
TF_INT = tf.int32
TF_TO_IMAGE_ARRAY_TYPE = tf.uint8

NP_FLOAT = np.float32
NP_IMAGE_TYPE = np.uint8

PROGRESS_INTERVAL = 5 # Progress feedback in seconds

DEEP_DREAM_ENGINE_DEVICES = [d.name for d in tf.config.list_logical_devices()]

PREPROCESS_CAFFE_MEAN = [103.939, 116.779, 123.68]

RELU_WARMUP_STEPS = 8
relu_warmup_steps_tf = None
global_relu_step = None
global_relu_step_increment = None


class DeepDream(tf.Module):

    '''Deep dream gradient ascent module.'''
    def __init__(self, model, input_range, lr_multiplier, layer_name, neuron_first, neuron_last):
        global relu_warmup_steps_tf, global_relu_step, global_relu_step_increment
        super().__init__()
        self.model = model
        self.input_range = input_range
        self.lr_multiplier = lr_multiplier
        # Assumes a single output layer
        self.layer_name = layer_name
        self.output_layer_size = model.output.shape[-1]
        self.output_layer_dtype = model.output.dtype
        self.neuron_first = neuron_first
        self.neuron_last = neuron_last
        self.loss_mask = self.range_hot(self.output_layer_size, neuron_first, neuron_last+1)
        self.mask_size = tf.constant(neuron_last - neuron_first + 1, dtype=self.output_layer_dtype)
        self.optimizer = None
        self.smoothing_factor = None
        self.crop_size = None
        self.jitter_pixels = None
        self.image_tf_var = None
        self.run_extra_args = []
        self.image_limits = None
        relu_warmup_steps_tf = tf.constant(RELU_WARMUP_STEPS, dtype=TF_INT)
        global_relu_step_increment = tf.constant(1, dtype=TF_INT)
        global_relu_step = tf.Variable(initial_value=0, trainable=False, dtype=TF_INT)

    def range_hot(self, size, start, end):
        '''Returns a 1D tensor of given size with zeros in the range [start; end) and zeros elsewhere.'''
        r = tf.range(1, size+1, dtype=self.output_layer_dtype)
        return tf.minimum(tf.maximum(r - start, 0)*tf.maximum((end+1)-r,0),1)

    @property
    def current_result(self):
        return self.image_tf_var

    def start_optimizer(self, image_tf, /, *, crop_size=None, step_size=STEP_SIZE_DEF, smoothing_factor=SMOOTHING_DEF,
                        jitter_pixels=JITTER_DEF):
        global global_relu_step
        logger.debug('-- start_optimizer(image_tf.shape=%s, crop_size=%s, step_size=%s, smoothing_factor=%s, '
                     'jitter_pixels=%s)', image_tf.shape, crop_size, step_size, smoothing_factor, jitter_pixels)
        # beta_1 = defaults to 0.9, beta_2 = defaults to 0.999, epsilon = defaults to 1e-7
        self.optimizer = tf.optimizers.Adam(learning_rate=step_size * self.lr_multiplier, beta_1=0.99, epsilon=1e-1)
        self.image_tf_var = tf.Variable(image_tf)
        self.crop_size = tf.constant(crop_size, dtype=TF_INT)
        self.smoothing_factor = tf.constant(smoothing_factor / (crop_size[0] * crop_size[1]), dtype=TF_FLOAT)
        self.jitter_pixels = tf.constant(jitter_pixels, dtype=TF_INT)
        self.run_extra_args = [self.jitter_pixels]
        global_relu_step.assign(0)

    def run_steps(self, steps_to_run):
        global global_relu_step, global_relu_step_increment
        for _ in range(steps_to_run):
            gradients = self.gradient_step(self.image_tf_var, self.smoothing_factor, self.crop_size,
                                           *self.run_extra_args)
            self.optimizer.apply_gradients([[gradients, self.image_tf_var]])
            self.image_tf_var.assign(tf.clip_by_value(self.image_tf_var, self.input_range[0], self.input_range[1]))
            global_relu_step.assign_add(global_relu_step_increment)

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None,None,3], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[3], dtype=TF_INT),
            tf.TensorSpec(shape=[], dtype=TF_INT),
            )
    )
    def gradient_step(self, image_tf, smoothing_factor, crop_size, jitter_pixels):
        logger.info('-- retracing tf.function gradient_step(image_tf.shape=%s, smoothing_factor=%s, crop_size=%s, '
                    'jitter_pixels=%s)', image_tf.shape, smoothing_factor, crop_size, jitter_pixels)
        with tf.GradientTape() as tape:
            tape.watch(image_tf)
            if jitter_pixels > 0:
                image_crop_tf = tf.image.random_crop(image_tf, size=crop_size)
            else:
                image_crop_tf = image_tf
            loss = self.dream_loss(image_crop_tf, smoothing_factor)
        # Calculates the gradient of the loss with respect to the pixels of the input image.
        gradients = tape.gradient(loss, image_tf)
        # Normalizes the gradients
        gradients /= tf.math.reduce_std(gradients) + 1e-8
        gradients = tf.clip_by_value(gradients, -3, 3)
        return gradients

    def dream_loss(self, image_tf, smoothing_factor):
        '''Forward pass on the image through the model to retrieve the activations.'''
        logger.info('-- retracing tf.function dream_loss(image_tf.shape=%s, smoothing_factor=%s)',
                    image_tf.shape, smoothing_factor)
        # Converts the image into a batch of size 1.
        image_batch = tf.expand_dims(image_tf, axis=0)
        layer_activations = self.model(image_batch)
        # unmasked_loss = self.raw_reduction(layer_activations)
        masked_activations = layer_activations * self.loss_mask
        dream_loss_raw = self.raw_reduction(masked_activations)
        dream_loss = dream_loss_raw / self.mask_size
        smooth_loss = tf.image.total_variation(image_tf)
        smooth_loss_weighted = smoothing_factor * smooth_loss
        final_loss = dream_loss + smooth_loss_weighted
        # if logger.isEnabledFor(logging.DEBUG):
        #     tf.print(dream_loss_raw, dream_loss, smooth_loss, smooth_loss_weighted, final_loss,
        #              output_stream=sys.stderr)
        final_loss = -final_loss # Important! We are maximizing, not minimizing the activations!
        return final_loss

    def raw_reduction(self, activations):
        logger.info('-- retracing tf.function raw_reduction(activations.shape=%s)', activations.shape)
        if self.layer_name == 'predictions' and self.neuron_first == self.neuron_last:
            return tf.reduce_sum(activations) # More appealing visually for single-neuron on prediction layer
        else:
            return tf.sqrt(tf.reduce_sum(tf.square(activations))) # More appealing visually for all other cases
        # Other possible reductions:
        # return tf.reduce_sum(tf.abs(activations))
        # return tf.reduce_sum(tf.square(activations))


class TiledDeepDream(DeepDream):
    '''Deep dream gradient ascent module.'''
    def __init__(self, model, input_range, lr_multiplier, layer_name, neuron_first, neuron_last):
        super().__init__(model, input_range, lr_multiplier, layer_name, neuron_first, neuron_last)
        if layer_name == 'predictions':
            assert model.input_shape[1] == model.input_shape[2]
            self.tile_size = model.input_shape[1]
        else:
            self.tile_size = TILE_SIZE_DEF
        self.remove_last_tile = None

    def start_optimizer(self, image_tf, /, *, crop_size=None, step_size=STEP_SIZE_DEF, smoothing_factor=SMOOTHING_DEF,
                        jitter_pixels=JITTER_DEF):
        super().start_optimizer(image_tf, crop_size=crop_size, step_size=step_size, smoothing_factor=smoothing_factor,
                                jitter_pixels=jitter_pixels)
        if jitter_pixels > 0:
            logger.warning('-- tiled - jitter_pixels = %s will be ignored!', jitter_pixels)
        else:
            logger.debug('-- tiled')
        self.smoothing_factor = tf.constant(smoothing_factor / (self.tile_size * self.tile_size), dtype=TF_FLOAT)
        self.remove_last_tile = tf.constant(np.array(crop_size) % self.tile_size, dtype=TF_BOOL)
        self.run_extra_args = [self.remove_last_tile]

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None,None,3], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[3], dtype=TF_INT),
            tf.TensorSpec(shape=[3], dtype=TF_BOOL),
            )
    )
    def gradient_step(self, image_tf, smoothing_factor, crop_size, remove_last_tile):
        logger.info('-- retracing tf.function tiled.gradient_step(image_tf.shape=%s, smoothing_factor=%s, crop_size=%s,'
                    ' remove_last_tile=%s', image_tf.shape, smoothing_factor, crop_size, remove_last_tile)
        # Rolls the image by a random amount to avoid "seam"
        shift, image_tf = self.random_roll(image_tf, self.tile_size)
        # Accumulates the gradient for each tile
        gradients = tf.zeros_like(image_tf)

        # Remove the last tile if it should not be processed
        ys = tf.range(0, crop_size[0], self.tile_size)
        if remove_last_tile[0]:
            ys = ys[:-1]
        xs = tf.range(0, crop_size[1], self.tile_size)
        if remove_last_tile[1]:
            xs = xs[:-1]
        for y in ys:
            for x in xs:
                with tf.GradientTape() as tape:
                    tape.watch(image_tf)
                    image_tile_tf = image_tf[y:y+self.tile_size, x:x+self.tile_size]
                    # image_tile_tf = tf.image.crop_to_bounding_box(image_tf, y, x, self.tile_size, self.tile_size)
                    loss = self.dream_loss(image_tile_tf, smoothing_factor)
                # Calculates the gradient of the loss with respect to the pixels of the input image.
                partial_gradient = tape.gradient(loss, image_tf)
                gradients += partial_gradient
        # Normalizes the gradients
        gradients /= tf.math.reduce_std(gradients) + 1e-8
        gradients = tf.clip_by_value(gradients, -3, 3)
        # Unrolls the gradient to the right place
        gradients = tf.roll(gradients, shift=-shift, axis=[0,1])
        return gradients

    @staticmethod
    def random_roll(image_tf, max_roll):
        logger.info('-- retracing tf.function random_roll(image_tf.shape=%s, max_roll=%s)', image_tf.shape, max_roll)
        # Randomly shift the image to avoid tiled boundaries.
        shift = tf.random.uniform(shape=[2], minval=-max_roll, maxval=max_roll, dtype=TF_INT)
        image_rolled_tf = tf.roll(image_tf, shift=shift, axis=[0,1])
        return shift, image_rolled_tf


class DeepDreamEngine():

    models = {
        'InceptionV3': {
            'model':         tf.keras.applications.InceptionV3,
            'preprocess':    tf.keras.applications.inception_v3.preprocess_input,
            'input_type':    'tf',
            'input_range' :  (-1., 1.),
            'lr_multiplier': 1.,
            'channels':      'RGB',
            'patch_relus':   keras.applications.inception_v3,
            },
        'ResNet50': {
            'model':         tf.keras.applications.ResNet50,
            'preprocess': tf.keras.applications.resnet.preprocess_input,
            'input_type':    'caffe',
            'input_range' :  (-176., 177.), # The range is not exact, this covers ~3 standard deviations from mean
            'lr_multiplier': 128.,
            'channels':      'BGR',
            'patch_relus':   'kwargs',
            },
        'EfficientNetB0' :  {
            'model':         tf.keras.applications.EfficientNetB0,
            'preprocess':    tf.keras.applications.efficientnet.preprocess_input,
            'input_type':    'raw',
            'input_range' :  (0, 255), # There is no actual preprocessing in efficientnet, the range is unchanged
            'lr_multiplier': 128.,
            'channels':      'RGB',
            'patch_relus':   None,
            },
        'EfficientNetB4' :  {
            'model':         tf.keras.applications.EfficientNetB4,
            'preprocess':    tf.keras.applications.efficientnet.preprocess_input,
            'input_type':    'raw',
            'input_range' :  (0, 255), # There is no actual preprocessing in efficientnet, the range is unchanged
            'lr_multiplier': 128.,
            'channels':      'RGB',
            'patch_relus':   None,
            },
    }

    def __init__(self):
        self.base_model = None
        self.preprocess = None
        self.input_type = None
        self.normalization_mean = None
        # self.layer_names = ['mixed3', 'mixed5']
        # self.layers = None
        self.layer_name = None
        self.layer = None
        self.deepdream_model = None
        self.deepdream = None
        self.device_name = None
        self.tiled_rendering = False

    def setup(self, device_name, model_name='InceptionV3', layer_name=None, neuron_first=None, neuron_last=None,
              tiled_rendering=False):
        logger.debug('>> loading ai model')
        self.device_name = device_name

        if model_name not in self.models:
            raise ValueError(f'unrecognized model module name "{model_name}"')

        self.tiled_rendering = layer_name == 'predictions' or tiled_rendering

        # Patches the ReLU activations
        patch_relus = self.models[model_name]['patch_relus']
        if patch_relus is None:
            relu_kwargs = {}
        elif patch_relus == 'kwargs':
            relu_kwargs = { 'layers' : CustomLayers() }
        else:
            # We have to monkey-patch a module to fix the relus
            relu_kwargs = {}
            # print(patch_relus)
            # print(patch_relus.layers)
            # setattr(patch_relus, 'layers',  CustomLayers())
            assert hasattr(patch_relus, 'layers')
            patch_relus.layers = CustomLayers()
            # print(patch_relus.layers)

        # Prepares the feature extraction model
        self.base_model = self.models[model_name]['model'](weights='imagenet', include_top=layer_name == 'predictions',
                                                           classifier_activation=None, **relu_kwargs)
        self.preprocess = self.models[model_name]['preprocess']
        self.input_type = self.models[model_name]['input_type']
        input_range = self.models[model_name]['input_range']
        lr_multiplier = self.models[model_name]['lr_multiplier']
        self.normalization_mean = tf.constant(PREPROCESS_CAFFE_MEAN, dtype=TF_FLOAT)

        # For multiple output layers:
        # self.layer_names = layer_names
        # self.layers = [self.base_model.get_layer(name).output for name in self.layer_names]
        # self.deepdream_model = tf.keras.Model(inputs=self.base_model.input, outputs=self.layers)

        self.layer_name = layer_name
        self.layer = self.base_model.get_layer(layer_name).output
        self.deepdream_model = tf.keras.Model(inputs=self.base_model.input, outputs=self.layer)

        # Create the feature extraction model
        if self.tiled_rendering:
            self.deepdream = TiledDeepDream(self.deepdream_model, input_range=input_range, lr_multiplier=lr_multiplier,
                                            layer_name=layer_name, neuron_first=neuron_first, neuron_last=neuron_last)
        else:
            self.deepdream = DeepDream(self.deepdream_model,  input_range=input_range, lr_multiplier=lr_multiplier,
                                       layer_name=layer_name, neuron_first=neuron_first, neuron_last=neuron_last)

        logger.debug('<< done!')

    def dream(self, image_pillow, /, *, progress_callback=None, signals=None, dream_kwargs=None):
        logger.debug('>> dreaming with ai model')
        image_array = np.asarray(image_pillow)
        dream_kwargs = dream_kwargs or {}
        kwargs = dict(octaves=range(-2, 3), octaves_scaling=2.**(1./OCTAVE_SCALING_DEF), steps_per_octave=STEPS_DEF,
                      octaves_blending=OCTAVES_BLENDING_DEF, step_size=STEP_SIZE_DEF, smoothing_factor=SMOOTHING_DEF,
                      jitter_pixels=JITTER_DEF)
        dream_kwargs_extra = set(dream_kwargs.keys()) - set(kwargs.keys())
        if dream_kwargs_extra:
            raise TypeError(f'unexpected arguments in drwam_kwargs: {dream_kwargs_extra}')
        kwargs.update(dream_kwargs)
        if progress_callback:
            progress_callback(0., image_array=image_array)
        with tf.device(self.device_name):
            image_tf = image_result = None
            for image_tf, progress in self.main_loop(image_array, **kwargs):
                if progress_callback:
                    image_result = self.image_tf_to_image_array(image_tf)
                    progress_callback(progress, image_array=image_result)
                if signals and signals.isStopped:
                    return None
        if progress_callback:
            progress_callback(1.)
        logger.debug('<< dream complete!')
        if image_result is None and image_tf is not None:
            image_result = self.image_tf_to_image_array(image_tf)
        if image_result is None:
            return image_array
        return image_result

    def main_loop(self, input_image_array, /, *, octaves, octaves_scaling, steps_per_octave, octaves_blending,
                  step_size, smoothing_factor, jitter_pixels):
        '''runs the specified number of octaves and the number of steps withing each octave, yielding periodically'''
        octave_image_array = self.preprocess(input_image_array)
        octave_image_tf = original_image_tf = tf.convert_to_tensor(octave_image_array)
        steps_per_octave = self.round_steps(steps_per_octave)
        octaves_n = len(octaves)
        steps_total = octaves_n * steps_per_octave
        base_shape = tf.shape(octave_image_tf)[:-1]
        float_base_shape = tf.cast(base_shape, TF_FLOAT)
        dream_start = progress_time = datetime.now()
        progress_last = step_global = -1
        logger.debug('base_shape = %s, octaves = %s, steps_per_octave = %s, octaves_blending = %s, step_size = %s, '
                     'smoothing_factor = %s, jitter_pixels = %s, dream_start = %s',
                     base_shape, octaves, steps_per_octave, octaves_blending, step_size, smoothing_factor,
                     jitter_pixels, dream_start.isoformat())
        firstOctave = True
        for octave_i,octave in enumerate(octaves):
            new_shape = tf.cast(float_base_shape*(octaves_scaling**octave), TF_INT)
            octave_image_tf = tf.image.resize(octave_image_tf, new_shape)
            if octaves_blending>0. and not firstOctave:
                original_resized_tf = tf.image.resize(original_image_tf, new_shape)
                octave_image_tf = (1.-octaves_blending)*octave_image_tf + octaves_blending*original_resized_tf
            else:
                firstOctave = False
            loop_image_tf = octave_image_tf
            if self.tiled_rendering:
                jitter_pixels = 0
                octave_image_tf, padding, crop_size = self.pad_image(octave_image_tf, min_dim=self.deepdream.tile_size,
                                                                     jitter_pixels=0)
            else:
                octave_image_tf, padding, crop_size = self.pad_image(octave_image_tf, jitter_pixels=jitter_pixels)
            logger.debug('octaves_scaling = %s, octave = %s, exp = %s, new_shape = %s, octave_image_tf.shape = %s, '
                         'padding = %s, crop_size = %s, steps = %s',
                         octaves_scaling, octave, octaves_scaling**octave, new_shape, octave_image_tf.shape,
                         padding, crop_size, steps_per_octave)
            # logger.debug('dream_loss_raw, dream_loss, smooth_loss, smooth_loss_weighted, final_loss')
            for loop_image_tf, step in self.octave_loop(octave_image_tf, steps=steps_per_octave, step_size=step_size,
                    smoothing_factor=smoothing_factor, crop_size=crop_size, jitter_pixels=jitter_pixels):
                dream_now = datetime.now()
                step_global = octave_i * steps_per_octave + step
                logger.debug('step_global = %s, step = %s, dream_now = %s', step_global, step, dream_now.isoformat())
                if (dream_now-progress_time).total_seconds() > PROGRESS_INTERVAL:
                    progress_time = dream_now
                    progress_last = step_global
                    progress = step_global / steps_total
                    image_result = self.unpad_image(loop_image_tf, padding=padding)
                    image_result = tf.image.resize(image_result, base_shape)
                    yield image_result, progress
            octave_image_tf = self.unpad_image(loop_image_tf, padding=padding)
        if progress_last != step_global:
            image_result = octave_image_tf
            image_result = tf.image.resize(image_result, base_shape)
            yield image_result, 1.

    def octave_loop(self, image_tf, /, *, steps, step_size, smoothing_factor, crop_size, jitter_pixels):
        step = 0
        self.deepdream.start_optimizer(image_tf, crop_size=crop_size, step_size=step_size,
                                       smoothing_factor=smoothing_factor, jitter_pixels=jitter_pixels)
        while step < steps:
            steps_to_run = min(STEPS_MAX, steps-step)
            step += steps_to_run
            self.deepdream.run_steps(steps_to_run)
            image_result = self.deepdream.current_result
            yield image_result, step

    @staticmethod
    def round_steps(steps):
        '''rounds up the number of steps in groups of STEP_MIN'''
        return ((steps + STEPS_MIN - 1) // STEPS_MIN) * STEPS_MIN

    def image_tf_to_image_array(self, image_tf):
        '''Converts a normalized float image_tf to a uint8 pixel image_array.'''
        if self.input_type == 'tf':
            image_tf = (255.*(image_tf + 1.0))/2.0
        elif self.input_type == 'caffe':
            image_tf += self.normalization_mean
            image_tf = image_tf[..., ::-1] # BGR -> RGB
            image_tf = tf.clip_by_value(image_tf, 0, 255)
        elif self.input_type == 'raw':
            pass
        else:
            assert False, f'unrecognized self.input_type = "{self.input_type}"'
        return tf.cast(image_tf, TF_TO_IMAGE_ARRAY_TYPE).numpy()

    @staticmethod
    def fit_image(image_pillow, /, min_dim=MIN_DIM, max_dim=MAX_DIM):
        '''Fits an image between minimum and maximum sizes, cropping only if needed.'''
        w, h = image_pillow.size
        dims = [[w, 0], [h, 1]]
        d_min = min(dims)
        d_max = dims[1-d_min[1]]
        if d_min[0] >= min_dim and d_max[0] <= max_dim:
            return image_pillow
        if d_min[0] == 0:
            raise ValueError('image is empty!')
        if d_max[0] > max_dim:
            d_min[0] = int(np.round(max_dim / d_max[0] * d_min[0]))
            d_max[0] = max_dim
        if d_min[0] < min_dim:
            d_max[0] = int(np.round(min_dim / d_min[0] * d_max[0]))
            d_min[0] = min_dim
        # Resizes image...
        # ... Gets the (w, h) tuple in the right order
        size_tuple = (d_min[0], d_max[0],) if d_min[1] == 0 else \
                     (d_max[0], d_min[0],)
        image_pillow = image_pillow.resize(size_tuple)
        if d_max[0] > max_dim:
            # Could not fit the image simply by resizing --- will have to crop
            crop_1 = (d_max[0] - max_dim) // 2
            crop_2 = crop_1+max_dim
            crop_box = (0, crop_1, w, crop_2,) if d_min[1] == 0 else \
                       (crop_1, 0, crop_2, h,)
            image_pillow = image_pillow.crop(crop_box)
        return image_pillow

    @classmethod
    def pad_image(cls, image_tf, /, *, min_dim=MIN_DIM, jitter_pixels=0):
        '''Adds padding such that image dimensions are at least min_dim+2*jitter_pixels.'''
        # On Tensorflow 2.7.0 padding is complicated due to 'reflect' and 'symmetric' being restricted to size of the
        # image. One solution would be to resize the input image, but here I decided to use a double padding, with
        # the maximum size allowed by 'reflect' and then an arbitrary padding with a constant padding
        h, w, c = image_tf.shape.as_list()
        max_reflect_padding = np.array(( (h//2, (h+1)//2), (w//2, (w+1)//2), (0, 0), ))
        # Gets the padding to apply except for the jitter padding
        w_pad = max(0, min_dim - w)
        h_pad = max(0, min_dim - h)
        padding = np.array(( (h_pad//2, (h_pad+1)//2), (w_pad//2, (w_pad+1)//2), (0, 0), ))
        # Gets the jitter and the full padding
        jitter_padding = np.array(( (jitter_pixels, jitter_pixels), (jitter_pixels, jitter_pixels), (0, 0), ))
        full_padding = padding + jitter_padding
        # Splits the full padding into reflect and constant padding and applies them
        reflect_padding = np.minimum(full_padding, max_reflect_padding)
        constant_padding = full_padding-reflect_padding
        if np.sum(constant_padding) > 0:
            # [TF2.7] This is needed because constant_value in tf.pad must be a scalar
            constant_value_r = tf.math.reduce_mean(image_tf[...,0], axis=(0, 1))
            constant_value_g = tf.math.reduce_mean(image_tf[...,1], axis=(0, 1))
            constant_value_b = tf.math.reduce_mean(image_tf[...,2], axis=(0, 1))
        else:
            constant_padding = None
        padded = image_tf
        if np.sum(reflect_padding) > 0:
            padded = tf.pad(padded, reflect_padding, mode='reflect')
        if constant_padding is not None:
            padded_r = tf.pad( padded[...,0:1], constant_padding, mode='constant', constant_values=constant_value_r )
            padded_g = tf.pad( padded[...,1:2], constant_padding, mode='constant', constant_values=constant_value_g )
            padded_b = tf.pad( padded[...,2:3], constant_padding, mode='constant', constant_values=constant_value_b )
            padded = tf.concat((padded_r, padded_g, padded_b,), axis=-1)
        # Computes the crop size corresponding to the image with the padding, but not the jitter padding
        crop_size = (h+h_pad, w+w_pad, c)
        return padded, full_padding, crop_size

    @staticmethod
    def unpad_image(image_array, /, *, padding):
        '''
        Removes padding to recover original image region. The usual sequence of operations will be:
        padded_image, padding, crop_size = pad_image(original_image, ...)
        # ... intermediate operations
        cropped_image = crop_somehow(padded_image, crop_size, ...)
        # ...
        unpadded_image = unpad_image(padded_image, padding=padding)
        '''
        if np.sum(padding) > 0:
            h, w, c = image_array.shape
            slices = tuple((slice(start, size-end) for size,(start,end) in zip((h,w,c),padding)))
            return image_array[slices]
        else:
            return image_array

    @classmethod
    def get_noise_array(cls, width, height, channels=3, *, scale=0.01, decay=1.):
        """An image paramaterization using 2D Fourier coefficients."""
        # Creates starting complex spectrum from Gaussian distribution
        fft_frequencies = cls.compute_fft_frequencies_2d(width, height)
        image_shape = (2, channels,) + fft_frequencies.shape # Real/Imaginary, Channels, Height, Width
        image_unscaled_spectrum = np.random.normal(size=image_shape, scale=scale)
        image_unscaled_spectrum = image_unscaled_spectrum[0] + 1j*image_unscaled_spectrum[1]
        # ...the IFT at this point would produce the so called "white" noise, with a flat power spectrum
        # Scales the spectrum with the inverse of the frequencies creating a "pinkish" noise
        scale  = 1.0 / np.maximum(fft_frequencies, 1.0 / max(width, height)) ** decay
        # This makes the spectrum size-invariant and is equivalent to NumPy's norm='ortho'
        # scale /= np.sqrt(width * height)
        image_scaled_spectrum = image_unscaled_spectrum * scale
        # Applies inverse transform to obtain scaled image in the space domain
        image_pixels = np.fft.irfft2(image_scaled_spectrum, norm='ortho')
        image_pixels = np.transpose(image_pixels, axes=(1,2,0))
        image_pixels = image_pixels[:height, :width, :channels]
        return image_pixels

    @staticmethod
    def compute_fft_frequencies_2d(width, height):
        '''Computes 2D spectrum frequencies'''
        # When we have an odd width we need to add one frequency and later cut it off
        width += width % 2
        # On the n-dimensional real fft/inverse-fft only the innermost dimension uses the rfft, all the others use the
        # complex fft, so np.irfft2 expects those frequencies:
        fx = np.fft.rfftfreq(width)
        fy = np.fft.fftfreq(height)
        fy = fy[:, None] # Transposes into column vector
        fft_frequencies = np.sqrt(fx*fx + fy*fy)
        return fft_frequencies

    @staticmethod
    def noise_to_image_array(noise_array):
        return (255. * (noise_array + 1.) / 2.).astype(NP_IMAGE_TYPE)

# Replace ReLU layers with custom layer that allows negative gradients being backpropagated
# This is based in Lucid's procedure:
# https://github.com/tensorflow/lucid/blob/master/lucid/optvis/overrides/redirected_relu_grad.py

class CustomLayers:
    def __getattr__(self, name):
        if name == 'Activation':
            return CustomReluActivation
        else:
            return getattr(tf.keras.layers, name)

# https://github.com/keras-team/keras/blob/948df87f1669e203e16e39daeaca52e2ea3253ad/keras/layers/core/activation.py#L24
class CustomReluActivation(tf.keras.layers.Activation):
    def __init__(self, activation, **kwargs):
        super().__init__(activation, **kwargs)
        if activation == 'relu':
            logger.debug('plugged new patched transparent_relu in place of native relu')
            self.activation = transparent_relu

# ReLU layer with custom gradient that backpropagates the negative gradient
@tf.custom_gradient
def transparent_relu(inputs, alpha=0., max_value=None, threshold=0.):
    assert alpha==0. and threshold==0. and max_value is None, 'advanced parameters for transparent_relu not implemented'
    outputs = tf.nn.relu(inputs)
    def grad(grad_upstream):
        global global_relu_step, relu_warmup_steps_tf
        # This is the "vanilla" relu gradient
        relu_grad = tf.where(inputs < 0., tf.zeros_like(grad_upstream), grad_upstream)
        # In this version we will allow negative gradients to pass through in the negative region (because gradient
        # descent_ will push the values towards zero)
        negative_pushing_lower = tf.logical_and(inputs < 0., grad_upstream > 0.)
        transparent_relu_grad = tf.where(negative_pushing_lower, tf.zeros_like(grad_upstream), grad_upstream)
        return tf.where(global_relu_step < relu_warmup_steps_tf, transparent_relu_grad, relu_grad)
    return outputs, grad

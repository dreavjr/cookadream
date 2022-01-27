
# TODO : Work on making other models accessible

# def replace_relus(model):
#     tfmot.quantization.keras.graph_transformations.model_transformer.ModelTransformer(model, transforms, candidate_layers=None, layer_metadata=None)

# TODO : Work on color decorrelation and FFT conditioning

IMAGENET_DECORRELATED_DEF = True
FREQUENCIES_CONDITIONED_DEF = True


# IMAGENET_COLOR_MEAN   = [0.485 * 255, 0.456 * 255, 0.406 * 255]
# IMAGENET_COLOR_STDDEV = [0.229 * 255, 0.224 * 255, 0.225 * 255]

IMAGENET_COLOR_CORRELATION_SQRT = np.asarray([[0.26,  0.09,  0.02],
                                              [0.27,  0.00, -0.05],
                                              [0.27, -0.09,  0.03]]).astype(NP_FLOAT)
IMAGENET_COLOR_CORRELATION_SQRT_MAX_NORM = np.max(np.linalg.norm(IMAGENET_COLOR_CORRELATION_SQRT, axis=0))
IMAGENET_COLOR_CORRELATION_SQRT_NORMALIZED = IMAGENET_COLOR_CORRELATION_SQRT/IMAGENET_COLOR_CORRELATION_SQRT_MAX_NORM

class DeepDream(tf.Module):
    def __init__(self, model, layer_name, neuron_first, neuron_last):
        self.frequencies_conditioned = None
        self.color_decorrelate_matrix = tf.constant(IMAGENET_COLOR_CORRELATION_SQRT_NORMALIZED.T, dtype=TF_FLOAT)

        self.imagenet_decorrelated = imagenet_decorrelated
        self.frequencies_conditioned = frequencies_conditioned

    def start_optimizer(self, image_tf, /, *, crop_size=None, step_size=STEP_SIZE_DEF, smoothing_factor=SMOOTHING_DEF,
                        jitter_pixels=JITTER_DEF, imagenet_decorrelated=IMAGENET_DECORRELATED_DEF,
                        frequencies_conditioned=FREQUENCIES_CONDITIONED_DEF):
        self.imagenet_decorrelated = imagenet_decorrelated
        self.frequencies_conditioned = frequencies_conditioned

    def run_steps(self, steps_to_run):
        for _ in range(steps_to_run):
            gradient_input_tf = self.image_tf_var
            # TODO: this naïve implementation is not correct =>
            # For frequency conditioning I must store the FFT representation as the latent variable and apply the
            # gradients (after irfft2 etc...) to that latent representation
            # For color correction, the color function must appear in the graph so it is taken into considearation by
            # the gradient computation
            # For the tiled computation:
            # (1) there is a beautiful shift theorem of the FFT that could be used to calculate the shifts on the latent representation!
            # (2) maybe the windowed FFT?
            if self.frequencies_conditioned:
                gradient_input_tf = self.condition_frequencies(gradient_input_tf)
            if self.imagenet_decorrelated:
                gradient_input_tf = self.condition_frequencies(gradient_input_tf)
            gradients = self.gradient_step(gradient_input_tf, self.smoothing_factor, self.crop_size,
                                           *self.run_extra_args)
            self.optimizer.apply_gradients([[gradients, self.image_tf_var]])
            self.image_tf_var.assign(tf.clip_by_value(self.image_tf_var, -1, 1))
    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None, 3], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[3], dtype=TF_INT),
            tf.TensorSpec(shape=[], dtype=TF_BOOL),
            tf.TensorSpec(shape=[], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[], dtype=TF_FLOAT),
            )
    )
    @classmethod
    def condition_frequencies(cls, image_tf, crop_size, spectral_input=False, scale=0.01, decay=1.):
        """An image paramaterization using 2D Fourier coefficients."""
        logger.info('-- retracing tf.function condition_frequencies(image_tf.shape=%s, crop_size=%s, spectral_input=%s,'
                    ' scale=%s, decay=%s)', image_tf.shape, crop_size, spectral_input, scale, decay)
        width, height, channels = crop_size
        fft_frequencies = cls.compute_fft_frequencies_2d(width, height)
        if spectral_input:
            image_unscaled_spectrum = image_tf # NOTE: spectral input is assumed to be already in C, H, W format
        else:
            image_unscaled_spectrum = tf.transpose(image_tf, (2, 0, 1)) # H, W, C => C, H, W
            image_unscaled_spectrum = tf.signal.rfft2d()
        # ...the IFT at this point would produce the so called "white" noise, with a flat power spectrum
        # Scales the spectrum with the inverse of the frequencies
        scale  = 1.0 / np.maximum(fft_frequencies, 1.0 / max(width, height)) ** decay
        # Assuming that Tensorflow fft routines have norm='backward' (the documentation is not clear) to make them
        # equivalent to NumPy's norm='ortho', we have to compensate, remultiplying the square root of the norm. This
        # is exactly what is done in Tensorflow Lucid:
        # https://github.com/tensorflow/lucid/blob/6dcc927e4ff4e7ef4d9c54d27b0352849dadd1bb/lucid/optvis/param/spatial.py#L77
        scale *= np.sqrt(width * height)
        image_scaled_spectrum = image_unscaled_spectrum * scale
        # Applies inverse transform to obtain scaled image in the space domain
        image_pixels = tf.signal.irfft2d(image_scaled_spectrum)
        image_pixels = np.transpose(image_pixels, axes=(1,2,0))
        image_pixels = image_pixels[:height, :width, :channels]
        # TODO: this "magical" normalization was present in TensorFlow Lucid. Is it needed? (Check if source => rfft2d => irfft2d => source without it)
        # image_pixels = image_pixels / 4.0
        return image_pixels

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[], dtype=TF_INT),
            tf.TensorSpec(shape=[], dtype=TF_INT)
        )
    )

    @staticmethod
    def compute_fft_frequencies_2d(width, height):
        '''Computes 2D spectrum frequencies'''
        logger.info('-- retracing tf.function compute_fft_frequencies_2d(width=%s, height=%s)', width, height)
        # When we have an odd width we need to add one frequency and later cut it off
        width += width % 2
        # On the n-dimensional real fft/inverse-fft only the innermost dimension uses the rfft, all the others use the
        # complex fft, so np.irfft2 expects those frequencies:
        # fx = np.fft.rfftfreq(width)
        fx = tf.range(0, width//2 + 1, dtype=TF_FLOAT) / width
        # fy = np.fft.fftfreq(height)
        fy = tf.concat((tf.range(0,            (height-1)//2 + 1, dtype=TF_FLOAT),
                        tf.range(-(height//2), 0,                 dtype=TF_FLOAT)), axis=0) / height
        fy = tf.expand_dims(fy, axis=1) # Transposes into column vector
        fft_frequencies = tf.math.sqrt(fx*fx + fy*fy)
        return fft_frequencies

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None, 3], dtype=TF_FLOAT),
            tf.TensorSpec(shape=[], dtype=TF_BOOL)
        )
    )
    def decorrelate_colors(self, image_tf, sigmoid=True):
        '''Convert input image_tf (standardized RGB in [-1, 1] interval) into 3 decorrelated color coordinates (using
        ImageNet correlation statistics).'''
        flat_tf = tf.reshape(image_tf, [-1, 3])
        flat_tf = tf.matmul(flat_tf, self.color_decorrelate_matrix)
        image_tf = tf.reshape(flat_tf, tf.shape(image_tf))
        if sigmoid:
            return tf.math.tanh(image_tf)
        else:
            return tf.clip_by_value(image_tf, -1, 1)

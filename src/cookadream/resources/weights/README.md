For the packaged binaries, the model weights should be in this directory prior to calling `briefcase build`.

The easiest way to do it is by choosing each of the 8 different models in the Preferences windows (each of the 4 networks x [last layer, any another layer]) and then copying the files from the Keras cache directory (in `~/.keras/models`). In Tensorflow 2.7.0 and 2.8.0, the expected files are:

- efficientnetb0.h5
- efficientnetb0_notop.h5
- efficientnetb4.h5
- efficientnetb4_notop.h5
- inception_v3_weights_tf_dim_ordering_tf_kernels.h5
- inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5
- resnet50_weights_tf_dim_ordering_tf_kernels.h5
- resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5

<img src="README.png" alt="Cook-a-Dream Header" style="width: 100%;"/>

Cook-a-Dream wraps an interactive, user-friendly interface around [deep dreaming](https://ai.googleblog.com/2015/06/inceptionism-going-deeper-into-neural.html). It aims to unleash the creative and [pedagogic](https://distill.pub/2017/feature-visualization/) potentials of deep dreaming for non-technical users.

Deep Dreaming uses Artificial Intelligence to create or modify images. It optimizes images to “superexcite” certain parts of an artificial neural network specialized in recognizing categories of objects. The process compares to dreaming, or maybe to visual hallucinations in humans.

**The results of deep dreaming are unpredictable** and may at times be beautiful or repulsive, inspiring or disturbing, humorous or offensive.

Cook-a-Dream is distributed in the hope that it will be useful, but **without any warranty**; without even the implied warranty of **merchantability** or **fitness for a particular purpose**.

Cook-a-Dream is free software: you can redistribute it and/or modify it under the terms of the version 3 of the GNU General Public License as published by the Free Software Foundation. See the [GNU General Public License](COPYING) for more details.

For acknowledgments and third-party licenses, check the file [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md)

# 1. Simplified Installation (Experimental)

I am currently trying to find out how to make Cook-a-Dream installation hassle-free for non-technical users. Unfortunately, that is *much* harder to do in Python than I expected.

For the moment, simplified installation is only available for Window 10+ and for macOS on Intel machines. On other Operating Systems or on macOS on Apple Sillicon, installation from sources is required (read below).

You may download the [installation packages here](https://github.com/dreavjr/cookadream/releases/tag/v0.2.0).

The installation packages were created with [Briefcase](https://beeware.org/project/projects/tools/briefcase/).


# 2. Installation from Sources

## 2.1. General Installation Procedures

1. Check that you have Python 3.8 or 3.9 installed. Cook-a-Dream requires Python version at least 3.8, and TensorFlow (the AI Engine used for deep dreaming) is compatible with versions 3.7–3.9

2. Install [TensorFlow](https://www.tensorflow.org/install/). Special requirements may apply for using hardware acceleration (e.g., CUDA on GPUs). Cook-a-Dream was developed and tested with version 2.7.0 of TensorFlow on Windows and Linux, and version 2.8.0 on macOS.

3. Install Cook-a-Dream other two dependencies: [PySide6 / Qt for Python 6](https://wiki.qt.io/Qt_for_Python) and [Pillow](https://pillow.readthedocs.io/en/stable/). Cook-a-Dream was developed and tested with version 6.2.2 of Qt for Python and version 8.4 of Pillow

4. Download Cook-a-Dream source code

## 2.2. Advice for Specific Systems

### 2.2.1. Windows without hardware acceleration or with CUDA

TensorFlow is officially supported on Windows 7 or Later.

1. Check that you have Python 3.8 or 3.9 installed. Ensure that your Python is 64-bit. **Warning:** Apparently, installing Python from the Microsoft Store leads to a [cryptic PySide6 bug being unable to load its DLLs](https://bugreports.qt.io/browse/PYSIDE-1245). We tested the system with the Windows Installer of Python 3.9.10 (64-bit) [downloaded from Python.org](https://www.python.org/downloads/windows/). We used the default installation options (which included pip), except for adding Python to PATH, which was not checked by default

1. Install [TensorFlow](https://www.tensorflow.org/install/). For hardware acceleration on an NVIDIA GPU, ensure that you have installed and configured CUDA. Read carefully [TensorFlow setup instructions for GPU](https://www.tensorflow.org/install/gpu), and the [CUDA installation guide for Windows](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/). Acceleration on AMD GPUs for Tensorflow 2 is currently not available. Indicative instructions below are for TensorFlow **without** special regard for acceleration:

	- Install the Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017, and 2019.
		- Go to the [Microsoft Visual C++ downloads](https://support.microsoft.com/help/2977003/the-latest-supported-visual-c-downloads)
		Scroll down the page to the “Visual Studio 2015, 2017 and 2019” section.
		- Download and install the *Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017 and 2019* for your platform (probably X86 if you have a run-of-the-mill desktop or laptop).
	- Make sure [to enable long paths on Windows](https://superuser.com/questions/1119883/windows-10-enable-ntfs-long-paths-policy-option-missing)
	- Upgrade pip and create a virtual environment to install TensorFlow. Type the following commands on a `cmd` shell:
      ```
      python -m pip install --upgrade pip
      python -m pip install --upgrade virtualenv
      python -m virtualenv cookenv
      ```

	- Activate the virtual environment

		```cookenv\Scripts\activate.bat```

	- Install TensorFlow

		```python -m pip install tensorflow==2.7.0```

1. Install the other dependencies

	```python -m pip install PySide6==6.2.2 Pillow==8.4```

1. Download Cook-a-Dream source code

1. Run Cook-a-Dream. (Remember to activate the virtual environment — see above — every time)

	```
    cd src/
    python -m cookadream
    ```

### 2.2.1. Linux without hardware acceleration or with CUDA

TensorFlow is officially supported on Ubuntu 16.04 or later, but users report successful installation in other distros.

1. Check that you have Python 3.8 or 3.9 installed. Otherwise, use the package manager of your system (e.g., apt on Ubuntu) to install it

1. For hardware acceleration, ensure that you have installed and configured CUDA. Read carefully [TensorFlow setup instructions for GPU](https://www.tensorflow.org/install/gpu). Cook-a-Dream was developed and tested with TensorFlow 2.7.0

1. Install Cook-a-Dream other dependencies PySide6 and Pillow:

	```python -m pip install PySide6==6.2.2 Pillow==8.4```

1. Download Cook-a-Dream source code

1. Run Cook-a-Dream

	```
    cd src/
    python -m cookadream
    ```

We tested Cook-a-Dream on an Ubuntu 20.04.3 server with acceleration with NVIDIA TITAN Xp GPUs. In our tests, we ran Cook-a-Dream remotely, using [X11 forwarding](https://en.wikipedia.org/wiki/X_Window_System#Remote_desktop). The solutions to the challenges we found to run Qt in that environment are collected in the [x11.environ](x11.environ) file.


### 2.2.2. macOS
1. Check that you have Python 3.8 or 3.9 installed. Usually, macOS ships with Python 2, which is too outdated for Cook-a-Dream and TensorFlow. There are several ways to install additional Python versions into a macOS system, the one we tested was [installing Homebrew](https://brew.sh/) and using it, which is as simple as typing the following command on a Terminal shell:

	```brew install python@3.8```

1. For using hardware acceleration, you need to install the [TensorFlow-Metal plugin](https://developer.apple.com/metal/tensorflow-plugin/). Follow the link and read the instructions carefully, for they are different depending on whether you are using an AMD GPU on Intel or an Accelerated arm64 on Apple Silicon. We developed and tested Cook-a-Dream on an iMac with an AMD Radeon Pro GPU. Indicative instructions for that hardware are below:

	- Upgrade pip and create a virtual environment to install TensorFlow. (**Warning**: Apple recommends virtual environments for TensorFlow-Metal only on Intel CPU/AMD GPU. For M1 / Apple Silicon, they recommend conda). Type the following commands on a Terminal shell:
      ```
      python -m pip install --upgrade pip
      python -m pip install --upgrade virtualenv
      python -m virtualenv cookenv
      ```

	- Activate the virtual environment

		```source cookenv/bin/activate```

	- Install TensorFlow-macOS

		```python -m pip install tensorflow-macos==2.8.0```

	- Install TensorFlow-Metal (for installation **without** hardware acceleration, you may follow the same steps except for this one)

		```python -m pip install tensorflow-metal==0.3```

1. Install Cook-a-Dream other dependencies PySide6 and Pillow:

	```python -m pip install PySide6==6.2.2 Pillow==8.4```

1. Download Cook-a-Dream source code

1. Run Cook-a-Dream. (Remember to activate the virtual environment — see above — every time)

	```
    cd src/
    python -m cookadream
    ```

**Known issues:** If you intend to use hardware acceleration, ensure that you install version 2.8.0 of tensorflow-macos, because version 2.7.0 [has a memory alignment check issue](https://github.com/tensorflow/tensorflow/issues/49202) that prevents tiled rendering (which is required for rendering with the last layer of the networks) from working.

### Other hardware acceleration options

As of 2022-01, [ROCm support on TensorFlow is incipient](https://github.com/ROCmSoftwarePlatform/tensorflow-upstream), and, in particular, not available for Windows.

Microsoft has created [their own port of TensorFlow for DirectX](https://github.com/microsoft/tensorflow-directml), but it is only compatible with TensorFlow 1.

Apple does not support acceleration with Intel or NVIDIA GPUs.

## 2.3. Downloading and running the source

With the dependencies installed, one option is to clone this repository on the installation location. Type the following commands on a shell:

```
git clone https://github.com/dreavjr/cookadream.git
cd cookadream/src
python -m cookadream
```

If you don't have `git` installed, you may download the [source from a release](https://github.com/dreavjr/cookadream/releases), and unzip / untar it on the location, using the graphical interface, or one of the sequences below in the command-line:

```
unzip cookadream-0.2.0.zip
cd cookadream-0.2.0/src
python -m cookadream
```

or

```
tar xvzf cookadream-0.2.0.tar.gz
cd cookadream-0.2.0/src
python -m cookadream
```

# 2. Running Cook-a-Dream

To run Cook-a-Dream, run the module `cookadream` on the command line:

```
cd src/
python -m cookadream
```

Cook-a-Dream usage intends to be intuitive. Basic usage is straightforward: just drag and drop an image to the main window, paste an image with the usual Paste shortcut key sequence for the system (normally ctrl+V or cmd+V), or open an image using the menu File->Open... Advanced options are accessible using the Preferences menu.

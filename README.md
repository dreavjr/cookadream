<img src="README.png" alt="Cook-a-Dream Header" style="width: 100%;"/>

Cook-a-Dream wraps an interactive, user-friendly interface around [deep dreaming](https://ai.googleblog.com/2015/06/inceptionism-going-deeper-into-neural.html). It aims to unleash the creative and [pedagogical](https://distill.pub/2017/feature-visualization/) potentials of deep dreaming for non-technical users.

Deep Dreaming uses Artificial Intelligence to create or modify images. It optimizes images to “superexcite” certain parts of an artificial neural network specialized in recognizing categories of objects. The process compares to dreaming, or maybe to visual hallucinations in humans.

**The results of deep dreaming are unpredictable** and may at times be beautiful or repulsive, inspiring or disturbing, humorous or offensive.

Cook-a-Dream is distributed in the hope that it will be useful, but **without any warranty**; without even the implied warranty of **merchantability** or **fitness for a particular purpose**.

Cook-a-Dream is free software: you can redistribute it and/or modify it under the terms of the version 3 of the GNU General Public License as published by the Free Software Foundation. See the [GNU General Public License](COPYING) for more details.

For acknowledgments and third-party licenses, check the file [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md)

# 1. Installation

I am currently trying to find out how to make Cook-a-Dream installation hassle-free for non-technical users. Unfortunately, that is *much* harder to do in Python than I expected.

For the moment, Cook-a-Dream is only available as this source repository, requiring the command-line to launch and to install its requirements. Saying that this is less than ideal is a big understatement.

## 1.1. General Installation Procedures

1. Check that you have Python 3.8 or 3.9 installed. Cook-a-dream requires Python version at least 3.8, and TensorFlow (the AI Engine used for deep dreaming) is compatible with versions 3.7–3.9.

2. Install [TensorFlow](https://www.tensorflow.org/install/). Special requirements may apply for using hardware acceleration (e.g., CUDA on GPUs).

3. Install Cook-a-Dream other two dependencies: [PySide6 / Qt for Python 6](https://wiki.qt.io/Qt_for_Python) and [Pillow](https://pillow.readthedocs.io/en/stable/)

4. Download Cook-a-Dream source code


## 1.2. Advice for Specific Systems

### 1.2.1. Windows without hardware acceleration or with CUDA

Tensorflow is officially supported on Windows 7 or Later.

1. Check that you have Python 3.8 or 3.9 installed. Ensure that your Python is 64-bit. **Warning:** Apparently, installing Python from the Microsoft Store leads to a [cryptic PySide6 bug being unable to load its DLLs](https://bugreports.qt.io/browse/PYSIDE-1245). We tested the system with the Windows Installer of Python 3.9.10 (64-bit) [downloaded from Python.org](https://www.python.org/downloads/windows/). We used the default installation options (which included pip), except for adding Python to PATH, which was not checked by default.

1. Install [TensorFlow](https://www.tensorflow.org/install/). For hardware acceleration on an NVIDIA GPU, ensure that you have installed and configured CUDA. Read carefully [TensorFlow setup instructions for GPU](https://www.tensorflow.org/install/gpu), and the [CUDA installation guide for Windows](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/). Acceleration on AMD GPUs for Tensorflow 2 is currently not available. Indicative instructions below are for Tensorflow **without** special regard for acceleration:

	- Install the Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017, and 2019.
		- Go to the [Microsoft Visual C++ downloads](https://support.microsoft.com/help/2977003/the-latest-supported-visual-c-downloads)
		Scroll down the page to the “Visual Studio 2015, 2017 and 2019” section.
		- Download and install the *Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017 and 2019* for your platform (probably X86 if you have a run-of-the-mill desktop or laptop).
	- Make sure [to enable long paths on Windows](https://superuser.com/questions/1119883/windows-10-enable-ntfs-long-paths-policy-option-missing)
	- Upgrade pip and create a virtual environment to install TensorFlow. Type the following commands on a ```cmd``` shell:
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

1. Run Cook-a-Dream. (Remember to activate the virtual environment — see above — every time).

	```python cookadream\Cookadream.py```

### 1.2.1. Linux without hardware acceleration or with CUDA

Tensorflow is officially supported on Ubuntu 16.04 or later, but users report successful installation in other distros.

1. Check that you have Python 3.8 or 3.9 installed. Otherwise, use the package manager of your system (e.g., apt on Ubuntu) to install it

1. For hardware acceleration, ensure that you have installed and configured CUDA. Read carefully [TensorFlow setup instructions for GPU](https://www.tensorflow.org/install/gpu). Cook-a-Dream was developed and tested with Tensorflow 2.7.0

1. Install Cook-a-Dream other dependencies PySide6 and Pillow:

	```python -m pip install PySide6==6.2.2 Pillow==8.4```

1. Download Cook-a-Dream source code

1. Run Cook-a-Dream

	```python cookadream/Cookadream.py```

We tested Cook-a-Dream on an Ubuntu 20.04.3 server with acceleration with NVIDIA TITAN Xp GPUs. In our tests, we ran Cook-a-Dream remotely, using [X11 forwarding](https://en.wikipedia.org/wiki/X_Window_System#Remote_desktop). The solutions to the challenges we found to run Qt in that environment are collected in the [x11.environ] file.


### 1.2.2. macOS
1. Check that you have Python 3.8 or 3.9 installed. Usually, macOS ships with Python 2, which is too outdated for Cook-a-Dream and TensorFlow. There are several ways to install additional Python versions into a macOS system, the one we tested was [installing Homebrew](https://brew.sh/) and using it, which is as simple as typing the following command on a Terminal shell:

	```brew install python@3.8```

1. For using hardware acceleration, you need to install the [Tensorflow-Metal plugin](https://developer.apple.com/metal/tensorflow-plugin/). Follow the link and read the instructions carefully, for they are different depending on whether you are using an AMD GPU on Intel or an Accelerated arm64 on Apple Silicon. We developed and tested Cook-a-Dream on an iMac with an AMD Radeon Pro GPU. Indicative instructions for that hardware are below:

	- Upgrade pip and create a virtual environment to install TensorFlow. (**Warning**: Apple recommends virtual environments for Tensorflow-Metal only on Intel CPU/AMD GPU. For M1 / Apple Silicon, they recommend conda). Type the following commands on a Terminal shell:
      ```
      python -m pip install --upgrade pip
      python -m pip install --upgrade virtualenv
      python -m virtualenv cookenv
      ```

	- Activate the virtual environment

		```source cookenv/bin/activate```

	- Install TensorFlow-macOS

		```python -m pip install tensorflow-macos==2.7.0```

	- Install TensorFlow-Metal (for installation **without** hardware acceleration, you may follow the same steps except for this one)

		```python -m pip install tensorflow-metal==0.3```

1. Install Cook-a-Dream other dependencies PySide6 and Pillow:

	```python -m pip install PySide6==6.2.2 Pillow==8.4```

1. Download Cook-a-Dream source code

1. Run Cook-a-Dream. (Remember to activate the virtual environment — see above — every time).

	```python cookadream/Cookadream.py```

### Other hardware acceleration options

As of 2022-01, [ROCm support on TensorFlow is incipient](https://github.com/ROCmSoftwarePlatform/tensorflow-upstream), and, in particular, not available for Windows.

Microsoft has created [their own port of Tensorflow for DirectX](https://github.com/microsoft/tensorflow-directml), but it is only compatible with TensorFlow 1.

Apple does not support acceleration with  Intel or NVIDIA GPUs.

## 1.2. Source installation

With the dependencies installed, clone this repository on the installation location:

```git clone https://github.com/dreavjr/cookadream.git```

# 2. Running Cook-a-Dream

To run Cook-a-Dream, execute the main script ```Cookadream.py```on the command line:

```python Cookadream.py```

Cook-a-Dream usage intends to be intuitive. Basic usage is straightforward: just drag and drop an image to the main window, paste an image with the usual Paste shortcut key sequence for the system (normally ctrl+V or cmd+V), or open an image using the menu File->Open... Advanced options are accessible using the Preferences menu.

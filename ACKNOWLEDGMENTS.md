# Main inpiration sources

## Deep Dreaming or "Inceptionism" is the original research work of:
"Inceptionism: Going Deeper into Neural Networks" \
Alexander Mordvintsev, Christopher Olah, and Mike Tyka. Google AI Blog, 2015-06-17. \
https://ai.googleblog.com/2015/06/inceptionism-going-deeper-into-neural.html

## Cook-a-Dream is based on TensorFlow tutorials:
https://www.tensorflow.org/tutorials/generative/deepdream \
https://www.tensorflow.org/tutorials/generative/style_transfer

> Apache License\
> Version 2.0, January 2004\
> http://www.apache.org/licenses

## The noisy image generator and the ReLU warmup procedure are based on:
https://github.com/TensorFlow/lucid

> Apache License\
> Version 2.0, January 2004\
> http://www.apache.org/licenses/

## In the course of developing this program, the author consulted the companion article of Lucid several times:
"Feature Visualization: How neural networks build up their understanding of images" \
Chris Olah, Alexander Mordvintsev, Ludwig Schubert. 2017-11-07. DOI: 10.23915/distill.00007 \
https://distill.pub/2017/feature-visualization/

Feature visualization is the earnest sibling to light-hearted deep dreaming, but the implementation techniques are surprisingly similar.

## In the course of developing this program, the author found the following tutorial helpful:

"Deep Dream with TensorFlow: A Practical guide to build your first Deep Dream Experience" \
Naveen Manwani. Hackernoon, 2018-12-27. \
https://hackernoon.com/deep-dream-with-tensorflow-a-practical-guide-to-build-your-first-deep-dream-experience-f91df601f479

The idea of blending the octaves with the original image was based on this example.

# Main software components

## The GUI of Cook-a-Dream is implemented with Qt 6.2.2

https://www.qt.io/

> Qt 6.2.2 is licensed under the GNU Lesser General Public License (LGPL) version 3. Other licenses are available.

Several modules of Qt use components subjected to their own licenses. Cook-a-Dream usage of Qt includes modules Qt For Python, QtCore, QtGui, QtQml, QtQuick, QtQuickControls, and QtWidgets, which may contain third party modules under permissive licenses. See Qt licensing, and each module licensing for further details.

https://doc.qt.io/qt-6/licensing.html \
https://doc.qt.io/qtforpython-6/licenses.html \
https://doc.qt.io/qt-6/qtcore-index.html \
https://doc.qt.io/qt-6/qtgui-index.html \
https://doc.qt.io/qt-6/qtquick-index.html \
https://doc.qt.io/qt-6/qtquickcontrols-index.html \
https://doc.qt.io/qt-6/qtwidgets-index.html

## The AI logic of Cook-a-Dream is implemented in TensorFlow

https://www.tensorflow.org/

> Apache License\
> Version 2.0, January 2004\
> http://www.apache.org/licenses/

## Cook-a-Dream is packaged for distribution with Briefcase

https://beeware.org/briefcase/

> Copyright (c) 2015 Russell Keith-Magee.\
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
>
> * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
> * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
> * Neither the name of Briefcase nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Other software components

## NumPy

https://numpy.org/

> NumPy License\
> https://numpy.org/doc/stable/license.html
>
> Copyright (c) 2005-2022, NumPy Developers.\
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
>
> * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
> * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
> * Neither the name of the NumPy Developers nor the names of any contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Pillow

https://python-pillow.org/

> HPND License\
> https://github.com/python-pillow/Pillow/blob/main/LICENSE
>
> Like PIL, Pillow is licensed under the open source HPND License:
>
> By obtaining, using, and/or copying this software and/or its associated documentation, you agree that you have read, understood, and will comply with the following terms and conditions:
>
> Permission to use, copy, modify, and distribute this software and its associated documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of Secret Labs AB or the author not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

## Python

https://www.python.org/

> Python software and documentation are licensed under the PSF License Agreement.\
> https://docs.python.org/3/license.html

## MenuFit.qml

The auto-sizing code for QML native menus is adapted from [this blog post by Martin Hoeher](https://martin.rpdev.net/2018/03/13/qt-quick-controls-2-automatically-set-the-width-of-menus.html), who has kindly released his solution to public domain.

# Other components

## Roboto Typeface

https://fonts.google.com/specimen/Roboto

> Apache License
> Version 2.0, January 2004
> http://www.apache.org/licenses/

## Example image labrador.jpg

From "Yellow Labrador Looking", Wikimedia Commons. CC-BY-SA-3.0. \
Photo taken by User:Elf, October 2004 in Turlock, California at the Nunes Agility Field. \
https://commons.wikimedia.org/wiki/File:YellowLabradorLooking_new.jpg

## The other images are Copyright Eduardo Valle

artichoke.jpg, Copyright Eduardo Valle, 2020 \
broken.*, Copyright Eduardo Valle, 2022 \
cacti.jpg, Copyright Eduardo Valle, 2020 \
cake.jpg, Copyright Eduardo Valle, 2021 \
chicken-okra.jpg, Copyright Eduardo Valle, 2019. "Mate Couro" is a registered trademark of Mate Couro S.A. \
garden.jpg, Copyright Eduardo Valle, 2020 \
green-apples.jpg, Copyright Eduardo Valle, 2019 \
grocer.jpg, Copyright Eduardo Valle, 2020 \
pitangas.jpg, Copyright Eduardo Valle, 2018 \
placeholder.*, Copyright Eduardo Valle, 2022

> The images are licensed under the terms of the version 3 of the GNU General Public License that applies to the software as a whole. Alternatively, each image listed in this subsection may be individually licensed under a Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0): https://creativecommons.org/licenses/by-sa/4.0/

## Application icon and splash screen

The application icon and splash screen are based on the image "Artichoke by Jean Bernard (1775-1883)", Wikimedia Commons. CC-BY-SA-4.0. \
Original from the Rijksmuseum Amsterdam. \
https://commons.wikimedia.org/wiki/File:Illustration_by_Jean_Bernard,_digitally_enhanced_by_rawpixel-com_292.jpg

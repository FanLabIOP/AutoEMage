# AutoEMage
AutoEMage is a software that automates file transfer, motion correction, CTF estimation, image display, outlier
detection, particle picking and 2D class averaging. Through specific settings, file transfer, data preprocessing
and monitoring can be done simultaneously with data acquisition. During this process, AutoEMage does not
require manual intervention or surveillance, which lives up to its name. Once outliers are detected, it will
send emails to users so that they can come back in time and have a check. Moreover, it provides users with a
graphical user interface, in order that they can not only see real-time pre-processed micrographs, but also some
results of data processing such as 2D classes.
## System Requirements and Installation
AutoEMage is developed using Python3 and Perl on Linux, including a few programs such as MotionCor2,
CTFFIND4 and some programs of RELION and IMOD, while its graphical user interface is based on PyQt6.
Therefore, these programming languages and cryo-EM programs should be installed before using AutoEMage,
which can be downloaded through the following links:
+ PyQt6: https://pypi.org/project/PyQt6/ Note that PyQt6 may be successfully installed by inputting
`python3 -m pip install PyQt6` on the command line.
+ Python3: https://www.python.org/
+ Perl: https://www.perl.org/
+ MotionCor2: https://hpc.nih.gov/apps/MotionCor2.html
+ CTFFIND4: https://grigoriefflab.umassmed.edu/ctffind4
+ RELION: https://relion.readthedocs.io/en/latest/Installation.html
+ IMOD: https://bio3d.colorado.edu/imod/download.html

Warning: MotionCor2 supports cuda of different versions, but RELION does not support cuda 12.1.

In addition, some libraries such as PyQt6-WebEngine, matplotlib and mrcfile need manual installation. After
successful installation, directories of MotionCor2, CTFFIND4 and AutoEMage can be added to environment
variables in this way: add the following lines to the .bashrc file:
```
#add MotionCor2 path
export PATH=MotionCor2 directory:$PATH
#add CTFFIND 4 path
export PATH=CTFFIND directory:$PATH
#add AutoEMage path
export PATH=AutoEMage directory:$PATH
```
## Usage
Details can be found in the [manual](autoemage_2023/manual_english.pdf).
## Contact Information
Emails: ipcas_oasis@163.com; chengyuanhao@iphy.ac.cn

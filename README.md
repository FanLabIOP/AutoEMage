# AutoEMage
AutoEMage is a software that automates file transfer, motion correction, CTF estimation, image display, outlier detection, particle picking, 2D classification, class ranking and 3D model generation. Through specific settings, file transfer, data preprocessing and monitoring can be done simultaneously with data acquisition. During this process, AutoEMage does not require manual intervention or surveillance, which lives up to its name. Once outliers are detected, it will send emails to users so that they can come back in time and have a check. Moreover, it provides users with a graphical user interface, in order that they can not only see real-time pre-processed micrographs, but also some
results of data processing.
## System Requirements and Installation
AutoEMage is developed using Python3 and Perl on Linux, including a few programs such as MotionCor2,
CTFFIND4, UCSF ChimeraX and some programs of RELION and IMOD, while its graphical user interface is based on PyQt6.
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
+ UCSF ChimeraX: https://www.cgl.ucsf.edu/chimerax/

Warning: MotionCor2 supports cuda of different versions, but RELION does not support cuda 12.1.

In addition, AutoEMage can be installed within a virtual environment created using `virtualenv`. Some libraries such as PyQt6-WebEngine, matplotlib and mrcfile need manual installation. To install the aforementioned libraries, users can enter the following command in the terminal: `python3 -m pip install PyQt6-WebEngine matplotlib mrcfile tifffile scipy scikit-image`. After successful installation, directories of MotionCor2, CTFFIND4 and AutoEMage can be added to environment variables in this way: add the following lines to the .bashrc file:
```
#add MotionCor2 path
PATH=$PATH:/work/Softwares/MotionCor2_1.6.4_Mar31_2023
#add CTFFIND 4 path
PATH=$PATH:/work/Softwares/ctffind-4.1.14-linux64/bin
#add AutoEMage path
PATH=$PATH:/work/Softwares/autoemage_2023
# add IMOD
export IMOD_DIR=/usr/local/imod_4.11.24
if [ -e $IMOD_DIR/IMOD-linux.sh ] ; then source $IMOD_DIR/IMOD-linux.sh ; fi
# Setup |RELION| if not already done so
if [ "" == "`echo $PATH | grep /work/Documents/relion/build/bin\`" ]; then
  PATH=$PATH:/work/Documents/relion/build/bin
fi
if [ "" != "`echo $LD_LIBRARY_PATH`" ]; then
  if [ "" == "`echo $LD_LIBRARY_PATH | grep /work/Documents/relion/build/lib`" ]; then
     LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/Documents/relion/build/lib
fi
else
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/Documents/relion/build/lib
fi
```
## Usage
Details can be found in the [manual](autoemage_2023/manual_english.pdf).
## Contact Information
Emails: ipcas_oasis@163.com; chengyuanhao@iphy.ac.cn
## Licensing
AutoEMage is available free of charge for non-profit academic use. Commercial/for-profit licensing inquiries can be sent to dingwei@iphy.ac.cn.

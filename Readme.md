# pypyueye

Convenience wrapper around [pyueye](https://pypi.python.org/pypi/pyueye) API for IDS cameras.

It allows to easily display a live video, save an image or record a video.
It has also been made easy to plug the live video through [opencv](https://opencv.org/) for live image analysis.
Pypyueye allows to easily display live videos, save images or record videos usin IDS cameras.
It is also easy to plug the live video through [opencv](https://opencv.org/) for live image analysis.

# Windows
## Installation on Anaconda

Download these files to an easily accessible location.

**Please create a new environment before installing these packages**

After creating the environment, left-click on the _Play_ button and select _Open with Terminal_, and type after going in the directory where these files have been downloaded. Type:

```Python
python setup.py install
```
The dependencies (`matlplotlib`, `opencv`, `spyder`) may require separate installation in the same environment. To do so, go to environments and search for these packages in the _Not installed_ drop down menu.

Pyueye may also require a separate install. Install pyueye by:


```Python
sudo apt-get update
sudo apt-get upgrade
```

```Python
pip install opencv-python
sudo apt-get install python-dev python-setuptools 
```

import setuptools
setuptools.setup(name='Tracking',
version='0.1',
description='Package with tracking objects and algos',
url='www.github.com/totosan/halloweenai',
author='Thomas Tomow',
install_requires=['opencv-contrib-python==4.5.3.56'],
author_email='toto_san@live.com',
package_data={'Tracking': ['dnn/face_detector/*']},
packages=setuptools.find_packages(),
zip_safe=False)
from setuptools import find_packages, setup

package_name = 'midge'

setup(
    name=package_name,
    version='2.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='davidebassan',
    maintainer_email='d.bassan@hotmail.it',
    description='Midge Explorer robot node',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'midge = midge.midge_node:main',
        ],
    },
)

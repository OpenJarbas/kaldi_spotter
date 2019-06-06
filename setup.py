from setuptools import setup

setup(
    name='kaldi_spotter',
    version='0.1.2',
    packages=['kaldi_spotter'],
    url='https://github.com/JarbasAl/kaldi_spotter',
    install_requires=["pyee==5.0.0", "numpy", "cython", "py-nltools"],
    license='apache2.0',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='wake word spotting with kaldi'
)

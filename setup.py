from setuptools import setup

setup(
    name="SynthethicHealthPopulation",
    version="0.1",
    author='Maciej Tarsa',
    author_email='maciej.tarsa@gmail.com',
    py_modules=["generator"],
    install_requires=[
        "Click",
        "Pandas",
        "TQDM",
    ],
    entry_points='''
        [console_scripts] 
            generate_patients=generator.__main__:main
    ''',  

)

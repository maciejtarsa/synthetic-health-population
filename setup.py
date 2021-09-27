from setuptools import setup

setup(
    name="SynthethicHealthPopulation",
    version="0.1",
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
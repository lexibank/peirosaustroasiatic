from setuptools import setup


setup(
    name='cldfbench_peirosaustroasiatic',
    py_modules=['cldfbench_peirosaustroasiatic'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'peirosaustroasiatic=cldfbench_peirosaustroasiatic:Dataset',
        ]
    },
    install_requires=[
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)

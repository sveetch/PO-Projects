from setuptools import setup, find_packages

setup(
    name='PO-Projects',
    version=__import__('po_projects').__version__,
    description=__import__('po_projects').__doc__,
    long_description=open('README.rst').read(),
    author='David Thenon',
    author_email='dthenon@emencia.com',
    url='http://pypi.python.org/pypi/PO-Projects',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Babel==1.3',
        'django-braces==1.0.0',
        'South==0.7.6',
        'autobreadcrumbs==0.9.0',
        'djangocodemirror==0.9.3',
        'django-crispy-forms >= 1.3.2',
    ],
    include_package_data=True,
    zip_safe=False
)
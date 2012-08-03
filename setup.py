from distutils.core import setup

setup(name='codene',
    version='1.0.0',
    description='Codene CDN server', 
    author='Colin Alston', 
    author_email='colin.alston@praekeltfoundation.org', 
    url='http://github.com/praekelt/codene',
    

    packages = ['codene', 'twisted.plugins'], 
    package_data={
        'twisted': ['twisted/plugins/*.py'], 
    },
)

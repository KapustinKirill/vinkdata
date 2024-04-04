from setuptools import setup, find_packages

setup(
    name='vinkdata',
    version='0.2.1',
    author='Капустин Кирилл',
    author_email='k.kapustin@vink.ru',
    description='Набор инструментов для трансформации данных, включая работу с базами данных, файлами и XML.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kapustinkirill/vink_data_transform',
    packages=find_packages(),
    install_requires=[
        # Зависимости проекта, например:
        'psycopg2-binary',
        'lxml',
        # Другие зависимости
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)

from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:
    
    requirements_lst:list[str] = []
    try:
        with open('requirements.txt') as file_obj:
            requirements = file_obj.readlines()
            for line in requirements:
                requirements=line.strip()
                if requirements and requirements != '-e .':
                    requirements_lst.append(requirements)
    except FileNotFoundError:
        print('requirements.txt not found')
    return requirements_lst


setup(
    name= "networksecurity",
    version= "0.0.1",
    author= "Yashwanth K",
    author_email="yahswanth0098@gmail.com",
    packages= find_packages(),
    install_requires = get_requirements()
    
)



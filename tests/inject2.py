from typing import NewType

from injector import inject, Injector


Name = NewType('Name', str)
Description = NewType('Description', str)

class X:
    @inject
    def __init__(self, name: Name, desc: Description):
        self.name = name
        self.desc = desc

def configure(binder):
    binder.bind(Name, to='miguel')
    binder.bind(Description, to='persona feliz')


injector = Injector(configure)
x = injector.get(X)
print(x.name)

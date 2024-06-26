from abc import ABC, ABCMeta, abstractmethod


class IWarningLogger(ABC):
    """ Interfaz simple para presentar excepciones al usuario. """
    
    @abstractmethod
    def display(self, title: str, body: str) -> None:
        pass

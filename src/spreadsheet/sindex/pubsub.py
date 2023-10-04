from abc import abstractmethod, ABC

from src.spreadsheet.sindex.domain import Sindex


class SindexSubscriber(ABC):
    @abstractmethod
    def follow_sindexes(self, pubs: set[Sindex]):
        raise NotImplemented

    @abstractmethod
    def on_sindex_deleted(self, pub: Sindex):
        raise NotImplemented


class SindexPublisher(Sindex, SindexSubscriber):
    def follow_sindexes(self, pubs: set[Sindex]):
        self._on_followed(pubs)

    def on_sindex_deleted(self, pub: Sindex):
        raise NotImplemented

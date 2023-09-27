import pytest

from src.node.repository import GraphRepoFake


def repo():
    return GraphRepoFake()



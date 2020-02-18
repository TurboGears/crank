import pytest
from crank.dispatcher import *

class TestDispatcher:

    def setup(self):
        self.dispatcher = Dispatcher()

    def test_create(self):
        pass

    def test_dispatch(self):
        with pytest.raises(NotImplementedError):
            self.dispatcher._dispatch(1,2)


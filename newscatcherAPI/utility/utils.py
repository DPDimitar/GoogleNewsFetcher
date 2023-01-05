class RotatingProxies():
    def __init__(self, proxies: list):
        self._list = proxies

    def _rotate(self):
        self._list = self._list[-1:] + self._list[:1]

    def get(self) -> str:
        self._rotate()
        return self._list[0]

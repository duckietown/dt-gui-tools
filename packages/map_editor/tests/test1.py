class A:
    def pr(self):
        print('A')

def get_a():
    print('get a')
    return A

class B:
    _a = None
    def __init__(self, a: A=None):
        self._a = a or get_a()
    def prb(self):
        self._a.pr()

if __name__ == '__main__':
    b = B()
    b.prb()

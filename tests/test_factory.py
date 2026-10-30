from stickman.factory import make_demo

def test_entrypoint():
    assert callable(make_demo)

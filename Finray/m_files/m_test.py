import matlab
import matlab.engine


def test_matlab():
    engine = matlab.engine.start_matlab()
    Finray1 = engine.plot_test()
    print(Finray1)
    print('finish')

test_matlab()
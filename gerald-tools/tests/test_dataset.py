import pytest as pytest
import gerald_tools


@pytest.fixture
def gerald_path():
    return r"C:\Users\Philipp\sciebo\10_IFS_der_RWTH_Aachen\40_Masterarbeit\04_Inhalt\datasets\GERALD\dataset"


def test_load_gerald(gerald_path):
    gerald = gerald_tools.GERALDDataset(path=gerald_path)
    assert len(gerald) == 5000

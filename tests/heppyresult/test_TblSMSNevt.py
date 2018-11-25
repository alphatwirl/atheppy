# Tai Sakuma <tai.sakuma@gmail.com>
import os
import sys

import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from atheppy.heppyresult import TblSMSNevt

##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_mkdir_p(monkeypatch):
    ret = mock.Mock()
    module = sys.modules['atheppy.heppyresult.TblSMSNevt']
    monkeypatch.setattr(module, 'mkdir_p', ret)
    return ret

@pytest.fixture()
def mock_open(monkeypatch):
    ret = mock.MagicMock()
    try:
        import __builtin__
        monkeypatch.setattr(__builtin__, 'open', ret)
    except ImportError:
        import builtins
        monkeypatch.setattr(builtins, 'open', ret)
    return ret

@pytest.fixture()
def component_t1tttt():
    ret = mock.Mock()
    name = 'SMS_T1tttt_madgraphMLM'
    thisdir = os.path.dirname(os.path.realpath(__file__))
    analyzer_path = os.path.join(
        thisdir, 'test_data', name, 'susyParameterScanAnalyzer')
    ret.susyParameterScanAnalyzer.path = analyzer_path
    ret.name = name
    return ret

@pytest.fixture()
def component_t2bb():
    ret = mock.Mock()
    name = 'SMS_T2bb_madgraphMLM'
    thisdir = os.path.dirname(os.path.realpath(__file__))
    analyzer_path = os.path.join(
        thisdir, 'test_data', name, 'susyParameterScanAnalyzer')
    ret.susyParameterScanAnalyzer.path = analyzer_path
    ret.name = name
    return ret

@pytest.fixture()
def obj():
    ret = TblSMSNevt(
        analyzerName='susyParameterScanAnalyzer',
        fileName='genEvtsPerMass.root',
        outPath='tbt_nevt_sms.txt'
    )
    yield ret

def test_read(obj, mock_open, component_t1tttt, component_t2bb):
    obj.begin()
    obj.read(component_t1tttt)
    obj.read(component_t2bb)

    obj.end()
    write_call_args = open().__enter__().write.call_args_list
    assert 1 == len(write_call_args)
    assert 1148 == (len(write_call_args[0][0][0].split('\n')))


##__________________________________________________________________||

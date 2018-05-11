# Tai Sakuma <tai.sakuma@gmail.com>
import sys
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

has_no_ROOT = False
try:
    import ROOT
except ImportError:
    has_no_ROOT = True

from atheppy.heppyresult import EventBuilderConfig

if not has_no_ROOT:
    from atheppy.heppyresult import EventBuilderConfigMaker

##__________________________________________________________________||
pytestmark = pytest.mark.skipif(has_no_ROOT, reason="has no ROOT")

##__________________________________________________________________||
@pytest.fixture()
def mockroot():
    return mock.Mock()

@pytest.fixture()
def analyzer():
    return mock.Mock(path='/heppyresult/dir/TTJets/treeProducerSusyAlphaT')

@pytest.fixture()
def component(analyzer):
    ret = mock.Mock(treeProducerSusyAlphaT=analyzer)
    ret.configure_mock(name='TTJets')
    return ret

@pytest.fixture()
def obj(monkeypatch, mockroot):
    module = sys.modules['atheppy.heppyresult.EventBuilderConfigMaker']
    monkeypatch.setattr(module, 'ROOT', mockroot)
    return EventBuilderConfigMaker(
        analyzerName='treeProducerSusyAlphaT',
        fileName='tree.root',
        treeName='tree'
    )

##__________________________________________________________________||
def test_repr(obj):
    repr(obj)

def test_create_config_for(obj, component):
    expected = dict(
        inputPaths=['/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root'],
        treeName='tree',
        maxEvents=30,
        start=20,
        name='TTJets',
        component = component,
        check_files=True,
        skip_error_files=True
    )
    actual = obj.create_config_for(
        component,
        files=['/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root'],
        start=20,
        length=30
    )
    assert expected == actual

def test_file_list_in(obj, component):
    expected = ['/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root']
    actual = obj.file_list_in(component)
    assert expected == actual

def test_file_list_in_maxFiles(obj, component):
    expected = [ ]
    actual = obj.file_list_in(component, maxFiles=0)
    assert expected == actual

##__________________________________________________________________||
@pytest.fixture()
def mocktfile():
    ret = mock.Mock()
    ret.good = True
    ret.IsZombie.return_value = False
    return ret

@pytest.fixture()
def mocktfile_null():
    ret = mock.Mock()
    ret.good = False
    ret.GetName.side_effect = ReferenceError
    return ret

@pytest.fixture()
def mocktfile_zombie():
    ret = mock.Mock()
    ret.good = False
    ret.IsZombie.return_value = True
    return ret

@pytest.fixture(params=['good', 'null', 'zombie'])
def file_(request, mocktfile, mocktfile_null, mocktfile_zombie):
    map_ = dict(good=mocktfile, null=mocktfile_null, zombie=mocktfile_zombie)
    return map_[request.param]

def test_nevents_in_file_skip(obj, file_, mockroot):
    obj.skip_error_files = True
    mockroot.TFile.Open.return_value = file_
    actual = obj.nevents_in_file(path='/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root')
    assert [mock.call.TFile.Open('/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root')] == mockroot.method_calls
    if file_.good:
        assert mockroot.TFile.Open().Get().GetEntries() is actual
    else:
        assert 0 == actual

def test_nevents_in_file_raise(obj, file_, mockroot):
    obj.skip_error_files = False
    mockroot.TFile.Open.return_value = file_

    if not file_.good:
        with pytest.raises(OSError):
            actual = obj.nevents_in_file(path='/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root')
    else:
        actual = obj.nevents_in_file(path='/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root')

    assert [mock.call.TFile.Open('/heppyresult/dir/TTJets/treeProducerSusyAlphaT/tree.root')] == mockroot.method_calls

    if file_.good:
        assert mockroot.TFile.Open().Get().GetEntries() is actual

##__________________________________________________________________||

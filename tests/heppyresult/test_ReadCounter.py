# Tai Sakuma <tai.sakuma@gmail.com>
import textwrap
import collections
import io
import os

from atheppy.heppyresult import ReadCounter

##__________________________________________________________________||
sample_counts_txt = """
Counter SkimReport :
	 All Events                                  500000 	 1.00 	 1.0000
	 Sum Weights                              1042218.60703 	 2.08 	 2.0844


"""

def io_from_txt(txt):
    txt = textwrap.dedent(txt[1:])
    try:
        io_ = io.StringIO(txt)
    except TypeError:
        io_ = io.BytesIO(txt.encode())
    return io_

def mock_isfile(path):
    return False

##__________________________________________________________________||
def test_read_file():
    readCounter = ReadCounter()
    file = io_from_txt(sample_counts_txt)
    expected = collections.OrderedDict([('All Events', {'count': 500000.0, 'eff2': 1.0, 'eff1': 1.0}), ('Sum Weights', {'count': 1042218.60703, 'eff2': 2.0844, 'eff1': 2.08})])
    assert expected == readCounter._readImp(file)

def test_no_file():
    isfile_org = os.path.isfile
    os.path.isfile = mock_isfile

    readCounter = ReadCounter()
    assert readCounter('SkimReport.txt') is None

    os.path.isfile = isfile_org

def test_readLine():
    readCounter = ReadCounter()

    line = "	 Sum Weights                              1042218.60703 	 2.08 	 2.0844"
    level, content = readCounter._readLine(line)
    assert 'Sum Weights' == level
    assert {'count': 1042218.60703, 'eff2': 2.0844, 'eff1': 2.08} == content

def test_readLine_tab_in_level():
    readCounter = ReadCounter()

    line = "	 Sum 	 Weights                              1042218.60703 	 2.08 	 2.0844"
    level, content = readCounter._readLine(line)
    assert 'Sum \t Weights' == level
    assert {'count': 1042218.60703, 'eff2': 2.0844, 'eff1': 2.08} == content

def test_readLine_tab_():
    readCounter = ReadCounter()

    line = "\t Sum \t Weights                              1042218.60703 \t 2.08 \t 2.0844"
    level, content = readCounter._readLine(line)
    assert 'Sum \t Weights' == level
    assert {'count': 1042218.60703, 'eff2': 2.0844, 'eff1': 2.08} == content

def test_readLine_scientific_notation():
    readCounter = ReadCounter()
    line = "	 Sum Weights                              3.73134089883e+12 	 154498.74 	 154498.7447"
    level, content = readCounter._readLine(line)
    assert 'Sum Weights' == level
    assert {'count': 3.73134089883e+12, 'eff2': 154498.7447, 'eff1': 154498.74} == content

def test_readLine_netative():
    readCounter = ReadCounter()
    line = "	 too many objects after requirements         -848739 	 -1.00 	 -0.1717"
    level, content = readCounter._readLine(line)
    assert 'too many objects after requirements' == level
    assert {'count': -848739, 'eff1': -1.0, 'eff2': -0.1717} == content

##__________________________________________________________________||

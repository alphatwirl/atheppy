# Tai Sakuma <tai.sakuma@gmail.com>
import textwrap
import io
import os

from atheppy.heppyresult import ReadComponentConfig

##__________________________________________________________________||
sample_cmp_cfg = """
MCComponent: QCD_HT_100To250_Chunk0
	addWeight      :   1.0
	efficiency     :   CFG: eff
	triggers       :   []
	xSection       :   28730000
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
def test_read():
    readConfig = ReadComponentConfig()
    file = io_from_txt(sample_cmp_cfg)
    expected = {'addWeight': 1.0, 'efficiency': 'CFG: eff', 'triggers': [], 'xSection': 28730000}
    assert expected == readConfig._readImp(file)

def test_no_file():
    isfile_org = os.path.isfile
    os.path.isfile = mock_isfile

    readConfig = ReadComponentConfig()
    assert readConfig('config.txt') is None

    os.path.isfile = isfile_org

##__________________________________________________________________||

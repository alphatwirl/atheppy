# Tai Sakuma <tai.sakuma@gmail.com>
from alphatwirl.misc import mkdir_p
from alphatwirl.misc import list_to_aligned_text
import os
import numpy as np
import ROOT

##__________________________________________________________________||
class TblSMSNevt(object):
    def __init__(self, analyzerName, fileName, outPath):
        self.analyzerName = analyzerName
        self.fileName = fileName
        self.outPath = outPath

    def begin(self):
        self.rows = [('component', 'histname', 'smsmass1', 'smsmass2', 'nevt')]

    def read(self, component):
        inputPath = os.path.join(getattr(component, self.analyzerName).path, self.fileName)
        file_ = ROOT.TFile.Open(inputPath)

        histnames = ['h_Gluino_LSP', 'h_Stop_LSP', 'h_Sbottom_LSP', 'h_Squark_LSP']
        for histname in histnames:
            h = file_.Get(histname)
            xaxis_lastbin_lowedge = h.GetXaxis().GetBinLowEdge(h.GetNbinsX()+1)
            mass1 = np.concatenate((np.array([1]), np.arange(50, xaxis_lastbin_lowedge+50, step=50, dtype=int)))
            yaxis_lastbin_lowedge = h.GetYaxis().GetBinLowEdge(h.GetNbinsY()+1)
            mass2 = np.concatenate((np.array([1]), np.arange(50, yaxis_lastbin_lowedge+50, step=50, dtype=int)))
            for m1 in mass1:
                binx = h.GetXaxis().FindBin(m1)
                ## binlowedgex = h.GetXaxis().GetBinLowEdge(binx)
                for m2 in mass2:
                    biny = h.GetYaxis().FindBin(m2)
                    ## binlowedgey = h.GetYaxis().GetBinLowEdge(biny)
                    c = h.GetBinContent(binx, biny)
                    if c == 0:
                        continue
                    self.rows.append(
                        (component.name, histname,
                        int(m1), int(m2), int(c))
                    )

    def end(self):
        mkdir_p(os.path.dirname(self.outPath))
        with open(self.outPath, 'w') as f:
            f.write(list_to_aligned_text(self.rows))

##__________________________________________________________________||

# Tai Sakuma <tai.sakuma@cern.ch>
import os
import sys
import logging

import gzip

try:
   import cPickle as pickle
except:
   import pickle

import alphatwirl
from alphatwirl.misc.deprecation import _deprecated_class_method_option

from .yes_no import query_yes_no
from . import heppyresult

##__________________________________________________________________||
import logging
logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler(stream=sys.stdout)
log_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

##__________________________________________________________________||
class AtHeppy(object):
    """A simple framework for looping over Heppy flat trees with alphatwirl

    Args:
        outdir (str): the output directory
        heppydir (str): Heppy results dir
        datamc (str): 'data' or 'mc'
        susy_sms (bool): if True, don't create tbl_xsec.txt
        force (bool): overwrite the output if True
        quiet (bool): don't show progress bars if True
        parallel_mode (str): 'multiprocessing', 'subprocess', 'htcondor'
        dispatcher_options (dict): options to dispatcher
        process (int): the number of processes for the 'multiprocessing' mode
        user_modules (list of str): names of python modules to be copied for the 'subprocess' mode
        max_events_per_dataset (int): maximum number of events per data set
        max_events_per_process (int): maximum number of events per process (job)
        max_files_per_dataset (int): maximum number of files per data set
        max_files_per_process (int): maximum number of files per process (job)
        profile (bool): run cProfile if True
        profile_out_path (bool): path to store the result of the profile. stdout if None

    """
    @_deprecated_class_method_option('htcondor_job_desc_extra', msg='use dispatcher_options instead')
    def __init__(self, outdir, heppydir,
                 datamc='mc',
                 susy_sms=False,
                 force=False, quiet=False,
                 parallel_mode='multiprocessing',
                 htcondor_job_desc_extra=[ ],
                 dispatcher_options=dict(),
                 process=4,
                 user_modules=set(),
                 max_events_per_dataset=-1,
                 max_events_per_process=-1,
                 max_files_per_dataset=-1,
                 max_files_per_process=1,
                 profile=False,
                 profile_out_path=None
    ):
        user_modules = set(user_modules)
        user_modules.add('atheppy')
        self.parallel = alphatwirl.parallel.build_parallel(
           parallel_mode=parallel_mode,
           quiet=quiet,
           processes=process,
           user_modules=user_modules,
           ## htcondor_job_desc_extra=htcondor_job_desc_extra,
           dispatcher_options=dispatcher_options
        )
        self.outdir = outdir
        self.heppydir = heppydir
        self.datamc = datamc
        self.susy_sms = susy_sms
        self.force =  force
        self.max_events_per_dataset = max_events_per_dataset
        self.max_events_per_process = max_events_per_process
        self.max_files_per_dataset = max_files_per_dataset
        self.max_files_per_process = max_files_per_process
        self.profile = profile
        self.profile_out_path = profile_out_path
        self.parallel_mode = parallel_mode

    def run(self, components,
            reader_collector_pairs,
            analyzerName,
            fileName='tree.root',
            treeName='tree'
    ):
        self.parallel.begin()
        try:
            loop = self._configure(
               components, reader_collector_pairs,
               analyzerName, fileName, treeName
            )
            self._run(loop)
        except KeyboardInterrupt:
            logger = logging.getLogger(__name__)
            logger.warning('received KeyboardInterrupt')
            if self.parallel_mode in ('multiprocessing', ):
               self.parallel.terminate()
            else:
               if query_yes_no('terminate running jobs'):
                  logger.warning('terminating running jobs')
                  self.parallel.terminate()
               else:
                  logger.warning('not terminating running jobs')
        self.parallel.end()

    def _configure(self, components, reader_collector_pairs,
                   analyzerName, fileName, treeName):

        dataset_readers = alphatwirl.datasetloop.DatasetReaderComposite()

        # tbl_heppyresult.txt
        tbl_heppyresult_path = os.path.join(self.outdir, 'tbl_heppyresult.txt')
        if self.force or not os.path.exists(tbl_heppyresult_path):
            # e.g., '74X/MC/20150810_MC/20150810_SingleMu'
            heppydir_rel = '/'.join(self.heppydir.rstrip('/').split('/')[-4:])
            alphatwirl.mkdir_p(os.path.dirname(tbl_heppyresult_path))
            f = open(tbl_heppyresult_path, 'w')
            f.write('heppyresult\n')
            f.write(heppydir_rel + '\n')
            f.close()

        # tbl_tree.txt
        tbl_tree_path = os.path.join(self.outdir, 'tbl_tree.txt')
        if self.force or not os.path.exists(tbl_tree_path):
            tblTree = heppyresult.TblTree(
                analyzerName=analyzerName,
                fileName=fileName,
                treeName=treeName,
                outPath=tbl_tree_path,
            )
            dataset_readers.add(tblTree)

        # tbl_branch.txt
        tbl_branch_path = os.path.join(self.outdir, 'tbl_branch.txt')
        if self.force or not os.path.exists(tbl_branch_path):
            tblBranch = heppyresult.TblBranch(
                analyzerName=analyzerName,
                fileName=fileName,
                treeName=treeName,
                outPath=tbl_branch_path,
            )
            dataset_readers.add(tblBranch)

        # tbl_branch_size.tx
        tbl_branch_size_path = os.path.join(self.outdir, 'tbl_branch_size.txt')
        if self.force or not os.path.exists(tbl_branch_size_path):
            tblBranchSize = heppyresult.TblBranch(
                analyzerName=analyzerName,
                fileName=fileName,
                treeName=treeName,
                outPath=tbl_branch_size_path,
                addType=False,
                addSize=True,
                sortBySize=True,
            )
            dataset_readers.add(tblBranchSize)

        # tbl_branch_title.txt
        tbl_branch_title_path = os.path.join(self.outdir, 'tbl_branch_title.txt')
        if self.force or not os.path.exists(tbl_branch_title_path):
            tblBranchTitle = heppyresult.TblBranch(
                analyzerName=analyzerName,
                fileName=fileName,
                treeName=treeName,
                outPath=tbl_branch_title_path,
                addType=False,
                addSize=False,
                addTitle=True,
            )
            dataset_readers.add(tblBranchTitle)

        # tbl_dataset.txt
        tbl_dataset_path = os.path.join(self.outdir, 'tbl_dataset.txt')
        if self.force or not os.path.exists(tbl_dataset_path):
            tblDataset = heppyresult.TblComponentConfig(
                outPath=tbl_dataset_path,
                columnNames=('dataset', ),
                keys=('dataset', ),
            )
            dataset_readers.add(tblDataset)

        # tbl_xsec.txt for MC
        if self.datamc == 'mc' and not self.susy_sms:
            tbl_xsec_path = os.path.join(self.outdir, 'tbl_xsec.txt')
            if self.force or not os.path.exists(tbl_xsec_path):
                tblXsec = heppyresult.TblComponentConfig(
                    outPath=tbl_xsec_path,
                    columnNames=('xsec', ),
                    keys=('xSection', ),
                )
                dataset_readers.add(tblXsec)

        # tbl_nevt.txt for MC
        if self.datamc == 'mc':
            tbl_nevt_path = os.path.join(self.outdir, 'tbl_nevt.txt')
            if self.force or not os.path.exists(tbl_nevt_path):
                tblNevt = heppyresult.TblCounter(
                    outPath=tbl_nevt_path,
                    columnNames=('nevt', 'nevt_sumw'),
                    analyzerName='skimAnalyzerCount',
                    fileName='SkimReport.txt',
                    levels=('All Events', 'Sum Weights')
                )
                dataset_readers.add(tblNevt)

        reader_top = alphatwirl.loop.ReaderComposite()
        collector_top = alphatwirl.loop.CollectorComposite()
        for r, c in reader_collector_pairs:
            reader_top.add(r)
            collector_top.add(c)
        eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(self.parallel.communicationChannel)
        eventBuilderConfigMaker = heppyresult.EventBuilderConfigMaker(
           analyzerName=analyzerName, fileName=fileName, treeName=treeName,
           check_files=True, skip_error_files=True
        )
        datasetIntoEventBuildersSplitter = alphatwirl.loop.DatasetIntoEventBuildersSplitter(
            EventBuilder=alphatwirl.roottree.BuildEvents,
            eventBuilderConfigMaker=eventBuilderConfigMaker,
            maxEvents=self.max_events_per_dataset,
            maxEventsPerRun=self.max_events_per_process,
            maxFiles=self.max_files_per_dataset,
            maxFilesPerRun=self.max_files_per_process
        )
        eventReader = alphatwirl.loop.EventDatasetReader(
            eventLoopRunner=eventLoopRunner,
            reader=reader_top,
            collector=collector_top,
            split_into_build_events=datasetIntoEventBuildersSplitter
        )

        dataset_readers.add(eventReader)

        if components == ['all']: components = None
        heppyResult = heppyresult.HeppyResult(
            path=self.heppydir,
            componentNames=components,
            componentHasTheseFiles=[analyzerName]
        )

        if self.parallel_mode in ('multiprocessing', ):
            loop = alphatwirl.datasetloop.DatasetLoop(
               datasets=heppyResult.components(),
               reader=dataset_readers
            )
        else:
            loop = alphatwirl.datasetloop.ResumableDatasetLoop(
               datasets=heppyResult.components(),
               reader=dataset_readers,
               workingarea=self.parallel.workingarea
            )

        return loop

    def _run(self, loop):
        if not self.profile:
            loop()
        else:
            alphatwirl.misc.print_profile_func(
               func=loop,
               profile_out_path=self.profile_out_path
            )

##__________________________________________________________________||

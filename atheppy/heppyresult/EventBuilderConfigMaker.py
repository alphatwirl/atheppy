# Tai Sakuma <tai.sakuma@gmail.com>
import os
import logging

import ROOT

from alphatwirl.roottree.inspect import is_ROOT_null_pointer
from alphatwirl.roottree import BEvents

from .EventBuilderConfig import EventBuilderConfig as HeppyEventBuilderConfig

##__________________________________________________________________||
class EventBuilderConfigMaker(object):
    def __init__(self, analyzerName, fileName, treeName,
                 check_files=True, skip_error_files=True):
        self.analyzerName = analyzerName
        self.fileName = fileName
        self.treeName = treeName
        self.check_files = check_files
        self.skip_error_files = skip_error_files

    def __repr__(self):
        name_value_pairs = (
            ('analyzerName', self.analyzerName),
            ('fileName', self.fileName),
            ('treeName', self.treeName),
            ('check_files', self.check_files),
            ('skip_error_files', self.skip_error_files),
        )
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def create_config_for(self, dataset, files, start, length):
        config = dict(
            events_class=BEvents,
            file_paths=files,
            tree_name=self.treeName,
            max_events=length,
            start=start,
            check_files=self.check_files,
            skip_error_files=self.skip_error_files,
            name=dataset.name, # for the progress report writer
            component=dataset # for scribblers
        )
        return config

    def file_list_in(self, dataset, maxFiles=-1):
        component = dataset
        files = [os.path.join(getattr(component, self.analyzerName).path, self.fileName)]
        if maxFiles < 0:
            return files
        return files[:min(maxFiles, len(files))]

    def nevents_in_file(self, path):
        file_ = ROOT.TFile.Open(path)
        if is_ROOT_null_pointer(file_) or file_.IsZombie():
            logger = logging.getLogger(__name__)
            if self.skip_error_files:
                logger.warning('cannot open {}'.format(path))
                return 0
            logger.error('cannot open {}'.format(path))
            raise OSError('cannot open {}'.format(path))
        tree = file_.Get(self.treeName)
        return tree.GetEntries() # GetEntries() is slow. call only as
                                 # many times as necessary

##__________________________________________________________________||

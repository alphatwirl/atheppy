# Tai Sakuma <tai.sakuma@gmail.com>

##__________________________________________________________________||
import collections

##__________________________________________________________________||
# deprecated. use dict instead
EventBuilderConfig = collections.namedtuple(
    'EventBuilderConfig',
    'inputPaths treeName maxEvents start name component'
)

# base is for roottree.EventBuilderConfig

##__________________________________________________________________||

# Tai Sakuma <tai.sakuma@cern.ch>

##__________________________________________________________________||
def collect_results_into_tuplelist(reader, columns):
    ret = reader.results().to_tuple_list()
    # e.g.,
    # ret = [
    #         (200, 2, 120, 240),
    #         (300, 2, 490, 980),
    #         (300, 3, 210, 420)
    #         (300, 2, 20, 40),
    #         (300, 3, 15, 30)
    # ]

    return ret

##__________________________________________________________________||
def combine_results_into_tuplelist(dataset_reader_list, summary_columns, dataset_column='dataset'):

    if not dataset_reader_list:
        return None

    # e.g.,
    # dataset_reader_list = [
    #     ('QCD',    reader),
    #     ('TTJets', reader),
    #     ('WJets',  reader),
    # ]

    dataset_tuple_list_pairs = [(d, r.results().to_tuple_list()) for d, r in dataset_reader_list]
    # e.g.,
    # dataset_tuple_list_pairs = [
    #     ('QCD', [
    #         (200, 2, 120, 240),
    #         (300, 2, 490, 980),
    #         (300, 3, 210, 420)
    #     ]),
    #     ('TTJets', [
    #         (300, 2, 20, 40),
    #         (300, 3, 15, 30)
    #     ]),
    #     ('WJets', [])
    # ]

    ret = [ ]
    for dataset, tuple_list in dataset_tuple_list_pairs:
        ret.extend([(dataset, ) + e for e in tuple_list])
    # e.g.,
    # [
    #     ('QCD',    200, 2, 120, 240),
    #     ('QCD',    300, 2, 490, 980),
    #     ('QCD',    300, 3, 210, 420),
    #     ('TTJets', 300, 2,  20,  40),
    #     ('TTJets', 300, 3,  15,  30)
    # ]

    header = (dataset_column, ) + summary_columns

    ret.insert(0, header)
    # e.g.,
    # [
    #     ('dataset', 'htbin', 'njetbin', 'n', 'nvar'),
    #     ('QCD',         200,         2, 120,    240),
    #     ('QCD',         300,         2, 490,    980),
    #     ('QCD',         300,         3, 210,    420),
    #     ('TTJets',      300,         2,  20,     40),
    #     ('TTJets',      300,         3,  15,     30)
    # ]

    return ret

##__________________________________________________________________||
def return_none(*_, **__):
    return None

##__________________________________________________________________||
def collect(dataset_reader_list, func_combine, func_deliver=None):
    combined = func_combine(dataset_reader_list)
    if func_deliver is not None:
        func_deliver(combined)
    return combined

##__________________________________________________________________||

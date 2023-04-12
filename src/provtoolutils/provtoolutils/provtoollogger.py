import logging

provtoollogger = logging.getLogger('provtool')

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
provtoollogger = logging.getLogger('provtool')
provtoollogger.setLevel(logging.WARNING)

fh = logging.FileHandler('provtool.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(FORMAT))
provtoollogger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(logging.Formatter(FORMAT))
provtoollogger.addHandler(ch)

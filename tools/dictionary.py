#!/usr/bin/python3

'''
Dictionary holding abbreviations to be used by xml2db to shorten long PVs.
Syntax:
    Function abbreviation() has to return a dictionary type variable.
    The words to abbreviate have to be the "keys" of the dictionary, while the abbreviations are the "values"
'''
def abbreviation():
    abbr = dict([
        ('amplitude', 'amp'), ('Amplitude', 'Amp'), 
        ('phase', 'phi'), ('Phase', 'Phi'), 
        ('calibration', 'cal'), ('Calibration', 'Cal'), 
        ('after', 'aft'), ('After', 'Aft'), 
        ('average', 'avg'), ('Average', 'Avg'), 
        ('request', 'req'), ('Request', 'Req'), 
        ('deviation', 'dev'), ('Deviation', 'Dev'), 
        ('standard', 'std'), ('Standard', 'Std'), 
        ('register', 'reg'), ('Register', 'Reg'), 
        ('registers', 'regs'), ('Registers', 'Regs'), 
        ('maximum', 'max'), ('Maximum', 'Max'), 
        ('minimum', 'min'), ('Minimum', 'Min'), 
        ('Output', 'Out'), 
        ('correction', 'corr'), ('Correction', 'Corr'), 
        ('configuration', 'cfg'), ('Configuration', 'Cfg'), 
        ('low', 'lo'), ('Low', 'Lo'), 
        ('high', 'hi'), ('High', 'Hi'), 
        ('triggers', 'trg'), ('Triggers', 'Trg'), 
        ('trigger', 'trg'), ('Trigger', 'Trg'), 
        ('Iand', 'I'), 
        ('forward', 'fwd'), ('Forward', 'Fwd')
        ])
    return abbr
import numpy as np
from preprocess_functions import preprocess_dataset,normalize,set_type
from util.timit_dataset import create_dataloader
from util.functions import test_file
from six.moves import cPickle 
import torch
import yaml
import editdistance
import os

def adjust_phone(list):
	#remove closing sounds
	while 'h#' in list: list.remove('h#')

	#all upper
	list = [x.upper() for x in list]

	#add stress numbers for vowels
	vowel = 'AEIOU'
	list = [x + '1' if x[0] in vowel else x for x in list]

	#convert timit-specific phonemes to phonemes recognized by the speech aligner
	list = ['T' if x == 'DX' else x for x in list]
	return list
	
def generate_guess(path):
	data_type = 'float32'

	mean_val = np.loadtxt('config/mean_val.txt')
	std_val = np.loadtxt('config/std_val.txt')

	x, y = preprocess_dataset('TIMIT/TEST/{}'.format(path))

	x = normalize(x, mean_val, std_val)
	x = set_type(x, data_type)

	config_path = 'config/las_example_config.yaml'
	conf = yaml.load(open(config_path,'r'))

	test_set = create_dataloader(x, y, **conf['model_parameter'], **conf['training_parameter'], shuffle=False)
	listener = torch.load(conf['training_parameter']['pretrained_listener_path'], map_location=lambda storage, loc: storage)
	speller = torch.load(conf['training_parameter']['pretrained_speller_path'], map_location=lambda storage, loc: storage)
	optimizer = torch.optim.Adam([{'params':listener.parameters()}, {'params':speller.parameters()}], lr=conf['training_parameter']['learning_rate'])

	for batch_index,(batch_data,batch_label) in enumerate(test_set):
		pred,true = test_file(batch_data, batch_label, listener, speller, optimizer, **conf['model_parameter'])

		pred = list(pred)
		pred  = adjust_phone(pred)

		str = 'WORD '

		for x in pred:
			str += x + ' '

		os.makedirs('montreal-forced-aligner/bin/dict/', exist_ok=True)
		with open('montreal-forced-aligner/bin/dict/SA1dict.txt', 'w+') as f:
			f.write(str)
			f.close()

generate_guess('DR1/FAKS0/SA1.PHN')
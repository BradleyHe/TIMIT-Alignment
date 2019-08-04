import numpy as np
from preprocess_functions import preprocess_dataset,normalize,set_type
from util.timit_dataset import create_dataloader
from util.functions import test_file
from six.moves import cPickle 
import torch
import yaml
import editdistance
import os
import sox
import subprocess
import shutil

bin_path = os.path.join('montreal-forced-aligner', 'bin')

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

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
	
def generate_dict(path):
	data_type = 'float32'

	mean_val = np.loadtxt('config/mean_val.txt')
	std_val = np.loadtxt('config/std_val.txt')

	x, y = preprocess_dataset(path)

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
		pred = adjust_phone(pred)

		str = 'WORD '

		for x in pred:
			str += x + ' '

		os.makedirs(os.path.join(bin_path, 'mixed'), exist_ok=True)
		with open(path[:-4] + '.dict', 'w+') as f:
			f.write(str)
			f.close()

def align_mixed(file1, file2):
	f1name = file1.split('/')[-1]
	f2name = file2.split('/')[-1]
	f1speaker = file1.split('/')[-2]
	f2speaker = file2.split('/')[-2]
	mix_fname = os.path.join(bin_path, 'mixed', f1speaker + '_' + f2speaker, f1name[:-4] + '_' + f2name)

	tfn = sox.Transformer()
	tfn.silence(location=-1)

	cbn = sox.Combiner()
	cbn.set_input_format(file_type=['wav', 'wav'])

	len1 = float(tfn.stat(file1)['Length (seconds)'])
	len2 = float(tfn.stat(file2)['Length (seconds)'])

	rms1 = sox.file_info.stat(file1)['RMS     amplitude']
	rms2 = sox.file_info.stat(file2)['RMS     amplitude']
	factor = tir_factor(0, rms1, rms2)

	os.makedirs(os.path.join(bin_path, 'mixed', f1speaker + '_' + f2speaker), exist_ok=True)

	if len1 < len2:		
		tfn.trim(0, len1)
		tfn.build(file2, os.path.join(bin_path, 'mixed', f2name))
		cbn.build([file1, os.path.join(bin_path, 'mixed', f2name)], mix_fname, 
								'mix', [1, 1 / factor])
		shutil.copy(file1[:-4] + '.PHN', mix_fname[:-4] + '.PHN')
		os.remove(os.path.join(bin_path, 'mixed', f2name))

	else:
		tfn.trim(0, len2)
		tfn.build(file1, os.path.join(bin_path, 'mixed', f1name))
		cbn.build([os.path.join(bin_path, 'mixed', f1name), file2], mix_fname, 
								'mix', [1, 1 / factor])
		shutil.copy(file2[:-4] + '.PHN', mix_fname[:-4] + '.PHN')
		os.remove(os.path.join(bin_path, 'mixed', f1name))

	
	generate_dict(mix_fname[:-4] + '.PHN')

	with open(mix_fname[:-4] + '.lab', 'w+') as f:
		f.write('WORD')

	os.makedirs(os.path.join(bin_path, 'mixed', 'aligned'), exist_ok=True)
	subprocess.run([os.path.join('./', bin_path, 'mfa_align'), os.path.join(bin_path, 'mixed', f1speaker + '_' + f2speaker), 
										 mix_fname[:-4] + '.dict', 'english', os.path.join(bin_path, 'mixed', 'aligned', f1speaker + '_' + f2speaker)])

align_mixed(bin_path + '/TIMIT/TEST/DR1/FAKS0/SA1.wav', bin_path + '/TIMIT/TEST/DR1/FAKS0/SA2.wav')
import numpy as np
from timit_preprocess import preprocess_dataset,normalize,set_type
from util.timit_dataset import create_dataloader
from util.functions import test_file
from six.moves import cPickle 
import torch
import yaml
import editdistance

data_type = 'float32'

mean_val = np.loadtxt('config/mean_val.txt')
std_val = np.loadtxt('config/std_val.txt')

x, y = preprocess_dataset('TIMIT/TEST/DR1/FAKS0/SA2.PHN')

x = normalize(x, mean_val, std_val)
x = set_type(x, data_type)

with open('test.pkl', 'wb') as cPickle_file:
    cPickle.dump([x, y], cPickle_file, protocol=cPickle.HIGHEST_PROTOCOL)

config_path = 'config/las_example_config.yaml'
conf = yaml.load(open(config_path,'r'))

test_set = create_dataloader(x, y, **conf['model_parameter'], **conf['training_parameter'], shuffle=False)
listener = torch.load(conf['training_parameter']['pretrained_listener_path'], map_location=lambda storage, loc: storage)
speller = torch.load(conf['training_parameter']['pretrained_speller_path'], map_location=lambda storage, loc: storage)
optimizer = torch.optim.Adam([{'params':listener.parameters()}, {'params':speller.parameters()}], lr=conf['training_parameter']['learning_rate'])

for batch_index,(batch_data,batch_label) in enumerate(test_set):
	pred,true = test_file(batch_data, batch_label, listener, speller, optimizer, **conf['model_parameter'])
	print(pred)
	print(true)
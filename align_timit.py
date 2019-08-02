import os
import subprocess

bin_path = os.path.join('montreal-forced-aligner', 'bin')
source_path = os.path.join(bin_path,  'TIMIT', 'TEST')

# generate .lab files
for dirName, subdirList, fileList in os.walk(source_path):
	for file in fileList:
		# comment out if you want to keep these files, but they are not needed for preprocessing
		if file.endswith('.WAV') or file.endswith('.PHN') or file.endswith('WRD'):
			os.remove(dirName + '/' + file)
			continue

		if file.endswith('wav'):
			continue

		# files remaining are .TXT
		# rename to .lab and edit to correct format
		with open(dirName + '/' + file) as f:
			str = ''.join(x for x in f.read() if not x.isdigit() and not x == '.')
			with open(dirName + '/' + file[:-4] + '.lab', 'w+') as w:
				w.write(str.lstrip())
		
# run montreal forced aligner on all voice files
# will run only in test files
for dialect in os.listdir(source_path):
	for speaker in os.listdir(os.path.join(source_path, dialect)):
		output = os.path.join(bin_path, 'aligned', speaker)
		os.makedirs(output, exist_ok=True)

		subprocess.run([os.path.join('./', bin_path, 'mfa_align'), os.path.join(source_path, dialect, speaker), 
										os.path.join(bin_path, 'libridict.txt'), 'english', output])

		


import os
# import pysnooper

bin_path = os.path.join('montreal-forced-aligner', 'bin')
source_path = os.path.join(bin_path,  'TIMIT', 'TEST')
sample_rate = 16000.0

def adjust_phone(list):
  adjust = []

  # turn everything uppercase
  for line in list:
    line[0] = float(line[0])
    line[1] = float(line[1])

    line[2] = line[2].upper()
    if line[2] == 'H#': line[2] = 'sil'

    adjust.append(line)

  # in TIMIT, there are various closing sounds (indicated by -CL).
  # It is better to merge them with their respective phonemes to clear the graph up
  # combine two phonemes if the starting one ends with 'CL' and both have the same starting letter

  x = 0
  while x < len(adjust)-1:
    if adjust[x][2].endswith('CL') and adjust[x][2][0] == adjust[x + 1][2][0]:
      adjust[x + 1][0] = adjust[x][0]
      adjust.pop(x)
    else:
      x += 1
  return adjust

# generate textgrid files
for dirName, subdirList, fileList in os.walk(source_path):
  for file in fileList:
    if file.endswith('.PHN'):
      lines = []
      with open(dirName + '/' + file) as f:
        [lines.append(line.rstrip().split(' ')) for line in f.readlines()]

      lines = adjust_phone(lines)

      # start textgrid file
      out = '''\
            File type = "ooTextFile"
            Object class = "TextGrid"
            xmin = 0.0\n'''
      out += 'xmax = ' + str(lines[-1][1] / sample_rate)
      out += '''
            tiers? <exists>
            size = 1
            item []:
            item [1]:
            class = "IntervalTier"
            name = "phones"
            xmin = 0.0\n'''
      out += 'xmax = ' + str(lines[-1][1] / sample_rate) + '\n'
      out += 'intervals: size = ' + str(len(lines)) + '\n'

      for x in range(0, len(lines)):
        out += 'intervals [{}]:'.format(str(x + 1)) + '\n'
        out += 'xmin = ' + str(lines[x][0] / sample_rate) + '\n'
        out += 'xmax = ' + str(lines[x][1] / sample_rate) + '\n'
        out += 'text = \"{}\"\n'.format(lines[x][2])

      # edit this to change where the textgrid files will go
      target = os.path.join(bin_path, 'aligned', dirName[-5:])
      os.makedirs(target, exist_ok=True)

      with open(target + '/' + file[:-3] + 'TextGrid', 'w+') as f:
        f.write(out)

    


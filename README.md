# TIMIT Forced Alignment
This is a modified version of the [Pytorch implementation](https://github.com/AzizCode92/Listen-Attend-and-Spell-Pytorch) of LAS, configured to work with the [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner).

## Setup
- Run timit_preprocess.sh to convert NIST .WAV to RIFF.wav
- Place montreal forced aligner folder in this directory
- Move the TIMIT directory to montreal-forced-aligner/bin
- Download the [LibriSpeech lexicon](http://www.openslr.org/resources/11/librispeech-lexicon.txt) and place it in montreal-forced-aligner/bin
- Run align_timit.py to generate alignments of all test files

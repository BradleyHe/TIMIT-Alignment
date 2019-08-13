# TIMIT Forced Alignment
This is a modified version of the [Pytorch implementation](https://github.com/AzizCode92/Listen-Attend-and-Spell-Pytorch) of LAS, configured to work with the [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner).

Since there seems to be a problem with the montreal forced aligner not working on some of the voice files, I have provided all alignments of all test voice files in this repository.

## Setup
- Run timit_preprocess.sh to convert NIST .WAV to RIFF.wav
- Place montreal forced aligner folder in this directory
- Move the TIMIT directory to montreal-forced-aligner/bin
- Download the [LibriSpeech lexicon](http://www.openslr.org/resources/11/librispeech-lexicon.txt) and place it in montreal-forced-aligner/bin
- Depending on what you want to do, you can run align_timit.py to generate TextGrid alignments of all test files, or you can run gen_timit_alignment.py to convert TIMIT phoneme files to a TextGrid format.

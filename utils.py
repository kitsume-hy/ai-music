import config 
import numpy as np
import itertools
import soundfile as sf
from numpy import fromstring, int16,int32
import struct

def key_pentas_list(choice_key="C"):
    rela_penta = np.array([0,2,4,7,9])
    base_penta = np.array([],dtype=int)

    for octave in range(11):
        temp = rela_penta  + (12*octave )
        base_penta = np.append(base_penta,temp)

    low_pitch  = config.pitch_char2num_dicts["B3"]
    high_pitch = config.pitch_char2num_dicts["D5"]

    val = config.pitch_char2num_dicts[choice_key + "-2"] #C-2をとってくる -1,+1でもなんでもいい。
    key_penta       = base_penta + val                   #key choice_keyでのペンタトニックスケール羅列
    key_penta_range = key_penta[(key_penta >= low_pitch)&(key_penta<=high_pitch )] #きりたんの音域にあうピッチのみ
    key_penta_range = [config.pitch_num2char_dicts[i] for i in key_penta_range] #ピッチ数を文字列に変換する

    return key_penta_range

#モチーフパターンを羅列
def make_motif_pattern_list(use_note_lists):
    dulation_char2num_dicts = {key:val for key,val in config.dulation_char2num_dicts.items() if key in use_note_lists}
    list_note_dulation = np.array(list(dulation_char2num_dicts.values()))
    list_char          = dulation_char2num_dicts.keys()

    note_max_count = [np.arange(int(1+96/i) ) for i in list_note_dulation ]
    note_count_candi = itertools.product( *note_max_count )

    pattern_list = []
    for note_count in note_count_candi:
        dulation_sum = np.dot(list_note_dulation, note_count)
        if dulation_sum == 96:
            pattern_list.append(note_count)

    dulation_prob = {i:1 for i in use_note_lists }

    list_char = [[i] for i in list_char]
    note_prob = list( dulation_prob.values() )

    motif_pattern_list = []
    motif_pattern_prob_list = []

    for pattern in pattern_list:
        synth_char = []
        motif_prob = 1

        for num, note_count in enumerate(pattern):
            synth_char += list_char[num] * note_count
            motif_prob *= note_prob[num] ** note_count 

        motif_pattern_list.append(synth_char)
        motif_pattern_prob_list.append(motif_prob)
    motif_pattern_prob_list = motif_pattern_prob_list/np.sum( motif_pattern_prob_list )
    ##############################################################
    return motif_pattern_list,motif_pattern_prob_list

#wav ファイルのはじめと終わりの1小節を削除して上書き保存 (neutrino用)
def cut_firstend_bar(wav_path,bpm):

    data,samplerate = sf.read(wav_path)
    bar_frames = int(samplerate*240/bpm)

    data_cut = data[bar_frames:-bar_frames]
    sf.write(wav_path,data_cut,samplerate)


def repeat_loop(loop_path,out_path,repeat_num=1):
    data,samplerate = sf.read(loop_path,always_2d=True)

    data_cut = np.tile(data,[repeat_num,1])
    sf.write(out_path,data_cut,samplerate)
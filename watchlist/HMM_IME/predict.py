import numpy as np
import nltk
import os
import math
import time
from collections import defaultdict

# 拼音预测器
class predicter():
    # 初始化
    def __init__(self):
        start = time.time()
        module_path = os.path.dirname(__file__)
        # 读取 转移概率 发射概率 拼音词典
        (self.cpd_tags, self.cpd_tagwords, self.pinyin2hanzi) = np.load(module_path + "/model/model_cut_for_search.npy", allow_pickle=True)
        end = time.time()
        # 计算模型加载时间
        self.load_model_time = end - start

    def predict(self, sentence):
        return self.recognize_HMM(self.cpd_tags, self.cpd_tagwords, sentence, self.pinyin2hanzi, DEBUG=False)

    ## 识别函数，参数列表： 转移概率，发射概率，原句，标签集合，已标记的标签
    def recognize_HMM(self, cpd_tags, cpd_tagwords, sentence, pinyin2hanzi, labeled_tags = [], DEBUG=False):
        viterbi = [ ]           # 维特比链
        
        first_viterbi = defaultdict(int)
        for tag in pinyin2hanzi[ sentence[1] ]:
            # Y 是 第一个拼音 的每一种可能的Tag
            if tag == "START": continue
            first_viterbi[ tag ] = cpd_tags["START"].prob(tag) * cpd_tagwords[tag].prob( sentence[1] )
            # P( "第一个拼音" | "Y")
        viterbi.append(first_viterbi)
        
        # 这里是 求 (START, END), 因为如果把 "END" 也算入，循环之后取出来的概率就是"END"的Tag（错误)，而不是"END"之前的那个Tag
        for wordindex in range(2, len(sentence) - 1):
            this_viterbi = defaultdict(int)
            prev_viterbi = viterbi[-1]
            for tag in pinyin2hanzi[ sentence[ wordindex ] ]:
                # START没有卵用的，我们要忽略
                if tag == "START": continue
                # 如果现在这个tag是X，现在的单词是w，
                # 我们想找前一个tag Y，并且让最好的tag sequence以 Y X 结尾。
                # 也就是说
                # Y要能最大化：
                # prev_viterbi[ Y ] * P(X | Y) * P( w | X)
                # 排序——逆序
                best_previous_list = sorted(prev_viterbi.keys(),
                                    key = lambda prevtag: \
                            prev_viterbi[ prevtag ] * cpd_tags[ prevtag[-1] ].logprob(tag) * cpd_tagwords[tag].logprob(sentence[wordindex]),
                                        reverse = True)
                
                # 如果是前缀的话，为了避免状态爆炸，取最大的20个就好了，错误，
                
                for best_previous in  best_previous_list: 
                    # 不应该是一阶HMM了，应该是全部的前缀  !!!!!!!
                    prob =  prev_viterbi[ best_previous ] * \
                            cpd_tags[ best_previous[-1] ].prob(tag) * cpd_tagwords[ tag ].prob(sentence[wordindex]) 
                    if prob == 0:
                        continue
                    this_viterbi[ best_previous + tag ] = prob
            # 每次遍历Tag集找完Y 我们把目前最好的 X = currbest存一下
            if DEBUG:
                currbest = max(this_viterbi.keys(), key = lambda tag: this_viterbi[ tag ])
                print( "Word", "'" + sentence[ wordindex ] + "'", "current best pre-sequence:", currbest)
            
            # 完结
            # 全部存下来
            viterbi.append(this_viterbi)
        
        # 找所有以END结尾的tag sequence
        prev_viterbi = viterbi[-1]
        
        # 同理 这里也有倒过来 !!!!!!!!!!!!!!!   就放到了循环了。。。
        
        # 取所有概率大于0 的
        word_prob_dict = { }
        for key in prev_viterbi.keys():
            word_prob_dict[ key ] = prev_viterbi[ key ] * cpd_tags[ key[-1] ].prob("END")
        
        if DEBUG:
            for (best_previous, prob_tagsequence) in sorted(word_prob_dict.items(), key = lambda item: item[1], reverse = True)[:20]:
                # 就是排序的概率，再算一次
                # 我们这会儿是倒着存的。因为好的在后面

                # 回溯 最好的tag
                # 这里为什么可以把 最后一个 回溯dict忽略？？？？？？
                # 因为"START" "NNP" 中 "NNP" 总是能在第一个单词的 Y 中最大化

                print( "The tag sequence is:", best_previous, end = " ")
                print( ". The probability of the tag sequence is:", prob_tagsequence if prob_tagsequence <=0 else math.log(prob_tagsequence))
        # 为结果排序
        best_previous_list = sorted(word_prob_dict.items(),
                            key = lambda item: float("-inf") if item[1] <= 0 else math.log(item[1]),
                            reverse = True)
        
    #     # 我们这会儿是倒着存的。因为好的在后面
    #     # 同理 这里也有倒过来
    #     # 回溯 最好的tag
    #     # 因为"START" "NNP" 中 "NNP" 总是能在第一个单词的 Y 中最大化

        if DEBUG:

            print( "\nThe sentence was:    ", end = " ")
            for w in sentence: print( w, end = " ")

            print( ".\nThe labeled tag sequence is:", end = " ")
            for l in labeled_tags: print(l, end = " ")
            print("\n" + "="*70)
            
        return best_previous_list
#----------------------------------------------
# -*- encoding=utf-8 -*-                      #
# __author__:'xiaojie'                        #
# CreateTime:                                 #
#       2019/5/7 13:47                       #
#                                             #
#               天下风云出我辈，                 #
#               一入江湖岁月催。                 #
#               皇图霸业谈笑中，                 #
#               不胜人生一场醉。                 #
#----------------------------------------------
# ACGAN(Auxiliary Classifier GAN)
# 组合的方法有很多，除了拼接外，还有相乘，相乘的话必须2个一样长
# ACGAN和CGAN真的很像，ACGAN中，标签c既传给D，又传给G，因此，不管是真实的X，还是生成的X_，经过判别器后
#   都要进行对抗学习和监督学习。
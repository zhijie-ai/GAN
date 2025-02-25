#----------------------------------------------
# -*- encoding=utf-8 -*-                      #
# __author__:'xiaojie'                        #
# CreateTime:                                 #
#       2019/5/14 20:33                       #
#                                             #
#               天下风云出我辈，                 #
#               一入江湖岁月催。                 #
#               皇图霸业谈笑中，                 #
#               不胜人生一场醉。                 #
#----------------------------------------------
import tensorflow as tf
from GAN.ACGAN.impl4.mnist import Mnist
from GAN.ACGAN.impl4.generator import generator
from GAN.ACGAN.impl4.discriminator import discriminator
from GAN.ACGAN.impl4.optimizer import optim
from GAN.ACGAN.impl4.queue_context import queue_context
import os
import sys

tf.logging.set_verbosity(0)

#
# hyper parameters
#

batch_size = 32  # batch size
cat_dim = 10  # total categorical factor
con_dim = 2  # total continuous factor
rand_dim = 38
num_epochs = 30
debug_max_steps = 1000
save_epoch = 5
max_epochs = 50

#
# inputs
#

# MNIST input tensor ( with QueueRunner )
data = Mnist(batch_size=batch_size, num_epochs=num_epochs)
num_batch_per_epoch = data.train.num_batch

# input images and labels
x = data.train.image
y = data.train.label

# labels for discriminator
y_real = tf.ones(batch_size)
y_fake = tf.zeros(batch_size)

# discriminator labels ( half 1s, half 0s )
y_disc = tf.concat(axis=0, values=[y, y * 0])

#
# create generator
#

# get random class number
if (int(tf.__version__.split(".")[1]) < 13 and int(tf.__version__.split(".")[0]) < 2):  ### tf version < 1.13
    z_cat = tf.multinomial(tf.ones((batch_size, cat_dim), dtype=tf.float32) / cat_dim, 1)
else:  ### tf versioin >= 1.13
    z_cat = tf.random.categorical(tf.ones((batch_size, cat_dim), dtype=tf.float32) / cat_dim, 1)

z_cat = tf.squeeze(z_cat, -1)
z_cat = tf.cast(z_cat, tf.int32)

# continuous latent variable
z_con = tf.random_normal((batch_size, con_dim))
z_rand = tf.random_normal((batch_size, rand_dim))

z = tf.concat(axis=1, values=[tf.one_hot(z_cat, depth=cat_dim), z_con, z_rand])

# generator network
gen = generator(z)

# add image summary
# tf.sg_summary_image(gen)
tf.summary.image('real', x)
tf.summary.image('fake', gen)

#
# discriminator
disc_real, cat_real, _ = discriminator(x)
disc_fake, cat_fake, con_fake = discriminator(gen)

# discriminator loss
loss_d_r = tf.reduce_mean(
    tf.nn.sigmoid_cross_entropy_with_logits(logits=disc_real, labels=y_real))
loss_d_f = tf.reduce_mean(
    tf.nn.sigmoid_cross_entropy_with_logits(logits=disc_fake, labels=y_fake))
loss_d = (loss_d_r + loss_d_f) / 2
print('loss_d', loss_d.get_shape())

# generator loss
loss_g = tf.reduce_mean(
    tf.nn.sigmoid_cross_entropy_with_logits(logits=disc_fake, labels=y_real))

# categorical factor loss
loss_c_r = tf.reduce_mean(
    tf.nn.sparse_softmax_cross_entropy_with_logits(logits=cat_real, labels=y))
loss_c_d = tf.reduce_mean(
    tf.nn.sparse_softmax_cross_entropy_with_logits(logits=cat_fake, labels=z_cat))
loss_c = (loss_c_r + loss_c_d) / 2
print('loss_c', loss_c.get_shape())
# continuous factor loss
loss_con = tf.reduce_mean(tf.square(con_fake - z_con))
print('loss_con', loss_con.get_shape())

train_disc, disc_global_step = optim(loss_d + loss_c + loss_con,
                                     lr=0.0001, optim='Adm', category='discriminator')
train_gen, gen_global_step = optim(loss_g + loss_c + loss_con,
                                   lr=0.001, optim='Adm', category='generator')
init = tf.global_variables_initializer()
saver = tf.train.Saver()
print(train_gen)

cur_epoch = 0
cur_step = 0

with tf.Session() as sess:
    sess.run(init)
    coord, threads = queue_context(sess)
    try:
        while not coord.should_stop():
            cur_step += 1
            dis_part = cur_step * 1.0 / num_batch_per_epoch
            dis_part = int(dis_part * 50)
            sys.stdout.write(
                "process bar ::|" + "<" * dis_part + '|' \
                + str(cur_step * 1.0 / num_batch_per_epoch * 100) + '%' + '\r')
            sys.stdout.flush()
            l_disc, _, l_d_step = sess.run([loss_d, train_disc, disc_global_step])
            l_gen, _, l_g_step = sess.run([loss_g, train_gen, gen_global_step])
            last_epoch = cur_epoch
            cur_epoch = l_d_step / num_batch_per_epoch
            if cur_epoch > max_epochs:
                break

            if cur_epoch > last_epoch:
                cur_step = 0
                print('cur epoch {0} update l_d step {1}, \
                    loss_disc {2}, loss_gen {3}'.format(cur_epoch,
                                                      l_d_step,
                                                      l_disc,
                                                      l_gen))
                if cur_epoch % save_epoch == 0:
                    # save
                    saver.save(sess, os.path.join('./checkpoint_dir', 'ac_gan'),
                               global_step=l_d_step)
    except tf.errors.OutOfRangeError:
        print('Train Finished')
    finally:
        coord.request_stop()
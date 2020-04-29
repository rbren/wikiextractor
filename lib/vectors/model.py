import tensorflow as tf
from .vectors import get_vectors
from .autoencoder import autoencoder

TRAINING_STEPS = 100000
PERCENT_TRAIN = .80
ENCODING_SIZE = 2

MODELS_DIR = './models'
LOAD_FROM_SAVED = False

def get_data(category):
    data = get_vectors(category)
    split_at = int(float(len(data)) * PERCENT_TRAIN)
    return data[:split_at], data[split_at:]

def run(category):
    train, test = get_data(category)
    print(len(train), len(test))

    x = tf.placeholder(tf.float32, shape=[None, len(train[0])], name="x")
    loss, output, latent = autoencoder(x, encoding_size=ENCODING_SIZE, cross_entropy=False)
    train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

    saver = tf.train.Saver()
    checkpoint_file = MODELS_DIR + "/" + category + "/model.ckpt"

    # Run the training loop
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        if LOAD_FROM_SAVED:
            saver.restore(sess, checkpoint_file)
        train_feed = {x: train}
        test_feed = {x: test}
        for step in range(int(TRAINING_STEPS + 1)):
            train_loss = sess.run([loss], feed_dict=train_feed)
            test_loss = sess.run([loss], feed_dict=test_feed)
            train_step.run(feed_dict=train_feed)
            if step % 100 == 0:
                print("at step %d, train %.5f, test %.5f" % (step, train_loss[0], test_loss[0]))

if __name__ == '__main__':
    run('20th-century_musicologists')

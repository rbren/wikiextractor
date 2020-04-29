import tensorflow as tf

HIDDEN_SIZE = 10

def weight_variable(shape, name):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial, name=name)

def bias_variable(shape, name):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial, name=name)

def fc_layer(previous, input_size, output_size, name):
    W = weight_variable([input_size, output_size], name + '_W')
    b = bias_variable([output_size], name + '_b')
    return tf.add(tf.matmul(previous, W), b, name=name)

def fc_layers(x, ret_size, layers, name, relu=True, pos=False):
    layer = x
    for i in range(len(layers) + 1):
        is_first = i == 0
        is_last = i == len(layers)
        in_size = x.get_shape().as_list()[1] if is_first else layers[i-1]
        out_size = ret_size if is_last else layers[i]
        layer = fc_layer(layer, in_size, out_size, name + "_" + str(i))
        if is_last and pos:
            layer = (tf.nn.tanh(layer) + 1.0) / 2.0
        elif is_last or not relu:
            layer = tf.nn.tanh(layer)
        else:
            layer = tf.nn.relu(layer)
    return layer

def encoder(x, encoding_size, layers=[HIDDEN_SIZE, HIDDEN_SIZE], name="Encoded"):
    enc = fc_layers(x, encoding_size, layers, "encoder")
    return tf.identity(enc, name=name)

def decoder(encoded, out_size, layers=[HIDDEN_SIZE, HIDDEN_SIZE]):
    dec = fc_layers(encoded, out_size, layers, "decoder")
    return tf.identity(dec, name="Decoded")

def autoencoder(x, encoding_size=2, cross_entropy=True):
    encoded = encoder(x, encoding_size, layers=[5, 5])
    decoded = decoder(encoded, x.get_shape().as_list()[1], layers=[5, 5])
    if cross_entropy:
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=x, logits=decoded), name="Loss")
    else:
        loss = tf.reduce_mean(tf.squared_difference(x, decoded), name="Loss")
    return loss, decoded, encoded


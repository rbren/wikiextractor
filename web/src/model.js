function newEncoder(opts) {
  const {originalDim, intermediateDim, latentDim} = opts;

  const inputs = tf.input({
    shape: [originalDim],
    name: 'encoder_input',
  });
  const hidden = tf.layers.dense({
    units: intermediateDim,
    activation: 'relu',
    name: 'encoder_hidden',
  }).apply(inputs);
  const encoding = tf.layers.dense({
    units: latentDim,
    activation: 'sigmoid',
    name: 'encoder_output',
  }).apply(hidden);
  return tf.model({
    inputs,
    outputs: [encoding],
    name: 'encoder',
  })
}

function newDecoder(opts) {
  const {originalDim, intermediateDim, latentDim} = opts;

  const inputs = tf.input({shape: [latentDim]});
  const hidden = tf.layers.dense({units: intermediateDim}).apply(inputs);
  const output = tf.layers.dense({units: originalDim}).apply(hidden);
  return tf.model({
    inputs,
    outputs: [output],
    name: 'decoder',
  });
}

function newAutoencoder(opts) {
  const encoder = newEncoder(opts);
  const decoder = newDecoder(opts);
  const encodings = encoder.apply(encoder.inputs);
  const decoded = decoder.apply(encodings);
  const ae = tf.model({
    inputs: encoder.inputs,
    outputs: [decoded, encodings],
    name: 'autoencoder',
  });
  return ae;
}

class ZLayer extends tf.layers.Layer {
  constructor(config) {
    super(config);
  }

  computeOutputShape(inputShape) {
    tf.util.assert(inputShape.length === 2 && Array.isArray(inputShape[0]),
        () => `Expected exactly 2 input shapes. But got: ${inputShape}`);
    return inputShape[0];
  }

  call(inputs, kwargs) {
    const [zMean, zLogVar] = inputs;
    const batch = zMean.shape[0];
    const dim = zMean.shape[1];

    const mean = 0;
    const std = 1.0;
    // sample epsilon = N(0, I)
    const epsilon = tf.randomNormal([batch, dim], mean, std);

    // z = z_mean + sqrt(var) * epsilon
    return zMean.add(zLogVar.mul(0.5).exp().mul(epsilon));
  }

  static get className() {
    return 'ZLayer';
  }
}
tf.serialization.registerClass(ZLayer);


function newEncoder(opts) {
  const {originalDim, intermediateDim, latentDim} = opts;

  const inputs = tf.input({shape: [originalDim], name: 'encoder_input'});
  const x = tf.layers.dense({units: intermediateDim, activation: 'relu'}) .apply(inputs);
  const zMean = tf.layers.dense({units: latentDim, name: 'z_mean'}).apply(x);
  const zLogVar =
      tf.layers.dense({units: latentDim, name: 'z_log_var'}).apply(x);

  const z =
      new ZLayer({name: 'z', outputShape: [latentDim]}).apply([zMean, zLogVar]);

  const enc = tf.model({
    inputs: inputs,
    outputs: [zMean, zLogVar, z],
    name: 'encoder',
  });
  return enc;
}

function newDecoder(opts) {
    const {originalDim, intermediateDim, latentDim} = opts;

  // The decoder model has a linear topology and hence could be constructed
  // with `tf.sequential()`. But we use the functional-model API (i.e.,
  // `tf.model()`) here nonetheless, for consistency with the encoder model
  // (see `encoder()` above).
  const input = tf.input({shape: [latentDim]});
  let y = tf.layers.dense({
    units: intermediateDim,
    activation: 'relu'
  }).apply(input);
  y = tf.layers.dense({
    units: originalDim,
    activation: 'sigmoid'
  }).apply(y);
  const dec = tf.model({inputs: input, outputs: [y]});

  // console.log('Decoder Summary');
  // dec.summary();
  return dec;
}

function newVAE(encoder, decoder) {
  const inputs = encoder.inputs;
  const [zMean, zLogVar, encoded] = encoder.apply(inputs);
  const decoderOutput = decoder.apply(encoded);
  const v = tf.model({
    inputs: inputs,
    outputs: [decoderOutput, zMean, zLogVar, encoded],
    name: 'vae_mlp',
  })

  return v;
}

function vaeLoss(inputs, outputs, fixedEncodings) {
  return tf.tidy(() => {
    const originalDim = inputs.shape[1];
    const decoderOutput = outputs[0];
    const zMean = outputs[1];
    const zLogVar = outputs[2];
    const encodings = outputs[3];
    fixedEncodings = fixedEncodings || encodings;

    const reconstructionLoss =
        tf.losses.meanSquaredError(inputs, decoderOutput).mul(originalDim);
    const encodingLoss =
        tf.losses.meanSquaredError(fixedEncodings, encodings).mul(originalDim);

    let klLoss = zLogVar.add(1).sub(zMean.square()).sub(zLogVar.exp());
    klLoss = klLoss.sum(-1).mul(-0.5);

    const baseLoss = reconstructionLoss.add(klLoss).mean();
    const encLoss = encodingLoss.sum();
    console.log('loss', baseLoss.dataSync(), encLoss.dataSync());
    return baseLoss.add(encLoss);
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

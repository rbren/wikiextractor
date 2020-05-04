const EPOCHS = 1000;
const HIDDEN_DIM = 10;
const ENCODING_DIM = 1;

function normalizeVector(vec) {
  return vec;
  return vec.map(v => {
    if (v === 0) {
      return -10;
    } else {
      return Math.max(-10, Math.log(v));
    }
  })
}

var app = new Vue({
  el: '#app',
  data() {
    window.app = this;
    return {
      vaeOpts: {},
      categories: null,
      category: null,
      articles: null,
      articlesSorted: null,
      article: null,
      tokens: null,
      weights: null,
      loading: false,
      encodings: null,
      step: 0,
      testLoss: 0.0,
      trainLoss: 0.0,
      query: '',
    };
  },
  beforeMount() {
    this.setCategories()
  },
  methods: {
    formatNum(n) {
      return Math.round(n * 10000) / 10000;
    },
    formatLoss(a, b) {
      return this.formatNum(Math.abs(a - b));
    },
    async setCategories() {
      const res = await axios.get('/api/categories');
      this.categories = res.data;
    },
    async setCategory(cat) {
      this.category = cat;
      this.loading = true;
      const res = await axios.get('/api/articles?category=' + this.category);
      this.articles = this.articlesSorted = res.data.articles;
      this.articles.forEach(a => a.vector = normalizeVector(a.vector));
      this.tokens = res.data.tokens;
      this.weights = res.data.weights;
      this.loading = false;
      this.setupTraining();
    },
    setArticle(a) {
      this.article = a;
    },
    setupTraining() {
      this.step = this.testLoss = this.trainLoss = 0;
      this.encodings = null;

      this.vaeOpts = {
        originalDim: this.articles[0].vector.length,
        intermediateDim: HIDDEN_DIM,
        latentDim: ENCODING_DIM,
      }
      this.encoder = newEncoder(this.vaeOpts);
      this.decoder = newDecoder(this.vaeOpts);
      this.vae = newVAE(this.encoder, this.decoder);
      this.optimizer = tf.train.adam();
    },
    startTraining() {
      this.training = true;
      this.trainBatch();
    },
    pauseTraining() {
      this.training = false;
    },
    trainBatch() {
      this.train(10);
      this.updateEncodings();
      window.draw(this.articles);
      if (!this.training) return;
      setTimeout(() => this.trainBatch(), 1000);
    },
    train(steps) {
      let finalLoss = 0.0;
      const {testSet, trainSet} = this.splitData();
      for (let step = 0; step < steps; step++) {
        this.step++;
        console.log('step', step);
        this.optimizer.minimize(() => {
          const outputs = this.vae.apply(trainSet);
          const loss = vaeLoss(trainSet, outputs, this.vaeOpts)
          if (step === steps - 1) {
            finalLoss = loss.dataSync()[0];
          }
          return loss;
        });
      }
      this.trainLoss = finalLoss;
      console.log("train loss", this.trainLoss);
      const outputs = this.vae.apply(testSet);
      const testLoss = vaeLoss(testSet, outputs, this.vaeOpts);
      this.testLoss = testLoss.dataSync()[0];
      console.log('test loss', this.testLoss);
    },
    splitData() {
      const splitIdx = Math.ceil(this.articles.length * .2);
      const data = this.articles.map(a => a.vector);
      const trainSet = tf.tensor(data.slice(0, splitIdx));
      const testSet = tf.tensor(data.slice(splitIdx, data.length));
      return {testSet, trainSet};
    },
    getAllData() {
      return tf.tensor(this.articles.map(a => a.vector));
    },
    updateEncodings() {
      let [decoded, mean, logvar, encoded] = this.vae.apply(this.getAllData());
      encoded = encoded.arraySync();
      decoded = decoded.arraySync();
      this.articles.forEach((art, idx) => {
        art.encoded = encoded[idx];
        art.decoded = decoded[idx];
      });
      this.articlesSorted = this.articles.map(a => a).sort((a1, a2) => {
        return a1.encoded[0] - a2.encoded[0];
      });
    },
    decode(encoding) {
      encoding = tf.tensor([encoding]);
      let decoded = this.decoder.apply(encoding);
      return decoded.arraySync()[0];
    },
  },
  computed: {
    tokensSorted() {
      let min = null;
      let max = null;
      this.articlesSorted.forEach(art => {
        if (min === null || art.encoded[0] < min) min = art.encoded[0];
        if (max === null || art.encoded[0] > max) max = art.encoded[0];
      })

      const a = this.decode([min]);
      const b = this.decode([max]);
      let diffs = this.tokens.map((token, idx) => {
        return {token, diff: a[idx] - b[idx]};
      });
      diffs = diffs.sort((d1, d2) => d2.diff - d1.diff);
      return diffs.map(t => t.token);
    },
    leftTokens() {
      return (this.tokensSorted || []).slice(0, 10);
    },
    rightTokens() {
      let toks = this.tokensSorted || [];
      return toks.slice(toks.length - 10, toks.length);
    },
  },
})


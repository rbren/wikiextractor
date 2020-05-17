const EPOCHS = 1000;
const HIDDEN_DIM = 10;
const ENCODING_DIM = 1;
const TRAIN_SIZE = 0.8;

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
      queryRaw: '',
    };
  },
  created() {
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
      this.categories.forEach(cat => {
        cat.displayName = cat.name.replace(/_/g, ' ');
        cat.queryName = cat.displayName.toLowerCase();
      })
    },
    async setCategory(cat) {
      this.category = cat;
      this.loading = true;
      const res = await axios.get('/api/articles?category=' + this.category.name);
      this.articles = this.articlesSorted = res.data.articles;
      this.articles.forEach(a => {
        a.displayTitle = a.title.replace(/_/g, '');
        a.vector = normalizeVector(a.vector)
      });
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
      this.trainBatch();
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
          const inputs = this.getTensor(trainSet);
          const outputs = this.vae.apply(inputs);
          const encodings = outputs[3].arraySync();
          const fixedEncodings = tf.tensor(trainSet.map((t, idx) => t.fixed || encodings[idx]));
          const loss = vaeLoss(inputs, outputs, fixedEncodings);
          if (step === steps - 1) {
            finalLoss = loss.dataSync()[0];
          }
          return loss;
        });
      }
      this.trainLoss = finalLoss;
      const testInputs = this.getTensor(testSet);
      const outputs = this.vae.apply(testInputs);
      const testLoss = vaeLoss(testInputs, outputs);
      this.testLoss = testLoss.dataSync()[0];
    },
    splitData() {
      const fixedPoints = this.articles.filter(a => a.fixed);
      const unfixedPoints = this.articles.filter(a => !a.fixed);
      const splitIdx = Math.ceil(this.articles.length * TRAIN_SIZE) - fixedPoints.length;
      const trainSet = fixedPoints.concat(unfixedPoints.slice(0, splitIdx));
      const testSet = unfixedPoints.slice(splitIdx, unfixedPoints.length);
      console.log('f/uf', fixedPoints.length, unfixedPoints.length);
      console.log('s/r', testSet.length, trainSet.length);
      return {testSet, trainSet};
    },
    getTensor(articles) {
      return tf.tensor(articles.map(a => a.vector));
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
    query: function() {
      return this.queryRaw.toLowerCase();
    },
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


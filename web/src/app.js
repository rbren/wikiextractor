const EPOCHS = 1000;
const HIDDEN_DIM = 10;
const ENCODING_DIM = 2;

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
      categories: null,
      category: null,
      articles: null,
      article: null,
      tokens: null,
      weights: null,
      loading: false,
      inputs: null,
      encodings: null,
      loss: 0.0,
      query: '',
    };
  },
  beforeMount() {
    this.setCategories()
  },
  methods: {
    async setCategories() {
      const res = await axios.get('/api/categories');
      this.categories = res.data;
    },
    async setCategory(cat) {
      this.category = cat;
      this.loading = true;
      const res = await axios.get('/api/articles?category=' + this.category);
      this.articles = res.data.articles;
      this.articles.forEach(a => a.vector = normalizeVector(a.vector));
      this.tokens = res.data.tokens;
      this.weights = res.data.weights;
      this.inputs = tf.tensor(this.articles.map(a => [a.vector]));
      this.loading = false;
      this.setupTraining();
    },
    setArticle(a) {
      this.article = a;
    },
    setupTraining() {
      this.loss = 0.0;
      this.encodings = null;
      this.autoencoder = newAutoencoder({
        originalDim: this.articles[0].vector.length,
        intermediateDim: HIDDEN_DIM,
        latentDim: ENCODING_DIM,
      });
      this.optimizer = tf.train.adam();
    },
    train(steps) {
      let finalLoss = 0.0;
      for (let step = 0; step < steps; step++) {
        console.log('step', step);
        this.optimizer.minimize(() => {
          const [decoded, encoded] = this.autoencoder.apply(this.inputs);
          const loss = tf.losses.meanSquaredError(this.inputs, decoded);
          if (step === steps - 1) {
            finalLoss = loss.dataSync()[0];
            console.log('set loss', finalLoss);
          }
          return loss;
        });
      }
      this.loss = finalLoss;
      console.log('loss', this.loss);
      this.updateEncodings();
    },
    updateEncodings() {
      let [decoded, encoded] = this.autoencoder.apply(this.inputs);
      encoded = encoded.arraySync();
      decoded = decoded.arraySync();
      this.articles.forEach((art, idx) => {
        art.encoded = encoded[idx][0];
        art.decoded = decoded[idx][0];
      });
      //math.reshape(this.encodings, [this.articles.length, ENCODING_DIM]);
      //this.encodings = math.reshape(encoded.dataSync(), [this.articles.length, ENCODING_DIM])
    }
  },
})


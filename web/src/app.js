
var app = new Vue({
  el: '#app',
  data: {
    categories: null,
    category: null,
    articles: null,
    loading: false,
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
      this.articles = res.data;
      this.loading = false;
    }
  },
})


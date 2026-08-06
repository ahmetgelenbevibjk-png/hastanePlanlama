import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router'; // router dosya yolunuz

const app = createApp(App);

app.use(createPinia());
app.use(router); // Router'ı uygulamaya kaydettiğinizden emin olun

app.mount('#app');
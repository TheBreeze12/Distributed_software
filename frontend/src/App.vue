<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { addProduct, createOrder, getMe, getProducts, login, register } from "./api";

const token = ref(localStorage.getItem("access_token") || "");
const loading = reactive({
  login: false,
  register: false,
  products: false,
  addProduct: false,
  order: false
});

const message = reactive({
  type: "info",
  text: "欢迎使用秒杀商城前端。请先登录。"
});

const user = ref(null);
const products = ref([]);

const loginForm = reactive({
  username: "",
  password: ""
});

const registerForm = reactive({
  username: "",
  password: "",
  password_confirm: "",
  email: ""
});

const productForm = reactive({
  name: "",
  price: ""
});

const orderForm = reactive({
  p_name: "",
  quantity: 1
});

const isAuthed = computed(() => Boolean(token.value));

function setMessage(type, text) {
  message.type = type;
  message.text = text;
}

function normalizeProducts(payload) {
  if (Array.isArray(payload?.data)) return payload.data;
  if (payload?.data && typeof payload.data === "object") return [payload.data];
  return [];
}

async function fetchProducts() {
  loading.products = true;
  try {
    const res = await getProducts();
    products.value = normalizeProducts(res);
  } catch (error) {
    setMessage("error", `获取商品失败：${error.message}`);
  } finally {
    loading.products = false;
  }
}

async function fetchMe() {
  if (!token.value) return;
  try {
    user.value = await getMe(token.value);
  } catch (error) {
    token.value = "";
    localStorage.removeItem("access_token");
    user.value = null;
    setMessage("error", `登录态失效：${error.message}`);
  }
}

async function submitLogin() {
  loading.login = true;
  try {
    const res = await login(loginForm);
    token.value = res.access_token;
    localStorage.setItem("access_token", res.access_token);
    setMessage("success", "登录成功，已同步用户信息。");
    await fetchMe();
  } catch (error) {
    setMessage("error", `登录失败：${error.message}`);
  } finally {
    loading.login = false;
  }
}

async function submitRegister() {
  loading.register = true;
  try {
    await register(registerForm);
    setMessage("success", "注册成功，请使用新账号登录。");
  } catch (error) {
    setMessage("error", `注册失败：${error.message}`);
  } finally {
    loading.register = false;
  }
}

async function submitAddProduct() {
  loading.addProduct = true;
  try {
    await addProduct(
      {
        name: productForm.name,
        price: Number(productForm.price)
      },
      token.value
    );
    setMessage("success", "新增商品成功。");
    productForm.name = "";
    productForm.price = "";
    await fetchProducts();
  } catch (error) {
    setMessage("error", `新增商品失败：${error.message}`);
  } finally {
    loading.addProduct = false;
  }
}

async function submitOrder() {
  loading.order = true;
  try {
    const res = await createOrder(
      {
        p_name: orderForm.p_name,
        quantity: Number(orderForm.quantity)
      },
      token.value
    );
    setMessage("success", `下单成功：${JSON.stringify(res)}`);
  } catch (error) {
    setMessage("error", `下单失败：${error.message}`);
  } finally {
    loading.order = false;
  }
}

function useProduct(product) {
  orderForm.p_name = product.name;
}

function logout() {
  token.value = "";
  localStorage.removeItem("access_token");
  user.value = null;
  setMessage("info", "已退出登录。");
}

onMounted(async () => {
  await fetchProducts();
  if (token.value) {
    await fetchMe();
  }
});
</script>

<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>秒杀商城 · Vue 前端</h1>
        <p>对接后端接口：用户认证、商品管理、下单流程</p>
      </div>
      <button v-if="isAuthed" class="ghost-btn" @click="logout">退出登录</button>
    </header>

    <p class="notice" :class="`notice-${message.type}`" aria-live="polite">{{ message.text }}</p>

    <main class="grid">
      <section class="card">
        <h2>登录</h2>
        <form class="form" @submit.prevent="submitLogin">
          <label>
            用户名
            <input v-model.trim="loginForm.username" type="text" required minlength="3" />
          </label>
          <label>
            密码
            <input v-model.trim="loginForm.password" type="password" required minlength="3" />
          </label>
          <button :disabled="loading.login" type="submit">
            {{ loading.login ? "登录中..." : "立即登录" }}
          </button>
        </form>
      </section>

      <section class="card">
        <h2>注册</h2>
        <form class="form" @submit.prevent="submitRegister">
          <label>
            用户名
            <input v-model.trim="registerForm.username" type="text" required minlength="3" />
          </label>
          <label>
            邮箱
            <input v-model.trim="registerForm.email" type="email" required />
          </label>
          <label>
            密码
            <input v-model.trim="registerForm.password" type="password" required minlength="3" />
          </label>
          <label>
            确认密码
            <input
              v-model.trim="registerForm.password_confirm"
              type="password"
              required
              minlength="3"
            />
          </label>
          <button :disabled="loading.register" type="submit">
            {{ loading.register ? "注册中..." : "创建账号" }}
          </button>
        </form>
      </section>

      <section class="card wide">
        <div class="title-row">
          <h2>商品列表</h2>
          <button class="ghost-btn" :disabled="loading.products" @click="fetchProducts">
            {{ loading.products ? "刷新中..." : "刷新" }}
          </button>
        </div>
        <ul class="list" v-if="products.length">
          <li class="item" v-for="item in products" :key="item.id">
            <div>
              <h3>{{ item.name }}</h3>
              <p>商品ID：{{ item.id }}</p>
            </div>
            <div class="right">
              <strong>¥ {{ Number(item.price).toFixed(2) }}</strong>
              <button class="small-btn" @click="useProduct(item)">选择下单</button>
            </div>
          </li>
        </ul>
        <p v-else class="empty">暂无商品，请先新增商品。</p>
      </section>

      <section class="card">
        <h2>新增商品</h2>
        <form class="form" @submit.prevent="submitAddProduct">
          <label>
            商品名
            <input v-model.trim="productForm.name" type="text" required />
          </label>
          <label>
            单价
            <input v-model="productForm.price" type="number" step="0.01" min="0.01" required />
          </label>
          <button :disabled="loading.addProduct" type="submit">
            {{ loading.addProduct ? "提交中..." : "新增商品" }}
          </button>
        </form>
      </section>

      <section class="card">
        <h2>创建订单</h2>
        <form class="form" @submit.prevent="submitOrder">
          <label>
            商品名
            <input v-model.trim="orderForm.p_name" type="text" required />
          </label>
          <label>
            数量
            <input v-model="orderForm.quantity" type="number" min="1" required />
          </label>
          <button :disabled="loading.order || !isAuthed" type="submit">
            {{ loading.order ? "下单中..." : "提交订单" }}
          </button>
        </form>
        <p class="tip">下单接口需要登录态，未登录时按钮将禁用。</p>
      </section>

      <section class="card">
        <h2>当前用户</h2>
        <div v-if="user" class="profile">
          <p><span>ID</span> {{ user.id }}</p>
          <p><span>用户名</span> {{ user.username }}</p>
          <p><span>邮箱</span> {{ user.email }}</p>
        </div>
        <p v-else class="empty">尚未获取用户信息。</p>
      </section>
    </main>
  </div>
</template>

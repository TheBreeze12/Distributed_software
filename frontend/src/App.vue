<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  addProduct,
  cancelOrder,
  changePassword,
  changeUserInfo,
  confirmOrder,
  createOrder,
  getInventory,
  getMe,
  getProducts,
  getUserOrders,
  login,
  register,
} from "./api";

const token = ref(localStorage.getItem("access_token") || "");
const loading = reactive({
  login: false,
  register: false,
  products: false,
  addProduct: false,
  order: false,
  changeUser: false,
  changePassword: false,
  confirmOrder: false,
  cancelOrder: false,
  getInventory: false,
  getUserOrders: false,
});

const message = reactive({
  type: "info",
  text: "欢迎使用秒杀商城前端。请先登录。",
});

const user = ref(null);
const products = ref([]);
const orders = ref([]);

const loginForm = reactive({
  username: "",
  password: "",
});

const registerForm = reactive({
  username: "",
  password: "",
  password_confirm: "",
  email: "",
});

const productForm = reactive({
  name: "",
  price: "",
});

const orderForm = reactive({
  p_name: "",
  quantity: 1,
});

const changeUserForm = reactive({
  username: "",
  email: "",
});

const changePasswordForm = reactive({
  password_old: "",
  password_new: "",
});

const confirmOrderForm = reactive({
  order_id: "",
});

const cancelOrderForm = reactive({
  order_id: "",
});

const checkInventoryForm = reactive({
  product_id: "",
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
        price: Number(productForm.price),
      },
      token.value,
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
        quantity: Number(orderForm.quantity),
      },
      token.value,
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

async function submitChangeUser() {
  loading.changeUser = true;
  try {
    const payload = {};
    if (changeUserForm.username.trim()) {
      payload.username = changeUserForm.username.trim();
    }
    if (changeUserForm.email.trim()) {
      payload.email = changeUserForm.email.trim();
    }
    if (Object.keys(payload).length === 0) {
      setMessage("warning", "请至少输入一个要修改的字段。");
      loading.changeUser = false;
      return;
    }
    const res = await changeUserInfo(payload, token.value);
    user.value = res;
    changeUserForm.username = "";
    changeUserForm.email = "";
    setMessage("success", "用户信息修改成功。");
  } catch (error) {
    setMessage("error", `修改用户信息失败：${error.message}`);
  } finally {
    loading.changeUser = false;
  }
}

async function submitChangePassword() {
  loading.changePassword = true;
  try {
    if (!changePasswordForm.password_old.trim()) {
      setMessage("warning", "请输入原密码。");
      loading.changePassword = false;
      return;
    }
    if (!changePasswordForm.password_new.trim()) {
      setMessage("warning", "请输入新密码。");
      loading.changePassword = false;
      return;
    }
    const res = await changePassword(
      {
        password_old: changePasswordForm.password_old,
        password_new: changePasswordForm.password_new,
      },
      token.value,
    );
    changePasswordForm.password_old = "";
    changePasswordForm.password_new = "";
    setMessage("success", "密码修改成功，请重新登录。");
  } catch (error) {
    setMessage("error", `修改密码失败：${error.message}`);
  } finally {
    loading.changePassword = false;
  }
}

async function submitConfirmOrder() {
  loading.confirmOrder = true;
  try {
    if (!confirmOrderForm.order_id.trim()) {
      setMessage("warning", "请输入订单ID。");
      loading.confirmOrder = false;
      return;
    }
    const res = await confirmOrder(confirmOrderForm.order_id, token.value);
    confirmOrderForm.order_id = "";
    setMessage("success", "订单确认成功，已标记为已支付。");
  } catch (error) {
    setMessage("error", `确认订单失败：${error.message}`);
  } finally {
    loading.confirmOrder = false;
  }
}

async function submitCancelOrder() {
  loading.cancelOrder = true;
  try {
    if (!cancelOrderForm.order_id.trim()) {
      setMessage("warning", "请输入订单ID。");
      loading.cancelOrder = false;
      return;
    }
    const res = await cancelOrder(cancelOrderForm.order_id, token.value);
    cancelOrderForm.order_id = "";
    setMessage("success", "订单已取消，库存已回滚。");
  } catch (error) {
    setMessage("error", `取消订单失败：${error.message}`);
  } finally {
    loading.cancelOrder = false;
  }
}

async function submitCheckInventory() {
  loading.getInventory = true;
  try {
    if (!checkInventoryForm.product_id.trim()) {
      setMessage("warning", "请输入商品ID。");
      loading.getInventory = false;
      return;
    }
    const res = await getInventory(checkInventoryForm.product_id, token.value);
    const inv = res.data;
    setMessage(
      "success",
      `商品${checkInventoryForm.product_id}库存查询：总库存${inv.total_stock}，可用${inv.available_stock}，已锁定${inv.locked_stock}`,
    );
    checkInventoryForm.product_id = "";
  } catch (error) {
    setMessage("error", `查询库存失败：${error.message}`);
  } finally {
    loading.getInventory = false;
  }
}

async function fetchUserOrders() {
  loading.getUserOrders = true;
  try {
    const res = await getUserOrders(token.value);
    orders.value = Array.isArray(res?.data) ? res.data : [];
    setMessage("success", `已加载 ${orders.value.length} 条订单。`);
  } catch (error) {
    setMessage("error", `获取订单失败：${error.message}`);
    orders.value = [];
  } finally {
    loading.getUserOrders = false;
  }
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
      <button v-if="isAuthed" class="ghost-btn" @click="logout">
        退出登录
      </button>
    </header>

    <p class="notice" :class="`notice-${message.type}`" aria-live="polite">
      {{ message.text }}
    </p>

    <main class="grid">
      <section class="card">
        <h2>登录</h2>
        <form class="form" @submit.prevent="submitLogin">
          <label>
            用户名
            <input
              v-model.trim="loginForm.username"
              type="text"
              required
              minlength="3"
            />
          </label>
          <label>
            密码
            <input
              v-model.trim="loginForm.password"
              type="password"
              required
              minlength="3"
            />
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
            <input
              v-model.trim="registerForm.username"
              type="text"
              required
              minlength="3"
            />
          </label>
          <label>
            邮箱
            <input v-model.trim="registerForm.email" type="email" required />
          </label>
          <label>
            密码
            <input
              v-model.trim="registerForm.password"
              type="password"
              required
              minlength="3"
            />
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
          <button
            class="ghost-btn"
            :disabled="loading.products"
            @click="fetchProducts"
          >
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
              <button class="small-btn" @click="useProduct(item)">
                选择下单
              </button>
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
            <input
              v-model="productForm.price"
              type="number"
              step="0.01"
              min="0.01"
              required
            />
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
            <input
              v-model="orderForm.quantity"
              type="number"
              min="1"
              required
            />
          </label>
          <button :disabled="loading.order || !isAuthed" type="submit">
            {{ loading.order ? "下单中..." : "提交订单" }}
          </button>
        </form>
        <p class="tip">下单接口需要登录态，未登录时按钮将禁用。</p>
      </section>

      <section class="card">
        <h2>修改用户信息</h2>
        <form class="form" @submit.prevent="submitChangeUser">
          <label>
            新用户名（留空则不修改）
            <input
              v-model.trim="changeUserForm.username"
              type="text"
              minlength="3"
            />
          </label>
          <label>
            新邮箱（留空则不修改）
            <input v-model.trim="changeUserForm.email" type="email" />
          </label>
          <button :disabled="loading.changeUser || !isAuthed" type="submit">
            {{ loading.changeUser ? "修改中..." : "修改信息" }}
          </button>
        </form>
        <p class="tip">需要登录态，至少输入一个字段。</p>
      </section>

      <section class="card">
        <h2>修改密码</h2>
        <form class="form" @submit.prevent="submitChangePassword">
          <label>
            原密码
            <input
              v-model="changePasswordForm.password_old"
              type="password"
              required
            />
          </label>
          <label>
            新密码
            <input
              v-model="changePasswordForm.password_new"
              type="password"
              required
            />
          </label>
          <button :disabled="loading.changePassword || !isAuthed" type="submit">
            {{ loading.changePassword ? "修改中..." : "修改密码" }}
          </button>
        </form>
        <p class="tip">需要登录态，修改成功后请重新登录。</p>
      </section>

      <section class="card">
        <h2>确认订单支付</h2>
        <form class="form" @submit.prevent="submitConfirmOrder">
          <label>
            订单ID
            <input
              v-model.trim="confirmOrderForm.order_id"
              type="text"
              placeholder="输入要确认的订单ID"
              required
            />
          </label>
          <button :disabled="loading.confirmOrder || !isAuthed" type="submit">
            {{ loading.confirmOrder ? "确认中..." : "确认订单已支付" }}
          </button>
        </form>
        <p class="tip">将订单状态从待支付（0）改为已支付（1），需要登录态。</p>
      </section>

      <section class="card">
        <h2>取消订单</h2>
        <form class="form" @submit.prevent="submitCancelOrder">
          <label>
            订单ID
            <input
              v-model.trim="cancelOrderForm.order_id"
              type="text"
              placeholder="输入要取消的订单ID"
              required
            />
          </label>
          <button :disabled="loading.cancelOrder || !isAuthed" type="submit">
            {{ loading.cancelOrder ? "取消中..." : "取消订单" }}
          </button>
        </form>
        <p class="tip">
          将订单状态改为已取消（2），库存会自动回滚，需要登录态。
        </p>
      </section>

      <section class="card">
        <h2>查询商品库存</h2>
        <form class="form" @submit.prevent="submitCheckInventory">
          <label>
            商品ID
            <input
              v-model.trim="checkInventoryForm.product_id"
              type="text"
              placeholder="输入商品ID"
              required
            />
          </label>
          <button :disabled="loading.getInventory || !isAuthed" type="submit">
            {{ loading.getInventory ? "查询中..." : "查询库存" }}
          </button>
        </form>
        <p class="tip">
          查询商品的库存状态：总库存、可用库存、已锁定库存，需要登录态。
        </p>
      </section>

      <section class="card wide">
        <div class="title-row">
          <h2>我的订单</h2>
          <button
            class="ghost-btn"
            :disabled="loading.getUserOrders || !isAuthed"
            @click="fetchUserOrders"
          >
            {{
              loading.getUserOrders
                ? "加载中..."
                : isAuthed
                  ? "刷新订单"
                  : "请先登录"
            }}
          </button>
        </div>
        <ul class="list" v-if="orders.length">
          <li class="item" v-for="item in orders" :key="item.id">
            <div>
              <h3>订单 #{{ item.id }}</h3>
              <p>商品ID：{{ item.p_id }} | 数量：{{ item.quantity }}</p>
              <p>
                状态：
                <span
                  :class="{
                    'status-0': item.status === 0,
                    'status-1': item.status === 1,
                    'status-2': item.status === 2,
                  }"
                >
                  {{
                    item.status === 0
                      ? "待支付"
                      : item.status === 1
                        ? "已支付"
                        : item.status === 2
                          ? "已取消"
                          : "未知"
                  }}
                </span>
              </p>
            </div>
            <div class="right">
              <strong>¥ {{ Number(item.order_amount).toFixed(2) }}</strong>
            </div>
          </li>
        </ul>
        <p v-else class="empty">
          {{
            isAuthed
              ? "暂无订单，点击刷新按钮加载订单列表。"
              : "请先登录查看订单。"
          }}
        </p>
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

const jsonHeaders = {
  "Content-Type": "application/json"
};

function withAuth(token) {
  if (!token) {
    return jsonHeaders;
  }
  return {
    ...jsonHeaders,
    Authorization: `Bearer ${token}`
  };
}

async function parseJsonResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data?.detail || data?.msg || "请求失败";
    throw new Error(detail);
  }
  return data;
}

export async function login(payload) {
  const response = await fetch("/api/v1/users/login", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify(payload)
  });
  return parseJsonResponse(response);
}

export async function register(payload) {
  const response = await fetch("/api/v1/users/register", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify(payload)
  });
  return parseJsonResponse(response);
}

export async function getMe(token) {
  const response = await fetch("/api/v1/users/me", {
    method: "GET",
    headers: withAuth(token)
  });
  return parseJsonResponse(response);
}

export async function getProducts() {
  const response = await fetch("/api/v1/products/", {
    method: "GET"
  });
  return parseJsonResponse(response);
}

export async function addProduct(payload, token) {
  const response = await fetch("/api/v1/products/", {
    method: "POST",
    headers: withAuth(token),
    body: JSON.stringify(payload)
  });
  return parseJsonResponse(response);
}

export async function createOrder(payload, token) {
  const response = await fetch("/api/1/orders/create", {
    method: "POST",
    headers: withAuth(token),
    body: JSON.stringify(payload)
  });
  return parseJsonResponse(response);
}

const API = "https://first-back-end-g799.onrender.com/pedidos";

// Utilitário para criar cards elegantes
function card(titulo, conteudo) {
  return `
    <div style="
      border: 1px solid #ccc;
      padding: 5px;
      width: 30%;
      height: auto;
      wrap-content: center;
      margin-top: 10px;
      background: #fafafa;
      border-radius: 6px;
    ">
      <h3>${titulo}</h3>
      <div>${conteudo}</div>
    </div>
  `;
}

// -----------------------------
// 1. Criar Pedido
// -----------------------------
async function criarPedido() {
  const nome = document.getElementById("nome").value;
  const produto = document.getElementById("produto").value.split(",").map(x => x.trim());
  const quantidade = parseInt(document.getElementById("quantidade").value);
  const valor = parseFloat(document.getElementById("valor").value.replace(",", "."));
  const adicionais = document.getElementById("adicionais").value.split(",").map(x => x.trim());

  const pedido = { nome, produto, quantidade, valor, adicionais };

  const resp = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(pedido)
  });

  const data = await resp.json();

  document.getElementById("respCriar").innerHTML = card(
    "Pedido Criado",
  );
}

// -----------------------------
// 2. Listar todos
// -----------------------------
async function listarPedidos() {
  const resp = await fetch(API);
  const lista = await resp.json();

  let html = "";

  lista.forEach(p => {
    html += card(
      `Pedido #${p.id}`,
      `
        <b>Nome:</b> ${p.nome}<br>
        <b>Produto:</b> ${p.produto.join(", ")}<br>
        <b>Quantidade:</b> ${p.quantidade}<br>
        <b>Valor:</b> R$ ${p.valor.toFixed(2)}<br>
        <b>Status:</b> ${p.status}
      `
    );
  });

  document.getElementById("respListar").innerHTML = html;
}

// -----------------------------
// 3. Buscar por ID
// -----------------------------
async function buscarPorId() {
  const id = document.getElementById("buscarId").value;

  const resp = await fetch(`${API}/${id}`);
  const data = await resp.json();

  document.getElementById("respBuscar").innerHTML = card(
    `Pedido #${data.id}`,
    `
      <b>Nome:</b> ${data.nome}<br>
      <b>Produto:</b> ${data.produto.join(", ")}<br>
      <b>Quantidade:</b> ${data.quantidade}<br>
      <b>Valor:</b> R$ ${data.valor.toFixed(2)}<br>
      <b>Status:</b> ${data.status}
    `
  );
}

// -----------------------------
// 4. Atualizar Status
// -----------------------------
async function atualizarStatus() {
  const id = document.getElementById("statusId").value;
  const novoStatus = document.getElementById("novoStatus").value;

  const resp = await fetch(`${API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: novoStatus })
  });

  const data = await resp.json();

  document.getElementById("respStatus").innerHTML = card(
    "Status Atualizado",
    `<b>Mensagem:</b> ${data.msg}`
  );
}

// -----------------------------
// 5. Apagar Pedido
// -----------------------------
async function apagarPedido() {
  const id = document.getElementById("deleteId").value;

  const resp = await fetch(`${API}/${id}`, { method: "DELETE" });
  const data = await resp.json();

  document.getElementById("respDelete").innerHTML = card(
    "Pedido Removido",
    `
      <b>ID:</b> ${data.pedido.id}<br>
      <b>Nome:</b> ${data.pedido.nome}<br>
      <b>Status:</b> ${data.msg}
    `
  );
}

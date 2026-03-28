const resultText = document.getElementById("resultText");
const pingButton = document.getElementById("pingButton");

pingButton.addEventListener("click", () => {
  const now = new Date().toLocaleString();
  resultText.textContent = `静态 JS 执行成功，时间: ${now}`;
});

import "@/css/glomar.css";
import { renderLoginChart } from "./glomar_login_chart";

document.addEventListener("DOMContentLoaded", function () {
  const el = document.getElementById("login-chart-container");
  if (el) renderLoginChart(el);
});

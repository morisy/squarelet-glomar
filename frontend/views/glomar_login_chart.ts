const COLORS = [
  "#4a90d9", // blue
  "#e6854a", // orange
  "#5bb576", // green
  "#d94a6b", // red
  "#9b59b6", // purple
  "#f5c242", // yellow
  "#3cc7c7", // teal
];

interface ChartData {
  labels: string[];
  series: Record<string, number[]>;
}

export function renderLoginChart(container: HTMLElement) {
  const raw = container.getAttribute("data-chart");
  if (!raw) return;
  const data: ChartData = JSON.parse(raw);
  const services = Object.keys(data.series);
  if (services.length === 0) {
    container.innerHTML =
      '<p class="empty">No service logins recorded.</p>';
    return;
  }

  const numMonths = data.labels.length;

  // Compute stacked totals per month
  const stackedTotals: number[][] = [];
  for (let s = 0; s < services.length; s++) {
    stackedTotals.push([]);
    for (let m = 0; m < numMonths; m++) {
      const prev = s > 0 ? stackedTotals[s - 1][m] : 0;
      stackedTotals[s].push(prev + data.series[services[s]][m]);
    }
  }

  const maxVal =
    Math.max(...stackedTotals[services.length - 1].map((v) => v)) || 1;

  // SVG dimensions
  const W = 600;
  const H = 240;
  const PAD_L = 36;
  const PAD_R = 12;
  const PAD_T = 12;
  const PAD_B = 28;
  const chartW = W - PAD_L - PAD_R;
  const chartH = H - PAD_T - PAD_B;

  function x(i: number): number {
    return PAD_L + (i / (numMonths - 1)) * chartW;
  }
  function y(val: number): number {
    return PAD_T + chartH - (val / maxVal) * chartH;
  }

  // Create wrapper for positioning the tooltip
  const wrapper = document.createElement("div");
  wrapper.className = "crm-login-chart-wrapper";

  // Build SVG element via DOM so events work properly
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("class", "crm-login-chart");
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

  // Grid lines
  const gridLines = 4;
  for (let g = 0; g <= gridLines; g++) {
    const val = (maxVal / gridLines) * g;
    const yPos = y(val);
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", String(PAD_L));
    line.setAttribute("y1", String(yPos));
    line.setAttribute("x2", String(W - PAD_R));
    line.setAttribute("y2", String(yPos));
    line.setAttribute("stroke", "#eef1f3");
    line.setAttribute("stroke-width", "1");
    svg.appendChild(line);

    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", String(PAD_L - 6));
    label.setAttribute("y", String(yPos + 3));
    label.setAttribute("text-anchor", "end");
    label.setAttribute("class", "crm-login-chart-axis");
    label.textContent = String(Math.round(val));
    svg.appendChild(label);
  }

  // X-axis labels
  for (let m = 0; m < numMonths; m++) {
    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", String(x(m)));
    label.setAttribute("y", String(H - 6));
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("class", "crm-login-chart-axis");
    label.textContent = data.labels[m];
    svg.appendChild(label);
  }

  // Stacked areas (render bottom service first so it's behind)
  for (let s = 0; s < services.length; s++) {
    const color = COLORS[s % COLORS.length];
    const top = stackedTotals[s];
    const bottom =
      s > 0 ? stackedTotals[s - 1] : new Array(numMonths).fill(0);

    let pathD = `M ${x(0)} ${y(top[0])}`;
    for (let m = 1; m < numMonths; m++) {
      pathD += ` L ${x(m)} ${y(top[m])}`;
    }
    for (let m = numMonths - 1; m >= 0; m--) {
      pathD += ` L ${x(m)} ${y(bottom[m])}`;
    }
    pathD += " Z";

    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", pathD);
    path.setAttribute("fill", color);
    path.setAttribute("fill-opacity", "0.6");
    path.setAttribute("stroke", color);
    path.setAttribute("stroke-width", "1.5");
    svg.appendChild(path);
  }

  // Tooltip element
  const tooltip = document.createElement("div");
  tooltip.className = "crm-login-tooltip";
  tooltip.style.display = "none";

  // Invisible wider hit-area columns for each month
  const colWidth = chartW / numMonths;
  for (let m = 0; m < numMonths; m++) {
    const hitArea = document.createElementNS(svgNS, "rect");
    hitArea.setAttribute("x", String(x(m) - colWidth / 2));
    hitArea.setAttribute("y", String(PAD_T));
    hitArea.setAttribute("width", String(colWidth));
    hitArea.setAttribute("height", String(chartH));
    hitArea.setAttribute("fill", "transparent");
    hitArea.style.cursor = "pointer";

    // Build tooltip content for this month
    const monthLabel = data.labels[m];
    const lines: string[] = [`<strong>${monthLabel}</strong>`];
    let monthTotal = 0;
    for (let s = 0; s < services.length; s++) {
      const val = data.series[services[s]][m];
      monthTotal += val;
      const color = COLORS[s % COLORS.length];
      lines.push(
        `<span class="crm-login-tooltip-row"><span class="crm-login-legend-swatch" style="background:${color}"></span>${services[s]}: ${val}</span>`
      );
    }
    lines.push(
      `<span class="crm-login-tooltip-total">Total: ${monthTotal}</span>`
    );
    const tooltipHTML = lines.join("");

    hitArea.addEventListener("mouseenter", (e) => {
      tooltip.innerHTML = tooltipHTML;
      tooltip.style.display = "block";
      // Position relative to the wrapper
      const rect = wrapper.getBoundingClientRect();
      const svgRect = svg.getBoundingClientRect();
      const svgScale = svgRect.width / W;
      const tipX = svgRect.left - rect.left + x(m) * svgScale;
      tooltip.style.left = tipX + "px";
      tooltip.style.top = svgRect.top - rect.top + PAD_T * svgScale - 4 + "px";
    });

    hitArea.addEventListener("mouseleave", () => {
      tooltip.style.display = "none";
    });

    svg.appendChild(hitArea);
  }

  // Dots on top of areas (rendered last so they're visually on top)
  for (let s = 0; s < services.length; s++) {
    const color = COLORS[s % COLORS.length];
    const top = stackedTotals[s];
    for (let m = 0; m < numMonths; m++) {
      const val = data.series[services[s]][m];
      if (val > 0) {
        const circle = document.createElementNS(svgNS, "circle");
        circle.setAttribute("cx", String(x(m)));
        circle.setAttribute("cy", String(y(top[m])));
        circle.setAttribute("r", "3.5");
        circle.setAttribute("fill", color);
        circle.setAttribute("stroke", "#fff");
        circle.setAttribute("stroke-width", "1.5");
        circle.style.pointerEvents = "none";
        svg.appendChild(circle);
      }
    }
  }

  wrapper.appendChild(svg);
  wrapper.appendChild(tooltip);

  // Legend
  const legend = document.createElement("div");
  legend.className = "crm-login-legend";
  for (let s = 0; s < services.length; s++) {
    const color = COLORS[s % COLORS.length];
    const item = document.createElement("span");
    item.className = "crm-login-legend-item";
    item.innerHTML = `<span class="crm-login-legend-swatch" style="background:${color}"></span>${services[s]}`;
    legend.appendChild(item);
  }
  wrapper.appendChild(legend);

  container.innerHTML = "";
  container.appendChild(wrapper);
}

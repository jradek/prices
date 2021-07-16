// <script>

/////////////////////////////////////////////////////////////////////////////
// TABLE BUILDING
/////////////////////////////////////////////////////////////////////////////

function generatePrices() {
  var root = document.getElementById("root");

  const rows = g_prices.map((it) => {
    return processRow(it);
  });

  root.innerHTML = rows.join(" ");
}

function processRow(data) {
  const name = data[1];
  const serving_size = data[5];
  const unit = data[6];
  const min_price = data[2];
  const avg_price = data[3];
  const max_price = data[4];
  const category = data[7];
  const num_measures = data[8];
  const categoryClasses = g_categories[category] || "fas fa-question";
  const per_store = data[9];
  const per_store_html = formatStores(per_store);

  const spacing = "padding: 0px 2px;";

  return `<li>
<div class="collapsible-header">
  <i class="${categoryClasses}" style="${spacing}"></i>
  <b style="${spacing}">${name} (${serving_size} ${unit})</b>
  <span class="my-price-background green" style="${spacing}">${min_price.toFixed(
    2
  )}&euro;</span>
  <span class="my-price-background yellow darken-3" style="${spacing}">${avg_price.toFixed(
    2
  )}&euro;</span>
  <span class="my-price-background red" style="${spacing}">${max_price.toFixed(
    2
  )}&euro;</span>
  <span style="${spacing}">#${num_measures}</span>
</div>
<div class="collapsible-body">
${per_store_html}
</div>
  </li>`;
}

function formatStores(data) {
  const rows = data.map((it) => formatStoreRow(it));

  return `
<table>
  <thead>
    <tr>
      <th>Store</th>
      <th>Min</th>
      <th>Avg</th>
      <th>Max</th>
      <th>#</th>
    </tr>
  </thead>
    ${rows.join(" ")}
  <tbody>
  </tbody>
</table>`;
}

function formatStoreRow(row) {
  // console.log(row);
  const store = row[0];
  const min_price = row[1];
  const avg_price = row[2];
  const max_price = row[3];
  const num_measures = row[4];

  const storeColors = g_storeToColor[store] || [
    "#eceff1",
    "blue-grey lighten-5",
    "black-text",
  ];

  return `
<tr>
  <td><span class="my-store-background ${storeColors[1]} ${
    storeColors[2]
  }">${store}</span></td>
  <td>${min_price.toFixed(2)}&euro;</td>
  <td>${avg_price.toFixed(2)}&euro;</td>
  <td>${max_price.toFixed(2)}&euro;</td>
  <td>${num_measures}</td>
</tr>
  `;
}

// </script>

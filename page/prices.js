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

  const style = "width: 80px; float: left";

  return `
<li>
  <div class="collapsible-header" style="display: flex; justify-content: space-between">
    <div>
      <i class="${categoryClasses}"></i>
      <span style="font-weight: bold">${name} (${serving_size} ${unit})</span>
    </div>
    <div>
      <span class="my-price-background green lighten-2 center" style="${style}">${min_price.toFixed(
        2
      )}&euro;</span>
      <span class="my-price-background yellow lighten-2 center" style="${style}">${avg_price.toFixed(
        2
      )}&euro;</span>
      <span class="my-price-background red lighten-2 center" style="${style}">${max_price.toFixed(
        2
      )}&euro;</span>
      <span class="center" style="${style}; font-weight: bold"># ${num_measures}</span>
    </div>
  </div>
  <div class="collapsible-body">
    ${per_store_html}
  </div>
</li>`;
}

// https://raddevon.com/articles/sort-array-numbers-javascript/
const numberSorter = (a, b) => a - b;

function formatStores(data) {
  const pricesPerServing = data
    .map((it) => {
      return it[1];
    })
    .sort(numberSorter);

  const minPrice = pricesPerServing[0];
  const maxPrice = pricesPerServing.pop();
  const rows = data.map((it) => formatStoreRow(it, minPrice, maxPrice));

  return `
<table>
  <thead>
    <tr>
      <th>Store</th>
      <th>Min</th>
      <th>Average</th>
      <th>Max</th>
      <th>#</th>
    </tr>
  </thead>
  <tbody>
    ${rows.join(" ")}
  </tbody>
</table>`;
}

function formatStoreRow(row, overallMinPrice, overallMaxPrice) {
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

  // mark best/worst min price per serving
  let rowStyle = "";
  if (min_price < overallMinPrice + 0.01) {
    rowStyle = "green lighten-5";
  } else if (min_price > overallMaxPrice - 0.01) {
    rowStyle = "red lighten-5";
  }

  return `
<tr class="${rowStyle}">
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

// <script>

/////////////////////////////////////////////////////////////////////////////
// TABLE BUILDING
/////////////////////////////////////////////////////////////////////////////

function generatePrices() {
  var root = document.getElementById("root");

  const rows = g_items.map((it) => {
    return processRow(it);
  });

  root.innerHTML = rows.join(" ");
}

function processRow(data) {
// 0: id, 1: name, 2: serving_size, 3: unit, 4: category, 5: min_price_per_serving, 6: avg_price_per_serving, 7: max_price_per_serving, 8: num_measures
  const itemId = data[0];
  const name = data[1];
  const serving_size = data[2];
  const unit = data[3];
  const category = data[4];
  const min_price = data[5] ? `${data[5].toFixed(2)}&euro;` : "";
  const avg_price = data[6] ? `${data[6].toFixed(2)}&euro;` : "";
  const max_price = data[7] ? `${data[7].toFixed(2)}&euro;` : "";
  const num_measures = data[8] ? data[8].toFixed(0) : "";
  const categoryClasses = g_categories[category] || "fas fa-question";
  const per_store_html = formatStores(itemId);

  const style = "width: 80px; float: left";

  return `
<li>
  <div class="collapsible-header" style="display: flex; justify-content: space-between">
    <div>
      <i class="${categoryClasses}"></i>
      <span style="font-weight: bold">${name} (${serving_size} ${unit})</span>
    </div>
    <div>
      <span class="my-price-background green lighten-2 center" style="${style}">${min_price}</span>
      <span class="my-price-background yellow lighten-2 center" style="${style}">${avg_price}</span>
      <span class="my-price-background red lighten-2 center" style="${style}">${max_price}</span>
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

function formatStores(itemId) {
  const perStoreData = g_pricesPerStore[itemId];

  let rows = [];
  for (const idx in perStoreData) {
    let row = formatStoreRow(perStoreData[idx])
    rows.push(row)
  }

  return `
<table>
  <thead>
    <tr>
      <th>Store</th>
      <th>Min</th>
      <th>Average</th>
      <th>Max</th>
      <th>#</th>
      <th>Regular</th>
    </tr>
  </thead>
  <tbody>
    ${rows.join(" ")}
  </tbody>
</table>`;

}

function formatStoreRow(data, overallMinPrice, overallMaxPrice) {
  // console.log(row);
// 0: item_id, 1: store, 2: min_price_per_serving, 3: min_date, 4: avg_price_per_serving, 5: max_price_per_serving, 6: max_date, 7: num_measures, 8: regular_price_per_serving, 9: regular_date

  const store = data[1];
  const min_price_per_serving = data[2] ? `${data[2].toFixed(2)}&euro;` : "";
  const min_date = data[3] ? data[3] : "";
  const avg_price_per_serving = data[4] ? `${data[4].toFixed(2)}&euro;` : "";
  const max_price_per_serving = data[5] ? `${data[5].toFixed(2)}&euro;` : "";
  const max_date = data[6] ? data[6] : "";
  const num_measures = data[7] ? data[7].toFixed(0) : ""
  const regular_price_per_serving = data[8] ? `${data[8].toFixed(2)}&euro;` : "";
  const regular_date = data[9] ? data[9] : "";

  const storeColors = g_storeToColor[store] || [
    "#eceff1",
    "blue-grey lighten-5",
    "black-text",
  ];

  // mark best/worst min price per serving
  let rowStyle = "";
  // if (min_price < overallMinPrice + 0.01) {
  //   rowStyle = "green lighten-5";
  // } else if (min_price > overallMaxPrice - 0.01) {
  //   rowStyle = "red lighten-5";
  // }

  return `
<tr class="${rowStyle}">
  <td><span class="my-store-background ${storeColors[1]} ${
    storeColors[2]
  }">${store}</span></td>
  <td><p>${min_price_per_serving}</p><p style="font-size: x-small">${min_date}</p></td>
  <td><p>${avg_price_per_serving}</p><p style="font-size: x-small">&nbsp;</p></td>
  <td><p>${max_price_per_serving}</p><p style="font-size: x-small">${max_date}</p></td>
  <td>${num_measures}</td>
  <td><p>${regular_price_per_serving}</p><p style="font-size: x-small">${regular_date}</p></td>
</tr>
  `;
}

// </script>

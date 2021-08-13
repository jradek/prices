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

/**
 * Generate two tabs
 * - Tab1: table with stores and the price per serving
 * - Tab2: table with stores and the price per package
 */
function get_tabs(
  itemId,
  itemUnit,
  servingSize,
  packageSize,
  perServingHtml,
  perPackageHtml
) {
  const id_left = `item${itemId}-left`;
  const id_right = `item${itemId}-right`;

  return `
<div class="row">
  <div class="col s12">
    <ul class="tabs">
      <li class="tab col s6">
        <a class="active" href="#${id_left}">Per ${servingSize}${itemUnit} serving</a>
      </li>
      <li class="tab col s6"><a href="#${id_right}">Per ${packageSize}${itemUnit} package</a></li>
    </ul>
  </div>
  <div id="${id_left}" class="col s12">
    ${perServingHtml}
  </div>
  <div id="${id_right}" class="col s12">
    ${perPackageHtml}
  </div>
</div>
`;
}

function processRow(data) {
  // 0: id, 1: name, 2: serving_size, 3: unit, 4: category, 5: usual_package_size, 6: min_price_per_serving, 7: avg_price_per_serving, 8: max_price_per_serving, 9: num_measures
  const itemId = data[0];
  const name = data[1];
  const serving_size = data[2];
  const unit = data[3];
  const category = data[4];
  const usual_package_size = data[5];
  const min_price = data[6] ? `${data[6].toFixed(2)}&euro;` : "&nbsp;";
  const avg_price = data[7] ? `${data[7].toFixed(2)}&euro;` : "&nbsp;";
  const max_price = data[8] ? `${data[8].toFixed(2)}&euro;` : "&nbsp;";
  const num_measures = data[9] ? `# ${data[9].toFixed(0)}` : "";

  const categoryClasses = g_categories[category] || "fas fa-question";

  const perServingHtml = formatStores(itemId);

  const style = "width: 80px; float: left";

  // tabs or no tabs
  const contentHtml = usual_package_size
    ? get_tabs(
        itemId,
        unit,
        serving_size,
        usual_package_size,
        perServingHtml,
        "Micha"
      )
    : perServingHtml;

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
      <span class="center" style="${style}; font-weight: bold">${num_measures}</span>
    </div>
  </div>
  <div class="collapsible-body">
    ${contentHtml}
  </div>
</li>`;
}

// https://raddevon.com/articles/sort-array-numbers-javascript/
const numberSorter = (a, b) => a - b;

function formatStores(itemId) {
  const perStoreData = g_pricesPerStore[itemId];

  // no data for this item available
  if (!perStoreData) {
    return "";
  }

  // determine the overall min price per serving for all stores
  // get value and filter 'null'
  let minPrices = perStoreData.map((it) => it[2]).filter((x) => x);

  minPrices = minPrices.sort(numberSorter);

  // min and max price per serving across stores
  let minPrice = 0;
  let maxPrice = 1000;
  if (minPrices.length > 0) {
    minPrice = minPrices[0];
    maxPrice = minPrices.pop();
  }

  const rows = perStoreData.map((store) => {
    return formatStoreRow(store, minPrice, maxPrice);
  });

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
  const min_price = data[2] ? data[2] : null;
  const min_price_per_serving = data[2] ? `${data[2].toFixed(2)}&euro;` : "";
  const min_date = data[3] ? data[3] : "";
  const avg_price_per_serving = data[4] ? `${data[4].toFixed(2)}&euro;` : "";
  const max_price_per_serving = data[5] ? `${data[5].toFixed(2)}&euro;` : "";
  const max_date = data[6] ? data[6] : "";
  const num_measures = data[7] ? data[7].toFixed(0) : "";
  const regular_price_per_serving = data[8]
    ? `${data[8].toFixed(2)}&euro;`
    : "";
  const regular_date = data[9] ? data[9] : "";

  const storeColors = g_storeToColor[store] || [
    "#eceff1",
    "blue-grey lighten-5",
    "black-text",
  ];

  // mark best/worst min price per serving
  let rowStyle = "";
  if (min_price && min_price < overallMinPrice + 0.01) {
    rowStyle = "green lighten-5";
  } else if (min_price && min_price > overallMaxPrice - 0.01) {
    rowStyle = "red lighten-5";
  }

  return `
<tr class="${rowStyle}">
  <td><span class="my-store-background ${storeColors[1]} ${storeColors[2]}">${store}</span></td>
  <td><p>${min_price_per_serving}</p><p style="font-size: x-small">${min_date}</p></td>
  <td><p>${avg_price_per_serving}</p><p style="font-size: x-small">&nbsp;</p></td>
  <td><p>${max_price_per_serving}</p><p style="font-size: x-small">${max_date}</p></td>
  <td>${num_measures}</td>
  <td><p>${regular_price_per_serving}</p><p style="font-size: x-small">${regular_date}</p></td>
</tr>
  `;
}

// </script>

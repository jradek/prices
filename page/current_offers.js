// <script>

/////////////////////////////////////////////////////////////////////////////
// SORTING
/////////////////////////////////////////////////////////////////////////////

const g_sortOptionToDataColumnIds = {
  // store, start date, name, price per serving
  store: [3, 0, 4, 11],
  // start date, name, price per serving
  date: [0, 4, 11],
  // name, price per serving, store
  product: [4, 11, 3],
  // category, name, price per serving
  category: [10, 4],
};

/**
sort array of arrays `data` by sort columns
the sort columns are the indexes of the sub arrays, e.g. [1,0,2]
*/
function sortArrayOfArrays(data, sortColumns) {
  // first: duplicate clone teh data
  let result = JSON.parse(JSON.stringify(data));

  // assemble sort function
  let sortFunction = (a, b) => {
    for (let i in sortColumns) {
      const idx = sortColumns[i];

      if (a[idx] < b[idx]) return -1;
      if (a[idx] > b[idx]) return 1;
    }
    return 0;
  };

  return result.sort(sortFunction);
}

function sortDataCallback(sortOption) {
  if (sortOption == null) {
    return;
  }

  const sortColumns = g_sortOptionToDataColumnIds[sortOption];
  const result = sortArrayOfArrays(g_offers, sortColumns);
  generateTable(result);
}

/////////////////////////////////////////////////////////////////////////////
// TABLE BUILDING
/////////////////////////////////////////////////////////////////////////////

function generateTable(offers) {
  var root = document.getElementById("table-body");
  const today = isoFormatYMD(new Date());

  const rows = offers.map((it) => {
    return buildRow(it, today);
  });

  root.innerHTML = rows.join(" ");
}

function buildRow(row, todayString) {
  // console.log(row);

  const start = row[0];
  const end = row[1];
  const isShort = row[2] == 1;
  const store = row[3];
  const item = row[4];
  const amount = row[6];
  const price = row[7] / 100.0;
  const unit = row[8];
  const serving_size = row[9];
  const category = row[10];
  const price_per_serving = row[11];
  const min_price_per_serving = row[14];
  const isDealPercent = row[15] == 1;
  const priceDiffPerServing = price_per_serving - min_price_per_serving;
  const isDealPerServing = row[16];
  const isDealStore = row[17];
  const storeRegularPricePerServing = row[18];
  const dayName = getDayName(start);
  const bestPrice = (min_price_per_serving * amount) / serving_size;
  const priceDiff = price - bestPrice;
  const storeColors = g_storeToColor[store] || [
    "#eceff1",
    "blue-grey lighten-5",
    "black-text",
  ];

  // check if entry is still valid
  // this is necessary, because export may have been a long time ago
  if (end < todayString) {
    return "";
  }

  var dealIcons = "";
  var dealClasses = "";

  if (isDealPerServing) {
    dealClasses = "green lighten-5";
    dealIcons += "<p style=\"font-size: x-small\"><i class=\"fas fa-puzzle-piece\"></i></p>";
  }

  if (isDealPercent) {
    dealClasses = "green lighten-5";
    dealIcons += "<p style=\"font-size: x-small\">5&#37;<p>"
  }

  if (isDealStore) {
    dealClasses = "green lighten-5";
    dealIcons += "<p style=\"font-size: x-small\"><i class=\"fas fa-store\"></i></p>";
  }

  if (isDealStore && !isDealPercent && !isDealPerServing) {
    dealClasses = "yellow lighten-5";
  }

  // var storeRegularPerServingStr = "";
  // var storeRegularPriceStr = "";

  // if (storeRegularPricePerServing) {
  //   const foo = storeRegularPricePerServing - min_price_per_serving;
  //   storeRegularPerServingStr = `<p style="font-size: x-small">(+${foo.toFixed(2)}&euro;)</p>`
  //   const bar = (storeRegularPricePerServing * amount / serving_size) - (min_price_per_serving * amount / serving_size);
  //   storeRegularPriceStr = `<p style="font-size: x-small">(+${bar.toFixed(2)}&euro;)</p>`;
  // }

  const dayStyle = isShort ? "font-weight: bold" : "font-weight: normal";
  const categoryClasses = g_categories[category] || "fas fa-question";

  var dateAvailableIcon = "";
  if (start > todayString) {
    dateAvailableIcon =
      '<span class="material-icons">hourglass_disabled</span>';
  }

  return `<tr class="${dealClasses}">
<td>${dateAvailableIcon}</td>
<td>
  <p style="${dayStyle}">${dayName} (${getDateDiffInDays(start, end) + 1})</p>
  <p style="font-size: x-small">${start}</p>
</td>
<td><span class="my-store-background ${storeColors[1]} ${
    storeColors[2]
  }">${store}</span></td>
<td><i class="${categoryClasses}"></i></td>
<td>${item}</td>
<td>${amount} ${unit}</td>
<td>${dealIcons}</td>
<td><p>${price}&euro;<p><p style="font-size: x-small">(+${Math.abs(
    priceDiff
  ).toFixed(2)}&euro;)</p>
</td>
<td>
  <p>${price_per_serving.toFixed(2)}&euro;/${serving_size}${unit}</p>
  <p style="font-size: x-small">(+${priceDiffPerServing.toFixed(2)}&euro;)</p>
</td>
</tr>`;
}

/////////////////////////////////////////////////////////////////////////////
// UTIL
/////////////////////////////////////////////////////////////////////////////

function isoFormatYMD(date) {
  var mm = date.getMonth() + 1; // getMonth() is zero-based
  var dd = date.getDate();

  return [
    date.getFullYear(),
    (mm > 9 ? "" : "0") + mm,
    (dd > 9 ? "" : "0") + dd,
  ].join("-");
}

function getDayName(dateString) {
  var date = new Date(dateString);
  return date.toLocaleDateString("en-US", { weekday: "long" });
}

var getDateDiffInDays = function (date1, date2) {
  dt1 = new Date(date1);
  dt2 = new Date(date2);
  return Math.floor(
    (Date.UTC(dt2.getFullYear(), dt2.getMonth(), dt2.getDate()) -
      Date.UTC(dt1.getFullYear(), dt1.getMonth(), dt1.getDate())) /
      (1000 * 60 * 60 * 24)
  );
};

// </script>

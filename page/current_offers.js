// <script>

const g_categories = {
  brandy: "fas fa-wine-glass-alt",
  cake: "fas fa-birthday-cake",
  chocolate: "fas fa-cookie",
  egg: "fas fa-egg",
  dairy: "fas fa-hat-cowboy",
  fruit: "far fa-lemon",
  fish: "fas fa-fish",
  gin: "fas fa-cocktail",
  hygiene: "fas fa-soap",
  liquor: "fas fa-glass-martini-alt",
  meat: "fas fa-drumstick-bite",
  rum: "fas fa-glass-whiskey",
  "soft drink": "fab fa-gulp",
  vegetable: "fas fa-leaf",
  vodka: "fas fa-glass-whiskey",
  wine: "fas fa-wine-bottle",
  whiskey: "fas fa-glass-whiskey",
};

g_storeToColor = {
  // RBG, materialized name, text color
  aldi: ["#01579b", "light-blue darken-4", "white-text"],
  edeka: ["#ffff00", "yellow accent-2", "blue-text"],
  "edeka sander": ["#ffff00", "yellow accent-2", "blue-text"],
  globus: ["#558b2f", "light-green darken-3", "black-text"],
  kaufland: ["#f44336", "red", "white-text"],
  lidl: ["#1976d2", "blue darken-2", "yellow-text"],
  netto: ["#ff3d00", "deep-orange accent-3", "yellow-text text-lighten-2"],
  norma: ["#f57f17", "yellow darken-4", "white-text"],
  penny: ["#c62828", "red darken-3", "white-text"],
  real: ["#fffffff", "white", "indigo-text text-darken-4"],
  rewe: ["#b71c1c", "red darken-4", "white-text"],
  tegut: ["#e65100", "orange darken-4", "white-text"],
  "thomas philipps": ["#ffffff", "white", "red-text text-darken-1"],
};

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

  var dealClasses = "";
  if (isDealPercent) {
    dealClasses = "green lighten-5";
  }

  if (isDealPerServing && !isDealPercent) {
    dealClasses = "yellow lighten-5";
  }

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
<td><i class="${categoryClasses}"></i></td>
<td>${item}</td>
<td><span class="my-store-background ${storeColors[1]} ${
    storeColors[2]
  }">${store}</span></td>
<td>${amount} ${unit}</td>
<td><p>${price}&euro;<p><p style="font-size: x-small">(+${Math.abs(
    priceDiff
  ).toFixed(2)}&euro;)</p></td>
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

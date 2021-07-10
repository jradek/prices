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

/////////////////////////////////////////////////////////////////////////////
// SORTING
/////////////////////////////////////////////////////////////////////////////

const g_sortOptionToDataColumnIds = {
  // store, start date, name, price per serving
  store: [3, 0, 4, 11],
  // start date, name, price per serving
  date: [0, 4,  11],
  // name, price per serving, store
  product: [4, 11, 3],
  // category, name, price per serving
  category: [10, 4, ]
}

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

function getRadioValue(form, name) {
  var val = null;
  // get list of radio buttons with specified name
  var radios = form.elements[name];

  // loop through list of radio buttons
  for (var i = 0, len = radios.length; i < len; i++) {
    if (radios[i].checked) {
      // radio checked?
      val = radios[i].value; // if so, hold its value in val
      break; // and break out of for loop
    }
  }
  return val; // return value of checked radio or undefined if none checked
}

function sortDataCallback() {
  const sortForm = document.getElementById("predefinedSortForm");
  const sortOption = getRadioValue(sortForm, "sortRadioGroup");

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
  const today = isoFormat(new Date());
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
  const priceDiff = price_per_serving - min_price_per_serving;
  const isDealPerServing = row[16];
  const dayName = getDayName(start);
  const storeColors = g_storeToColor[store];

  var dealClasses = "";
  if (isDealPercent) {
    dealClasses = "green lighten-5";
  }

  if (isDealPerServing && !isDealPercent) {
    dealClasses = "yellow lighten-5";
  }

  var dayStyle = "font-weight: normal";
  if (isShort) {
    dayStyle = "font-weight: bold";
  }

  var categoryClasses = "fas fa-question";
  if (category in g_categories) {
    categoryClasses = g_categories[category];
  }

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
<td>${price}&euro;</td>
<td style="font-size: x-small">
  <p>${price_per_serving.toFixed(2)}&euro;/${serving_size}${unit}</p>
  <p>(+${priceDiff.toFixed(2)}&euro;)</p>
</td>
  </tr>`;
}

/////////////////////////////////////////////////////////////////////////////
// UTIL
/////////////////////////////////////////////////////////////////////////////

function isoFormat(date) {
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
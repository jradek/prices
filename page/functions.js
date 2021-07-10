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

function populateTable() {
  console.log("works");
  var root = document.getElementById("table-body");
  const today = isoFormat(new Date());
  const rows = g_offers.map((it) => {
    return buildRow(it, today);
  });
  root.innerHTML = rows.join(" ");
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

function buildRow(row, todayString) {
  console.log(row);

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
  const isDeal = row[15] == 1;
  const priceDiff = price_per_serving - min_price_per_serving;
  const dayName = getDayName(start);
  const storeColors = g_storeToColor[store];

  var dealClasses = "";
  if (isDeal) {
    dealClasses = "green lighten-5";
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
<td style="padding: 0px 5px !important;">${dateAvailableIcon}</td>
<td>
  <p style="${dayStyle}">${dayName} (${getDateDiffInDays(start, end) + 1})</p>
  <p style="font-size: x-small">${start}</p>
</td>
<td style="padding: 0px 5px !important;"><i class="${categoryClasses}"></i></td>
<td>${item}</td>
<td><span class="${storeColors[1]} ${
    storeColors[2]
  }" style="padding: 2px 5px">${store}</span></td>
<td>${amount} ${unit}</td>
<td>${price}&euro;</td>
<td style="font-size: x-small">
  <p>${price_per_serving.toFixed(2)}&euro;/${serving_size}${unit}</p>
  <p>(+${priceDiff.toFixed(2)}&euro;)</p>
</td>
  </tr>`;
}

function isoFormat(date) {
  var mm = date.getMonth() + 1; // getMonth() is zero-based
  var dd = date.getDate();

  return [
    date.getFullYear(),
    (mm > 9 ? "" : "0") + mm,
    (dd > 9 ? "" : "0") + dd,
  ].join("-");
}

#! /usr/bin/env sh

# dump item table to html file

mkdir -p tmp/
cat <<EOF > tmp/items.html
<html>
  <header>
    <style>
      table > tbody > tr:nth-child(odd) > td {
        background-color: #8ff;
      }
      table > tbody > tr:nth-child(even) > td {
        background-color: #fff;
      }
    </style>
  </header>
  <body>
    <table>
EOF

sqlite3 --html tmp/prices.db "SELECT * FROM item ORDER BY name;" >> tmp/items.html

cat <<EOF >> tmp/items.html
    </table>
  </body>
</html>
EOF

echo "wrote 'tmp/items.html"
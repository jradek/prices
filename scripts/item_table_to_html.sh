#! /usr/bin/env sh

# dump item table to html file

output_file="tmp/item_table.html"

mkdir -p "$(dirname "$output_file")"
cat <<EOF > $output_file
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

sqlite3 --html tmp/prices.db "SELECT * FROM item ORDER BY name;" >> $output_file

cat <<EOF >> $output_file
    </table>
  </body>
</html>
EOF

echo "wrote '$output_file'"
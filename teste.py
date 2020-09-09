#!/usr/bin/env python3

with open("index.html", "r") as in_file:
    buf = in_file.readlines()

with open("index.html", "w") as out_file:
    count = 0
    for line in buf:
        if line.strip() == "<tbody>":
            line = line + "<tr><td>-----------</td><td>-----------</td><td \
                class=\"Undefined\">--------</td></tr>"
        out_file.write(line)
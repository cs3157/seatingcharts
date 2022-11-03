header = """
    <style>
            table {
                table-layout: fixed;
                width: 100%;
            }
            img {
                width: 60px;
                vertical-align: text-bottom;
            }
            .seat {
                font-weight: bold;
                font-size: 14pt;
                vertical-align: top;
            }
            .name {
                font-size: 9pt;
            }
            td {
                text-align: center;
                vertical-align: baseline;
                width: 70px;
            }
            .unselected {
                background-color: white;
            }
            .selected {
                background-color: orange;
            }
    </style>

    <script>
        function selectStudent(cell) {
            if (cell.className === "unselected") {
                cell.className = "selected";
            } else {
                cell.className = "unselected";
            }
        }
    </script>
    <body><table border=1>\n\n"""

css = """<style>
            .seat {{
                padding-left: 1em;
                margin-bottom: .2em;
            }}
            .name {{
                font-size: 9pt;
            }}
            .assignments {{
                -webkit-column-count: 4; /* Chrome, Safari, Opera */
                -moz-column-count: 4; /* Firefox */
                column-count: 4;
            }}
            h3 {{
                text-align: center;
            }}
            </style>
    <body>
    <h3>{}</h3>
    <div class="assignments">\n\n"""

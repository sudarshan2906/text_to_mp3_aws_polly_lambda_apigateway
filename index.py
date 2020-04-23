def create_html(api_url):
    html = '<body>' \
            '<form method="GET" action="https://'+api_url+'/">' \
                '<label>Text to convert to mp3</label><br>' \
                '<textarea name="text" placeholder="Text"></textarea><br>' \
            '<input type="submit" value="Submit">' \
            '</form>' \
            '</body>'
    f = open("index.html", "w")
    f.write(html)
    f.close()
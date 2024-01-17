import re #regular expressions
from urllib.request import urlopen

with open('scrape_output.csv', 'w') as file:
    url = "https://maggardcolin.github.io/projects.html"
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    pattern = '<(div|a).*?class=\".*?project(?!-container).*?\".*?>(\n.*?)*</(div|a).*?>\n'
    match_results = re.finditer(pattern, html, re.IGNORECASE)
    match_count = 0
    for match in match_results:
        match_content = match.group()
        pattern = 'time-spent=\".*\"'
        time_spent = re.search(pattern, match_content, re.IGNORECASE).group()
        time_spent = re.sub("(time-spent=\")|\"", "", time_spent)
        pattern = ("<(div|a).*?class=\".*?project(?!-container).*?\".*?>")
        information = re.search(pattern, match_content).group()
        classes = re.search("class=\".*?\"", information).group()
        classes = re.sub("class=", "", classes)
        relevance = re.search("relevance=\".*?\"", information).group()
        relevance = re.sub("relevance=", "", relevance)
        chron_order = re.search("chron-order=\".*?\"", information).group()
        chron_order = re.sub("chron-order=", "", chron_order)
        match_content = re.sub("<(div|a).*?class=\".*?project(?!-container).*?\".*?>", "", match_content)
        link_pattern = "<.*?href=\".*?\".*?>.*?</.*?>"
        links = re.finditer(link_pattern, match_content)
        link_list = list(links)
        link_count = 0
        match_content = re.sub(link_pattern, "!link-here!", match_content)
        match_content = re.sub("<.*?>", "", match_content)
        lines = match_content.splitlines()
        match_content = ""
        for line in lines:
            if ("Approximate time spent:") in line.strip():
                line = line.strip() + " " + time_spent
            text = ""
            text = line.strip()
            text = text.replace("\"", "\"\"")
            if (text != ""):
                match_content += "\"" + text + "\","
        if ("!link-here!") in match_content:
            match_content += "\"Links used:"
            for link in link_list:
                link_content = re.sub("(\">)", "\"\" with text: \"\"", link_list[link_count].group())
                link_content = re.sub("(</a.*?>)", "", link_content)
                link_content = re.sub("(<a.*?href=\")", " \"\"", link_content)
                match_content += link_content + "\"\"\""
                link_count += 1
        match_content += classes + "," + relevance + "," + chron_order
        file.write(match_content + "\n")
        match_count += 1
    print(str(match_count) + ' matches found')
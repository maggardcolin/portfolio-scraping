import re #regular expressions
from urllib.request import urlopen
url = "https://maggardcolin.github.io/projects.html"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf-8")

pattern = '<(div|a).*?class=\".*?project(?!-container).*?\".*?>(\n.*?)*</(div|a).*?>\n'
match_results = re.finditer(pattern, html, re.IGNORECASE)
match_count = 0
with open('output.txt', 'w') as file:
    for match in match_results:
        match_content = match.group()
        pattern = 'time-spent=\".*\"'
        time_spent = re.search(pattern, match_content,re.IGNORECASE).group()
        time_spent = re.sub("(time-spent=\")|\"", "", time_spent)
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
                line = line.strip() + " " + time_spent + "+ hours"
            #if ("!link-here!") in line.strip():
                #line = re.sub("!link-here!", link_list[link_count].group(), line)
                #link_count += 1
            if (line.strip() != ""):
                match_content += line.strip() + "\n"
        if ("!link-here!") in match_content:
            match_content += "Links used:"
            for link in link_list:
                match_content += link_list[link_count].group()
                link_count += 1
        file.write(match_content + "\n")
        match_count += 1
    print(str(match_count) + ' matches found')
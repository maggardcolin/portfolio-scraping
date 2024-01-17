import re #regular expressions
import json
from urllib.request import urlopen

# this program scrapes my website and creates output in both csv and json formats
url_header = "https://maggardcolin.github.io/"
url = "https://maggardcolin.github.io/index.html"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf-8")

urls_ = list(re.finditer("\".*?.html\"", html))
urls = list()
for url in urls_:
    html_link = re.sub("\"", "", url.group())
    if html_link not in urls:
        urls.append(html_link)

# CSV format
with open('scrape_output.csv', 'w') as file:
    for url in urls:
        url = url_header + url
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        #print(url)
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
            match_content += classes + "," + relevance + "," + chron_order + ","
            match_count += 1
            if match_count == 1:
                file.write(url + "\n")
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
            file.write(match_content + "\n")
        #print(str(match_count) + ' matches found')

# json format
with open('scrape_output.json', 'w') as file:
    output_data = {"matches": []}
    for url in urls:
        url = url_header + url
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

        pattern = '<(div|a).*?class=\".*?project(?!-container).*?\".*?>(\n.*?)*</(div|a).*?>\n'
        match_results = re.finditer(pattern, html, re.IGNORECASE)

        for match in match_results:
            match_content = match.group()
            pattern = 'time-spent=\".*\"'
            time_spent = re.search(pattern, match_content, re.IGNORECASE).group()
            time_spent = re.sub("(time-spent=\")|\"", "", time_spent)
            pattern = ("<(div|a).*?class=\".*?project(?!-container).*?\".*?>")
            information = re.search(pattern, match_content).group()
            classes = re.search("class=\".*?\"", information).group()
            classes = re.sub("class=", "", classes)
            classes = re.sub("\"", "", classes)
            relevance = re.search("relevance=\".*?\"", information).group()
            relevance = re.sub("relevance=", "", relevance)
            relevance = re.sub("\"", "", relevance)
            chron_order = re.search("chron-order=\".*?\"", information).group()
            chron_order = re.sub("chron-order=", "", chron_order)
            chron_order = re.sub("\"", "", chron_order)
            match_content = re.sub("<(div|a).*?class=\".*?project(?!-container).*?\".*?>", "", match_content)
            link_pattern = "<.*?href=\".*?\".*?>.*?</.*?>"
            links = re.finditer(link_pattern, match_content)
            link_list = list(links)
            link_count = 0
            match_content = re.sub(link_pattern, "!link-here!", match_content)
            match_content = re.sub("<.*?>", "", match_content)
            lines = match_content.splitlines()

            match_content = {"url": url, "classes": classes, "relevance": relevance, "chron-order": chron_order, 
                             "title": "", "time-spent": time_spent}

            explanation = False
            description = False
            for line in lines:
                text = line.strip()
                text = text.replace("\"", "\"\"")

                if text == "":
                    continue

                if description == True:
                    match_content["description"] = text
                    description = False
                    continue

                if explanation:
                    match_content["how-it-works"] = text
                    explanation = False
                    continue

                if line == lines[1]:
                    match_content["title"] = text
                elif "Approximate time" in text:
                    description = True
                    continue
                elif "Main focuses" in text:
                    match_content["main-focus"] = text.replace("Main focuses: ", "")
                elif "Main focus" in text:
                    match_content["main-focus"] = text.replace("Main focus: ", "")
                elif "How it works" in text:
                    explanation = True
                    continue
                elif "- Remote" in text:
                    match_content["time-span"] = text
                else:
                    if text != "":
                        match_content["fields"].append(text)

            if ("description" in match_content and "!link-here!" in match_content["description"]) or ("how-it-works" in match_content and "!link-here!" in match_content["how-it-works"]):
                match_content["Links used:"] = []
                for link in link_list:
                    link_content = re.sub("(\">)", "\" with text: \"", link_list[link_count].group())
                    link_content = re.sub("(</a.*?>)", "\"", link_content)
                    link_content = re.sub("(<a.*?href=\")", "\"", link_content)
                    match_content["Links used:"].append(link_content)
                    link_count += 1


            output_data["matches"].append(match_content)

    file.write(json.dumps(output_data, indent=2))
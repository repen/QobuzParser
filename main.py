import requests, json
from bs4 import BeautifulSoup
from report import ExelPlain
from datetime import datetime
import os

NAME_FILE = "import.xlsx"
WORK_DIR = os.getcwd()



class ErrorGetContent(Exception):
    pass

class ErrorAttributeElement(Exception):
    pass

class Qobuz:
    def __init__(self, message_send = None, report = None):
        self.error = 0
        self.message = None
        self.message_send = message_send
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; \
                                x64; rv:47.0) Gecko/20100101 Firefox/48.0'}

    def open_urls(self):
        with open( os.path.join( WORK_DIR, "urls.txt" ), encoding="utf8") as f_obj:
            data = [x.replace("\n","") for x in f_obj]
        return data

    def get_content(self, url):
        try:
            r = requests.get(url, headers=self.header)
            if r.status_code == 200:
                return r.text
        except:
            pass

    def main(self):
        table = '''<table><tbody>{}</tbody></table>'''.strip()
        urls = self.open_urls()
        if not urls:
            self.message_send("[Error] No urls")
            raise Exception("[Error] No urls")

        try:
            wb = ExelPlain.load_xlsx(NAME_FILE)
        except FileNotFoundError:
            wb = ExelPlain()
            wb = wb.create_sheet("Music")

        for e2, url in enumerate(urls):
            try:
                html = self.get_content(url)
                if not html:
                    self.message_send("[ERROR] not content")
                    raise ErrorGetContent("[ERROR] not content")
                soup = BeautifulSoup(html, "html.parser")

                data = soup.select_one('script[type="application/ld+json"]').text.strip()
                data = json.loads(data)

                author = soup.select_one("h2").text.strip()
                title= author + " - " + soup.h1.text
                temp = '<img src="{}" alt="" class="fr-fic fr-dib">'
                image = temp.format( soup.select_one('img.album-cover__image[src][alt][title]')['src'] )

                tracks = soup.select_one("#playerTracks")
                build=[]
                for e, track in enumerate(tracks.select(".player__item"), start=1):
                    string1 = '<tr><td style="width:11.911%;">{}</td>'.format(e)
                    string1 += '<td style="width:76.6667%;">{}</td>'.format( track.select_one("div.track__overlay")['title'].strip() )
                    string1 += '<td style="width:11.1111%;" width="25">{}</td></tr>'.format(track.select_one("span.track__item--duration").text.strip())
                    build.append(string1)

                table = table.format( "".join(build) )
                
                date  = data["releaseDate"].split("-")[0]
                y, m, d  = data["releaseDate"].split("-")
                date_release = ".".join([ d, m, y ])
                label = soup.select_one("a.album-meta__link").text.strip()
                quantity_track = e
                total_duration = soup.select_one("span.album-about__item--duration").text.strip()
                album_name = data['name'].strip()
                genre = [x.text for x in soup.select("li.album-about__item") if "Genre" in x.text]
                genre = genre[0].strip().split("\n")[-1].strip()

                sheet_ranges = wb["Music"]
                sheet_ranges.append([title, image, table, author, date, date_release,
                                                label, quantity_track, total_duration, album_name, genre])
                self.message_send("processing left count: {}".format(len(urls) - e2))
            except:
                self.message_send("Error {}".format( url ))
        wb.save(NAME_FILE)
        self.message_send("[Successful] saved to {}".format(NAME_FILE))


if __name__ == "__main__":
    start = Qobuz()
    start.main()




from bs4 import BeautifulSoup
from bs4.element import Tag
from models import Celeb, CelebRole
from urllib3 import PoolManager
from urllib3.response import HTTPResponse
import urllib3 as urllib
import re
import json
from typing import List, Dict
import os
import multiprocessing
from multiprocessing import Process, Pool

class CelebSpyder():
    """
    This is a web spider class that crawls 'https://www.the-numbers.com' for top grossing celebrity film stars.
    usage:
        ```
        spyder = CelebSpyder()
        spyder.get_data()
        celeb_data  = spyder.celeb_list
        ```
    """

    def _process_chunk(self, celebs: List[Celeb]):
        return list(map(lambda celeb: self._parse_celeb(celeb), celebs))

    # Controller function.
    def get_data(self, num_processes:int=0):
        """
        Get list of celebrity objects.
        @param num_processes (int) the number of processors to use. If '0', uses all available CPUs.
        @return List[Celeb]
        """

        self.__log('Getting celebrity profiles...')

        # 1. Get list of celebs from HTML.
        if not os.path.exists(self._start_page_path):
            html_page = self.__get_html(url=self._celeb_list_url)
            self._start_page_path = self.__save_file(html_page, self._start_page_path)

        celeb_rows_html: List[Tag] = self._parse_celeb_list_html(path=self._start_page_path)

        if len(celeb_rows_html) == 0:
            raise Exception("Error getting list of celebrities from HTML.")

        # 2. Create list of celeb objects.
        celeb_list: List[Celeb] = list(map(lambda row: self._create_celeb(row), celeb_rows_html))

        if len(celeb_list) == 0:
            raise Exception("Error creating list of celebrity objects.")

        # 3. Split workload into N processes
        
        if num_processes == 0:
            num_processes = multiprocessing.cpu_count()

        list_len = len(celeb_list)
        n = 25
        chunks = [celeb_list[i:i + n] for i in range(0, list_len, n)]
        procs = [] 
        for chunk in chunks:
            p = Process(target=self._process_chunk, args=(chunk,))
            procs.append(p)
            p.start()

        for proc in procs:
            proc.join()
        
            
        self.__log(str.format('Completed retreiving celebrity profiles from {0}.', self._celeb_list_url))

    # region helper functions

    def __init__(self, celeb_list_url: str, page_num: int = 1, debug: bool=False):
        """
        Entry point for class. Init local vars here.
        """
        self._celeb_list_url: str = celeb_list_url
        self._start_page_path = str.format('./html/celebs_{0}.html', str(page_num))
        self.celeb_list: List[Celeb] = []
        self.debug = debug
        self._imdb_url = "https://www.imdb.com"

    def __log(self, msg: str):
        if self.debug:
            print(msg)

    def __save_file(self, contents: str, output_path: str) -> str:
        """
        Writes text contents to a file path.
        @param contents (str)
        @param output_path (str)
        @returns output_path (str)
        """
        try:
            with open(output_path, 'w', encoding='utf8') as output:
                output.write(contents)
                output.close()

            return output_path
        except Exception as e:
            raise e
    
    def __get_html(self, url: str) -> str:
        """
        Gets the raw HTML from a web page URL.
        @param url (str)
        @returns html (str)
        """
        try:
            http: PoolManager = urllib.PoolManager()
            res: HTTPResponse = http.request('GET', url)
            html = res.data.decode('utf-8')
            return html
        except Exception as e:
            raise e

    def __trim(self, s: str) -> str:
        """
        Removes leading/trailing white space from string.
        @param s (str)
        @returns str
        """
        return re.sub(r'\s+', ' ', re.sub(r'(^\s+|\s+$|\r\n+|\n+|\&nbsp\;+)', '', s))

    def __to_num(self, s: str) -> str:
        """
        Converts str to integer.
        @param s (str)
        @returns int
        """
        return int(re.sub(r'\D', '', self.__trim(s)))

    # endregion

    # region HTML functions

    def _parse_celeb_list_html(self, path: str) -> List[Tag]:
        """
        Parses the HTML for a celebrity list page URL into a list of Celeb objects.
        @param path (str) - the file path to a local HTML page.
        @returns Celeb
        """
        self.__log(str.format('Parsing celeb list from {0}...', path))
        celeb_rows: List[Tag] = None
        try:
            with open(path, 'r', encoding='utf-8') as html_page:
                soup: BeautifulSoup = BeautifulSoup(html_page, 'html.parser')
                celeb_list_container: Tag = soup.find_all('div', attrs={'id': 'page_filling_chart'})
                celeb_rows = celeb_list_container[1].find('center').find('table').find('tbody').find_all('tr')
                html_page.close()
                self.__log(str.format('Parsed celeb list from {0}.', path))
                return celeb_rows
        except Exception as e:
            raise e

    def _create_celeb(self, tr: Tag) -> Celeb:
        cells = tr.find_all('td')
        celeb = Celeb()
        celeb.Rank = self.__to_num(cells[0].text)
        celeb.FullName = self.__trim(cells[1].find('a').text) 
        celeb.DomesticBoxOfficeRevenue = self.__to_num(cells[2].text)
        celeb.AverageDomesticBoxOfficeRevenue = self.__to_num(cells[4].text)
        return celeb

    def _parse_celeb(self, celeb: Celeb) -> Celeb:
        """
        Create instance of Celeb from parsed HTML.
        @param tr (Tag)
        @returns (Celeb)
        """

        filename = str.format('./JSON/{0}.json', re.sub(r'[^a-zA-Z]', '', celeb.FullName))

        if os.path.exists(filename):
            return celeb

        def _export_json(celeb_obj: Celeb):
            # Export to JSON
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(celeb_obj.toJson(indent=4))
                file.close()

        self._search_imdb(celeb)
        self._parse_celeb_profile_html(celeb)
        _export_json(celeb)

        self.__log(str.format('Created Celeb object for {0}.', celeb.FullName))
        return celeb

    def _search_imdb(self, celeb: Celeb) -> Celeb:
        """
        Search IMDB by celebrity's full name if result doesn't already exist locally. 
        Return first result.
        Saves HTML to local folder.
        @param celeb (Celeb)
        @returns output_path (str)
        """
        celeb_name_clean: str = re.sub(r'\W', '', celeb.FullName)
        output_path: str = str.format("./html/imdb_profiles/{0}.html", celeb_name_clean)

        if not os.path.exists(output_path):
            self.__log(str.format('Downloading HTML from IMDB for {0}...', celeb.FullName))
            imdb_base_url: str = self._imdb_url
            celeb_name_param: str = re.sub(r'\s', '+', celeb.FullName)
            imdb_search_url = str.format("{0}/find?s=nm&q={1}&ref_=nv_sr_sm", imdb_base_url, celeb_name_param)
            celeb.DataSourceUrl = imdb_search_url
            search_results_html: str = self.__get_html(imdb_search_url)
            soup = BeautifulSoup(search_results_html, 'html.parser')
            celeb_url_list: List[Tag] = soup.select("div#main table.findList > tr.findResult:first-child > td.result_text > a:first-child")
            if len(celeb_url_list) > 0:
                celeb_url = str.format("{0}{1}", imdb_base_url, celeb_url_list[0]['href'])
                celeb_profile_html: str = self.__get_html(celeb_url)
                self.__save_file(celeb_profile_html, output_path)
                self.__log(str.format('IMDB HTML retreived for {0}.', celeb.FullName))
            else:
                self.__log(str.format('Could not retreive IMDB HTML for {0}.', celeb.FullName))
        else:
            self.__log(str.format('IMDB HTML already exists for {0}.', celeb.FullName)) 
                
        self.__log(str.format('Retrieved IMDB HTML for {0} at {1}.', celeb.FullName, output_path))  
        celeb.LocalDataSourcePath = output_path    
        return celeb

    def _parse_celeb_profile_html(self, celeb: Celeb) -> Celeb:
        """
        Parses the HTML for a celebrity profile page URL into an instance of Celeb.
        @param celeb (Celeb)
        @param profile_html (str)
        @returns Celeb
        """  

        with open(celeb.LocalDataSourcePath, 'r', encoding='utf-8') as profile_html:    
            soup = BeautifulSoup(profile_html, 'html.parser')

            # Photo Url
            img: Tag = soup.select_one("img#name-poster")
            if img:
                celeb.PhotoUrl = img['src']

            # Date of Birth
            dob: Tag = soup.select_one("div#name-born-info > time")
            if dob:
                celeb.DOB = dob['datetime']

            # Born in
            born_in: Tag = soup.select_one("div#name-born-info > a")
            if born_in:
                celeb.BornIn = born_in.text

            # Date of Death
            dod: Tag = soup.select_one("div#name-death-info > time")
            if dod:
                celeb.DOD = dod['datetime']

            # Gender
            actor = soup.select_one("a[href='#actor']")
            actress = soup.select_one("a[href='#actress']")
            if actor:
                celeb.Gender = 'Male'
            elif actress:
                celeb.Gender = 'Female'

            # Height
            height: Tag = soup.select_one("div#details-height")
            if height:
                ht = self.__trim( height.text )
                htm: List[str] = re.findall(r'\(\d\.\d+\sm\)', ht)
                if len(htm) > 0:
                    celeb.Height = float(re.sub(r'[^0-9\.]', '', htm[0]))

            # Atrological Sign
            sign = soup.select_one("div#dyk-star-sign > a")
            if sign:
                celeb.AstrologicalSign = self.__trim( sign.text )

            # Trademark
            trademark = soup.select_one("div#dyk-trademark")
            if trademark:
                tm = re.findall(r'(?<=\</h4\>)(.*)(?=\<span)', str(trademark).replace('\n', ''))
                if len(tm) > 0:
                    celeb.Trademark = self.__trim( tm[0] )
            
            # Awards
            awards = [span for span in soup.select("span.awards-blurb") if re.search(r'(wins|nominations)', span.text)]
            if len(awards) > 0:
                wins = re.findall(r'\d+(?=\swins)', awards[0].text)
                if len(wins) > 0:
                    celeb.AwardsWins = int(wins[0])

                nominations = re.findall(r'\d+(?=\snominations)', awards[0].text)
                if len(nominations) > 0:
                    celeb.AwardNominations = int(nominations[0])

            # Roles
            celeb.Roles = []
            for row in soup.select("div#filmography div.filmo-row"):
                celeb.Roles.append(self._parse_film_html(row))

            # celeb.Roles = list(map(lambda row: self._parse_film_html(row), soup.select("div#filmography div.filmo-row"))) 

            self.__log(str.format('Parsed HTML profile for {0}.', celeb.FullName))
            profile_html.close()
            
        return celeb

    def _parse_film_html(self, row: Tag) -> CelebRole:
        role = CelebRole()

        # CharacterName
        # Use Regex look behind and look ahead to get all characters between <br/> and <div>
        role_el = re.findall(r'(?<=\<br/\>)(.*)(?=\<)', str(row).replace('\n', ''))
        if len(role_el) > 0:
            role_name = role_el[0]
            if len(re.findall(r'\<div', role_name)) > 0:
                role_name = role_name.split('<div')[0]          
            role.CharacterName = self.__trim(role_name)

        # Year
        yr: Tag = row.select_one("span.year_column")
        if yr:
            role.Year = self.__trim(yr.text)

        # FilmTitle
        title: Tag = row.select_one("b > a")
        if not title:
            return role

        role.FilmTitle = self.__trim( title.text )
        self.__log(str.format("Parsing Film Details for {0}...", role.FilmTitle))

        # FilmUrl
        role.FilmUrl = str.format("{0}{1}", self._imdb_url, self.__trim(title['href']))

        # Get film details from IMDB URL       
        film_path = str.format('./html/imdb_films/{0}.html', re.sub(r'[^a-zA-Z0-9]', '', role.FilmTitle))

        if not os.path.exists(film_path):
            film_html = self.__get_html(role.FilmUrl)
            self.__save_file(film_html, film_path)
        
        with open(film_path, 'r', encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'html.parser')
            role.Directors = []
            role.Writers = []
            role.Stars = []
            role.Genres = []
            role.ProductionCompanies = []
            role.PlotKeywords = []

            for item in soup.select("div.plot_summary div.credit_summary_item"):
                h4 = item.select_one("h4")

                # Directors
                if h4 and re.search(r'^Director', h4.text):
                    for director in item.select("a"):
                        if director.text not in role.Directors:
                            role.Directors.append(director.text)
                # Writers
                elif h4 and re.search(r'^Writer', h4.text):
                    for writer in item.select("a"):
                        if writer.text not in role.Writers:
                            role.Writers.append(writer.text)
                # Stars
                elif h4 and re.search(r'^Star', h4.text):
                    for star in item.select("a"):
                        if not re.search(r'^See\s', star.text) and star.text not in role.Stars:
                            role.Stars.append(star.text)

                # Metascore
                metascore = soup.select_one("div.metacriticScore > span")
                if metascore:
                    role.Metascore = int(metascore.text)
            
                for review in soup.select("div.titleReviewBarItem span.subText > a"):
                # UserReviews
                    if re.search(r'\d+\suser', review.text):
                        role.UserReviews = int(re.sub(r'\D', '', review.text))

                # CriticReviews
                    if re.search(r'\d+\scritic', review.text):
                        role.CriticReviews = int(re.sub(r'\D', '', review.text))

                # Popularity
                for item in soup.select("div.titleReviewBarSubItem"):
                    for div in item.select("div"):
                        if re.search(r'Popularity', div.text):
                            popularity = item.select_one("div span.subText")
                            if popularity:
                                role.Popularity = int(re.sub(r'\D', '', re.findall(r'\d+\n', popularity.text)[0] ))
                
                # PlotKeywords
                for item in soup.select("div#titleStoryLine > div > a > span.itemprop"):
                    kw = re.sub(r'\s+', ' ', re.sub(r'(\n)', '', item.text))
                    if kw not in role.PlotKeywords:
                        role.PlotKeywords.append(kw)

                # Genres
                for item in soup.select("div#titleStoryLine > div"):
                    h4 = item.select_one("h4")
                    if h4 and re.search(r'Genre', h4.text):
                        for genre in item.select("a"):
                            ge = re.sub(r'(^\s+|\s+$)', '', genre.text)
                            if ge not in role.Genres:
                                role.Genres.append(ge)
                # MotionPictureRating
                    elif h4 and re.search(r'^Motion Picture Rating', h4.text):
                        rating = item.select_one("span")
                        if rating:
                            role.MotionPictureRating = rating.text

                # ReleaseDate
                for item in soup.select("div#titleDetails > div"):
                    h4 = item.select_one("h4")
                    if h4 and re.search(r'^Release Date', h4.text):
                        release_date = re.findall(r'\d{1,2}\s.*\s\d{4}', item.text)
                        if len(release_date) > 0:
                            role.ReleaseDate = release_date[0]
                # Budget
                    elif h4 and re.search(r'^Budget', h4.text):
                        budget = re.findall(r'[\$0-9,]+', item.text)
                        role.Budget = int(re.sub(r'[^0-9]', '', budget[0]))
                # OpeningWeekend
                    elif h4 and re.search(r'^Opening Weekend', h4.text):
                        opening = re.findall(r'[\$0-9,]+', item.text)
                        role.OpeningWeekend = int(re.sub(r'[^0-9]', '', opening[0]))
                # Gross
                    elif h4 and re.search(r'^Gross', h4.text):
                        gross = re.findall(r'[\$0-9,]+', item.text)
                        role.Gross = int(re.sub(r'[^0-9]', '', gross[0]))
                # CumulativeWorldwideGross
                    elif h4 and re.search(r'^Cumulative Worldwide Gross', h4.text):
                        cumlative = re.findall(r'[\$0-9,]+', item.text)
                        role.CumulativeWorldwideGross = int(re.sub(r'[^0-9]', '', cumlative[0])) 
                # ProductionCompanies
                    elif h4 and re.findall(r'^Production Co', h4.text):
                        for a in item.select("a"):
                            if not re.search(r'^See\s', a.text):
                                pc = re.sub(r'(^\s+|\s+$)', '', a.text)
                                if pc not in role.ProductionCompanies:
                                    role.ProductionCompanies.append(pc)
                # RuntimeMinutes
                    elif h4 and re.findall(r'^Runtime', h4.text):
                        runtime = item.select_one("time")
                        if runtime:
                            role.RuntimeMinutes = int(re.sub(r'[^0-9]', '', runtime.text))
            html.close()

        self.__log(str.format("Parsed Film Details for {0}.", role.FilmTitle))

        return role
    # end (def _parse_film_html())
     

    # endregion

# Get first 5 pages of celebrities
if __name__ == '__main__':
    start_url="https://www.the-numbers.com/box-office-star-records/domestic/lifetime-acting/top-grossing-leading-stars"
    for page_num in range(0, 5):
        url = start_url if page_num < 1 else str.format('{0}/{1}01', start_url, page_num)
        print(url)
        spyder = CelebSpyder(celeb_list_url=url, page_num=page_num, debug=True)
        spyder.get_data()
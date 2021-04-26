import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class BookEntry:
    def __init__(self, title, author, isbn, date_of_publication, call_number):
        """ Constructor for BookEntry encompassing Title, Author, ISBN, Date of Publication, and Call Number. """
        self.title = title
        self.author = author
        self.isbn = isbn
        self.date_of_publication = date_of_publication
        self.call_number = call_number

    def __str__(self):
        """ Represents the BookEntry class as a string. """
        return "Title: {}\nAuthor: {}\nISBN: {}\nDate Of Publication: {}\nCall Number: {}".format(self.title, self.author, self.isbn, self.date_of_publication, self.call_number)

class BibliographicalAPI:
    max_retries = 5

    def __init__(self, endpoint_url, api_key, format="json"):
        """ Constructor for BibliographicalAPI encompassing Endpoint URL, API Key, and Format. """
        self.__endpoint_url = endpoint_url
        self.__api_key = api_key
        self.__params = {"apikey": api_key, "format": format}

    @staticmethod
    def __cleanStringData(data):
        """
        Cleans string data of unnecessary characters.

        String Data from API may contain characters unsuitable for presentation purposes,
        and in some cases may be an unexpected input such as NULL (or None) or may not be a string at all. 
        The string is cleaned of unnecessary characters ('/', '.', ',', '[', ']', ':', ' '). If the inputted data
        is NULL (or None) or not a string, the string "N/A" will be returned.

        Parameters
        ----------
        data : str
            String data needed to be cleaned.

        Returns
        -------
        str
            Cleaned string data.

        """

        if data == None:
            return "N/A"

        if type(data) == str:
            # Clean String of any unnecessary characters
            excluded_chars = ['/', '.', ',', '[', ']', ':', ' ']
            if data[-1] in excluded_chars:
                data = data[:-1]
            
            if data[0] in excluded_chars:
                data = data[1:]
            
            # Remove leading or trailing whitespace
            data = data.strip()

            return data
        else:
            return "N/A"
    
    @staticmethod
    def sortRecordsByTitle(records, descending=False):
        """
        Sorts records by title.

        Records are sorted by the title field of the BookEntry object and returned as a list of BookEntry
        in ascending order. If descending flag is checked, a sorted list of BookEntry is returned in descending order.

        Parameters
        ----------
        records : list
            List of BookEntry records to be sorted by title.

        descending: boolean
            Will sort records in descending order if value is True, otherwise, ascending order.
            Default value is False.

        Returns
        -------
        list
            List of BookEntry records sorted by title.

        """

        if records is None or type(records) != list:
            return []
        
        return sorted(records, key=(lambda book: book.title), reverse=descending)

    @staticmethod
    def sortRecordsByPublishDate(records, descending=False):
        """
        Sorts records by publish date.

        Records are sorted by the title field of the BookEntry object and returned as a list of BookEntry
        in ascending order. If descending flag is checked, a sorted list of BookEntry is returned in descending order.

        Parameters
        ----------
        records : list
            List of BookEntry records to be sorted by publish date.

        descending: boolean
            Will sort records in descending order if value is True, otherwise, ascending order.
            Default value is False.

        Returns
        -------
        list
            List of BookEntry records sorted by publish date.

        """

        if records is None or type(records) != list:
            return []

        return sorted(records, key=(lambda book: int(book.date_of_publication)), reverse=descending)

    def getRecordsFromAPI(self, verbose=False):
        """
        Gets records and associated bibliographical data from endpoint url and bibliographical API.

        Using the endpoint url supplied and the bibliographical API, records are fetched and bibliograqphical
        data isolated to be represented as a BookEntry object. A list of BookEntry objects are returned upon completion.

        Parameters
        ----------
        self : BibliographicalAPI
            BibliographicalAPI class with the associated endpoint url, api key, and format.

        verbose: boolean
           Indicates whether to display output to console.

        Returns
        -------
        list
            List of BookEntry records with bibliographical data gathered from endpoint url and bibliographical API.

        """
        verboseprint = print if verbose else lambda *a, **k: None # Verbose Print For Debug Purposes
        records = [] # Records of Bibliographical Data

        verboseprint("Establishing new Session for API Calls.")
        # Begin new session for queries into API
        with requests.Session() as session:
            session.params = self.__params # Set API call parameters
            
            # Establish retry attempts for status codes 400 and 401
            retries = Retry(total=BibliographicalAPI.max_retries, backoff_factor=1, status_forcelist=[400, 401])
            session.mount("https://", HTTPAdapter(max_retries=retries))

            verboseprint("Obtaining ILS Member Data from Endpoint URL.")
            ils_data = session.get(self.__endpoint_url) # GET Request to Endpoint URL
            ils_decoded_json = ils_data.json() # Decode ILS data from JSON into Dictionary
            ils_member_items = ils_decoded_json["member"] # ILS members to process
            ils_total_record_count = ils_decoded_json["total_record_count"]

            verboseprint("Total Record Count: " + str(ils_total_record_count))

            # Isolate the bibliographic data from each entry in the dictationary
            verboseprint("Isolating bibliographic data from ILS Member Data.")
            current_record_index = 1
            for member in ils_member_items:
                member_url =  member["link"] # Link to bibliographic data

                if member_url:
                    verboseprint("[Record {}] Member_Url:\n{}\n".format(current_record_index, member_url))

                    # GET Request to bibliographic link
                    verboseprint("[Record {}] Performing GET Request to Member Url".format(current_record_index))
                    bib_data = session.get(member_url)
                    
                    verboseprint("[Record {}] Status Code {}".format(current_record_index, bib_data.status_code))

                    if bib_data:
                        verboseprint("[Record {}] Decoding Response from JSON.".format(current_record_index))
                        bib_decoded_json = bib_data.json() # Decode Bibliographic data from JSON into Dictionary

                        verboseprint("[Record {}] Fetching Bibliographic Data.".format(current_record_index))
                        title = BibliographicalAPI.__cleanStringData(bib_decoded_json["bib_data"]["title"])
                        author = BibliographicalAPI.__cleanStringData(bib_decoded_json["bib_data"]["author"])
                        isbn = BibliographicalAPI.__cleanStringData(bib_decoded_json["bib_data"]["isbn"])
                        date_of_publication = BibliographicalAPI.__cleanStringData(bib_decoded_json["bib_data"]["date_of_publication"])
                        call_number = BibliographicalAPI.__cleanStringData(bib_decoded_json["holding_data"]["call_number"])
                        
                        # Creating new BookEntry object.
                        verboseprint("[Record {}] Creating new BookEntry object.".format(current_record_index))
                        book_entry = BookEntry(title, author, isbn, date_of_publication, call_number)

                        # Adding BookEntry to Results
                        verboseprint("[Record {}] Adding BookEntry to Results".format(current_record_index))
                        records.append(book_entry)

                        verboseprint("[Record {}] Outputting Bibliographical Data to Console.".format(current_record_index))
                        verboseprint("-" * 20)
                        verboseprint(book_entry)
                        verboseprint("-" * 20)
                    
                    current_record_index += 1
        return records


        



    

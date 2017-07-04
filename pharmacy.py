import requests
import untangle
import csv
import os

# Set your API key. Either store this in an environment variable called 'API_KEY', or amend the default value below
api_key = os.getenv('API_KEY', 'default_value')
base_url = f'http://v1.syndication.nhschoices.nhs.uk/organisations/pharmacies/all.xml?apikey={api_key}'

# Define the API page number to start from - set this to a high number (e.g. 380) if you just want to test against the
# last few pages
starting_page_number = 1

# Create an empty list to hold the pharmacy data we're going to collect
pharmacies = []


def store_services(entries: list) -> None:
    """
    Stores some key data from the XML for each pharmacy in an provided list and adds each object to our
    list of pharmacies. Takes a list of objects representing <entry> XML trees.
    """

    for entry in entries:
        org_name = entry.content.s_organisationSummary.s_name.cdata
        ods_code = entry.content.s_organisationSummary.s_odscode.cdata
        post_code = entry.content.s_organisationSummary.s_address.s_postcode.cdata
        coords = {
            'long': entry.content.s_organisationSummary.s_geographicCoordinates.s_longitude.cdata,
            'lat': entry.content.s_organisationSummary.s_geographicCoordinates.s_latitude.cdata,
        }
        id_url = entry.id.cdata
        # print(f'{org_name} - {ods_code}')
        
        # Create a dictionary for that pharmacy's data
        pharmacy = {
            'name': org_name,
            'odscode': ods_code,
            'id': id_url,
            'postCode': post_code,
            'coords': coords
        }
        
        # Add the pharmacy dictionary to the pharmacies list
        pharmacies.append(pharmacy)


def get_all_pharmacies() -> None:
    """
    Iterate through the pages of pharmacy data from the Choices API and then call store_services() on each page
    """
    
    page_number = starting_page_number

    # Perform a GET request against the Choices API using the base URL + the starting page number as a URL param
    result = requests.get(base_url + f'&page={page_number}')
    
    # Parse the returned XML into an object representing the XML structure
    document = untangle.parse(result.text)
    
    # Define the contents of the <feed> element as its own object
    feed = document.feed
    
    # Define the <link> elements into their own object
    urls = feed.link
    
    # Create an empty dictionary to store the URLs from the XML response
    url_list = {}
    
    # For each <link> element in our urls object
    for url in urls:
        # Add it to our dictionary with the rel attribute as the key, and the href attribute as the value
        url_list[url['rel']] = url['href']
      
    # Following code wrapped in a try/except so as to catch the KeyError when we reach the last page
    try:
        # Now iterate through the pages of results from the API, each time checking for the presence of a 'next' link in
        # our dictionary of URLs.
        while url_list['next']:

            # Perform a GET against the API using the URL from the 'next' link in the previous page
            result = requests.get(url_list['next'],
                                  headers={'Content-Type': 'application/xml',
                                           'Accept': 'application/xml'})
            
            # Parse the returned XML into an object called 'document'
            document = untangle.parse(result.text)
            
            # Define the contents of the <feed> element as its own object
            feed = document.feed
            
            # Define the list of <entry> elements as their own object (list)
            entries = feed.entry

            # Define the list of <link> elements as their own object (list)
            urls = feed.link

            # Create an empty dictionary to store the URLs from the XML response
            url_list = {}
            # For each <link> element in our urls object
            for url in urls:
                # Add it to our dictionary with the rel attribute as the key, and the href attribute as the value
                url_list[url['rel']] = url['href']
            
            # Call the store_services method passing in the list of entries that we have just extracted from the
            # results page XML. We will do this for each results page that we iterate through.
            store_services(entries)
            
    # Catch a KeyError exception as this indicates we have reached the last page (as there is no 'next' link type)
    except KeyError:
        print('Finished getting list of all pharmacies')
        

def update_eps_statuses() -> None:
    """
    Iterate through the list of pharmacies and get the epsEnabled status for each individual pharmacy.
    Add it to respective pharmacy object in the pharmacies list. We have to do this separately to the first retrieval
    of pharmacy data as the flag we are after is stored in the /overview subset of data for each pharmacy which we can
    only access one by one.
    """
    
    print('Getting EPS status for all pharmacies in list')
    
    # For each pharmacy in the list of pharmacies we compiled...
    for pharmacy in pharmacies:
        
        # Get the ID url for that pharmacy instance
        id_url = pharmacy['id']
        
        # Append /overview.xml to the end to get us the detail containing EPS status, and add the api key on the end
        url = f'{id_url}/overview.xml?apikey={api_key}'
        
        # Perform a GET request against the URL
        results = requests.get(url)

        # Take the returned XML and parse it into an object
        document = untangle.parse(results.text)
        
        # Pull the contents of the <content> element into its own object
        content = document.feed.entry.content
        
        # Get the value from the <isEpsEnabled> element
        eps_enabled = content.s_overview.s_isEpsEnabled.cdata
        
        # Convert it to a boolean
        eps_enabled = bool(eps_enabled)
        
        # Update the pharmacy object in our list with the boolean epsEnabled flag
        pharmacy['epsEnabled'] = eps_enabled
    
    print('Finished getting EPS status for all pharmacies')


def write_to_csv() -> None:
    """
    Write all of the pharmacy data we've collected to a CSV file in the local directory
    """
    # Set the filename for the CSV file
    csv_file_name = 'pharmacies.csv'
    
    # Use a context manager to open the destination CSV file in writable mode  and hold it open whilst we're
    # working with it. CSV file will close as soon as the code within the with block has completed.
    with open(csv_file_name, 'w', newline='') as csvfile:
        
        # Create a CSV writer instance using the open CSV file, set the delimiter character, and the quote character.
        # QUOTE_MINIMAL tells it to only quote fields that have special characters such as the delimeter or quotechar
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        # For each record in our list of pharmacies, write a line to the CSV file
        for record in pharmacies:
            csv_writer.writerow([f"{record['name']}",
                                 f"{record['odscode']}",
                                 f"{record['epsEnabled']}",
                                 f"{record['postCode']}",
                                 f"{record['coords']['lat']}",
                                 f"{record['coords']['long']}"])
            
        print('Finished writing CSV')

print('Beginning download of pharmacy data')

get_all_pharmacies()
update_eps_statuses()
write_to_csv()

print('Finished!')



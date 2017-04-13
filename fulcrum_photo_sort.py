import os
from fulcrum import Fulcrum


#Ask user for API key, then create Fulcrum access object
fulcrumKey = raw_input('Enter the Fulcrum API key: ')
fulcrum = Fulcrum(key=fulcrumKey)


#Get resources from Fulcrum.
#Note: the string passed here is the fulcrum_id of the SWPPP Inspect app/form.
form = fulcrum.forms.find('b2029e78-4362-4f3f-805b-f615f3f8337e')
records = fulcrum.records.search(url_params={'form_id': 'b2029e78-4362-4f3f-805b-f615f3f8337e'})

#Define output directory.  Script will write photos here.
outDir = 'H:\\py\\output\\'

#Define functions.

def form_check(search_dict, field='type', fieldvalue='PhotoField'):
    """
    Searches a Fulcrum form for elements with specific attributes.
    
    Returns a dict of ('key':'data_name') pairs.
    
    Default search is for 'type' : "PhotoField".
    Could also search for different element attribute,
    such as 'hidden' : False .
    """
    output = {}

    #Iterate over the key:value pairs in the input dict.
    for key, value in search_dict.iteritems():

        #If a match is found, update output dict with 'key' and 'data_name'.
        if key == field and value == fieldvalue:
            updatedict = {search_dict['key']: search_dict['data_name']}
            output.update(updatedict)

        #If another dict is found, check this dict.
        elif isinstance(value, dict):
            results = form_check(value)
            output.update(results)

        #If a list is found, check the list for dicts, then check those.
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = form_check(item)
                    output.update(more_results)

    return output


def get_photos(record, fieldDict,site=None):
    """
    Searches a Fulcrum record for photos.  Returns a list of dicts.

    Output is of the form:
    [{'photo_id': 'xxxx','photo_type': 'yyyy', 'photo_site': 'zzzz'}]
    
    Photo_id will match the filename when photos are retrieved from fulcrum.
    Photo_type will match the photo data_name in Fulcrum data.
    Photo_site will match the custom form element with the key provided
    in the function definition.  As written, the key references a facility_name
    field in the SWPPP Inspect form/app.
    

    Input fieldDict should be output from form_check(form).
    Input record should be i in records['records'][i].
    """

    
    fields = fieldDict.keys()
    photos_found = []

    #Derive the site name from the input record.
    #Note: Site name key must be determined manually if form is changed.
    if site == None:
        site = record['form_values']['e763']
        
    #Iterate over key-value pairs in the record.
    for key, value in record.iteritems():

        #If a key is matched, extract and write the id, type and site to a dict
        if key in fields:
            for item in value:
                extract = {'photo_id': item['photo_id'],
                           'photo_type': fieldDict[key],
                           'photo_site': site}
                photos_found.append(extract)
        
        #If another dict is found, check it for photos.        
        elif isinstance(value, dict):
            results = get_photos(value, fieldDict, site)
            for result in results:
                photos_found.append(result)

        #If a list is found, check it for dicts, check dicts for photos.
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_photos(item, fieldDict, site)
                    for another_result in more_results:
                        photos_found.append(another_result)

    return photos_found


#Identify photo fields for the SWPPP Inspect form

fieldDict = form_check(form)

#Generate a list of photos for the entire app.

photoList = []

for record in records['records']:
    updateList = get_photos(record, fieldDict)
    photoList.extend(updateList)

#Write photos to directories

#Create site directories and sub directories in output directory.

#Create folder aliases for photo types.
aliasDict = {}
for item in fieldDict.values():
    userInput = raw_input(('Enter folder name for type ' + str(item) + ':')) 
    entry = {item: userInput}
    aliasDict.update(entry)

#Create site directories using known record name field, and
#Create type subdirectories using user-provided aliases
for record in records['records']:
    site = record['form_values']['e763']
    for item in fieldDict.values():
        path = os.path.join(outDir, site, aliasDict[item])
        if not os.path.exists(path):
            os.makedirs(path)

#Download photo media and write to directories.
for photo in photoList:
    #define and navigate to relevant subdirectory
    site = photo['photo_site']
    subtype = aliasDict[photo['photo_type']]
    os.chdir(os.path.join(outDir,site,subtype))

    #get the photo media from Fulcrum
    photo_id = photo['photo_id']
    media = fulcrum.photos.media(photo_id, 'original')

    #write the media to disk
    with open('{}.jpg'.format(photo_id), 'wb') as f:
        f.write(media)
        f.close()

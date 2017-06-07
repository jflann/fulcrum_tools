from fulcrum import Fulcrum
import os
import sys

import pprint
import requests
requests.packages.urllib3.disable_warnings()

#Ask user for API key, then create Fulcrum access object
fulcrumKey = raw_input('Enter the Fulcrum API key: ')
fulcrum = Fulcrum(key=fulcrumKey)


def ask_yesno(question):
    '''
    Ask a the user a yes/no question.  Returns a boolean.
    '''
    class YesNoError(Exception):
        pass

    while True:
        try:
            yesno = raw_input('{} (Y/N): '.format(question))
            if yesno.lower() in ['yes','y']:
                output = True
                break
            elif yesno.lower() in ['no','n']:
                output = False
                break
            else:
                raise YesNoError('Please answer with yes or no.')
        except YesNoError as e:
            print e.args[0]
    return output

def get_key_labels(search_dict, fields):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in search_dict.iteritems():
        
        if value in fields:
            if 'label' in search_dict.keys():
                fields_found.append(search_dict['label'])

        elif isinstance(value, dict):
            results = get_key_labels(value, fields)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_key_labels(item, fields)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found

def get_output_dir():
    '''
    Asks user for a directory and creates it if it does not exist.
    Outputs a directory path.
    '''

    class YesNoError(Exception):
        pass

    while True:
        try:
            user_input = raw_input("Specify the path to an output directory: ")
            outDir = os.path.abspath(user_input)
            print outDir
            if not os.path.exists(outDir):
                print 'Specified path {} does not exist.'.format(outDir)
                while True:
                    try:
                        create = raw_input('Do you wish to create this directory? (Y/N): ')
                        if create.lower() in ['yes','y']:
                            os.makedirs(outDir)
                            break
                        elif create.lower() in ['no','n']:
                            break
                        else:
                            raise YesNoError('Please answer with yes or no.')
                    except YesNoError as e:
                        print e.args[0]
                        
            if os.path.exists(outDir):
                break
            
                
        except:
            e = sys.exc_info()[0]
            pprint.pprint(e)

    print 'Output Directory set to {}. \n '.format(outDir)
    return outDir
            

#Scan forms and return name, id, and title_field_keys.

def create_formlist():
    '''
    Gets forms from Fulcrum and outputs a dictionary for each list.
    Dictionary will contain 'name', 'id', and 'title_field_keys'.
    '''
    
    forms = fulcrum.forms.search()['forms']
    output = []
    for form in forms:
        forminfo = {}
        for key in form:
            if key in ('name','id','title_field_keys'):
                forminfo[key]= form[key]
        output.append(forminfo)
        
    return output

#Ask user which form to use.

def which_form(formList):
    '''
    Asks the user which Fulcrum form (app) to search in.

    Requires list input from create_formlist().
    Outputs a dict element of input list.
    '''
    #Ask user to select from a list of forms
    print 'Which app do you wish to search?\n'
    i = 1
    for form in formList:
       print '({}). '.format(i) + form['name']
       i = i + 1
    print '\n'

    #Get user selection and test for validity
    while True:
        try:
            #Get input, test if int.
            user_input = int(raw_input("Enter the number of your selection:"))
            #Test if input in formList index.
            test = formList[user_input - 1]
            break
        except ValueError:
            print "Error: Please enter an integer."
        except IndexError:
            print 'Error: Please enter a number from {} through {}.'.format(
                                                range(len(formList))[1],
                                                range(len(formList))[-1] + 1
                                                )

    #Output selected list info as a dict
    index = user_input - 1
    print 'Selected:', '{}.\n'.format(formList[index]['name'])
    output = formList[index]

    return output

#Function to ask which media type(s) to download.

def which_media():
    '''

    '''
    choices = {
        '1':'photos',
        '2':'videos',
        '3':'audio',
        '4':'signatures',
        }
    class InputError(Exception):
        pass
    selection = []
    output = []
    print 'What do you wish to download?\n'
    for key, value in sorted(choices.iteritems()):
        print '({}). {}'.format(key, value)
    print '\n'

    while True:
        try:
            #Get user input and split it into a list, then convert to integers.
            user_input = raw_input('Enter the number(s) of your selection, separated by comma: ').split(',')
            print 'You entered', user_input, '\n'
            int_user_input = [ int(x) for x in user_input]
            
            #Test that user input is not longer than number of choices.    
            if len(int_user_input) > len(choices):
                raise InputError('Error: Number of inputs must be less than {}.'.format(len(choices)))
            
            #Test that user input has no duplicates.
            if len(int_user_input) != len(set(int_user_input)):
                raise InputError('Error: Selection must not include duplicates.')
            
            #Retrieve selection from list of choices and print it.
            for item in int_user_input:
                item = choices[str(item)]
                selection.append(item)   
            print 'Your selection is', selection
                
            break

        except InputError as e:
            print e.args[0]
        except ValueError:
            print 'Error: Please enter integers.'
        except KeyError:
            print 'Error: Please enter numbers from {} through {}.'.format(
                                                            range(len(choices))[1],
                                                            range(len(choices))[-1] + 1
                                                            )
    return int_user_input

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
            results = form_check(value, field, fieldvalue)
            output.update(results)

        #If a list is found, check the list for dicts, then check those.
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = form_check(item, field, fieldvalue)
                    output.update(more_results)

    return output



def get_selection_keys(selection):

    fieldtypes =   { '1': 'PhotoField',
                     '2': 'VideoField',
                     '3': 'AudioField',
                     '4': 'SignatureField' }
    mediamethods = { '1': 'photos',
                     '2': 'videos',
                     '3': 'audio',
                     '4': 'signatures'   }
    output = []
    for i in selection:
        keys = {}
        mediatype =  fieldtypes[str(i)]
        keys = form_check(form, field='type', fieldvalue=mediatype)
        if keys:
            entry = {mediamethods[str(i)]: keys}
            output.append(entry)
        else:
            print 'Warning: App does not contain {}.\n'.format(mediamethods[str(i)])

    return output

def get_storage_scheme(inputlist):
    '''

    '''

    class InputError(Exception):
        pass

    record_title = ", ".join(get_key_labels(form, selected_form['title_field_keys']))

    output = inputlist
    
    for row in inputlist:
        for mediatype, keys in row.iteritems():
            
            path1 = os.path.abspath(os.path.join(outDir,mediatype.title()))
            path2 = os.path.abspath(os.path.join(
                outDir,
                '%{}%'.format(record_title),
                mediatype.title()
                                    ))
            path3 = os.path.abspath(os.path.join(
                outDir,
                '%{}%'.format(record_title),
                '%{}_Subtype%'.format(mediatype.title())
                                ))
                                    
            print 'How do you wish to store {}?\n'.format(mediatype)
            print '(1). {}\n'.format(path1)
            print '(2). {}\n'.format(path2)
            print '(3). {}\n'.format(path3)
            print '\t*%{}_Subtype% are elements in:'.format(mediatype.title())
            for i in inputlist:
                if mediatype in i:
                    print '\t', i[mediatype].values(), '\n'

        #Get user choice and test for validity
        while True:
            try:
                choice = raw_input('Enter your choice: ')
                int_choice = int(choice)
                #Test that user input is not longer than number of choices.    
                if int_choice not in [1,2,3]:
                    raise InputError('Error: Please enter 1, 2, or 3.')
                break
            except ValueError:
                print 'Please enter an integer.'
            except InputError as e:
                print e.args[0]

        #Write a dict entry for 'mode' for each mediatype
        row['mode'] = choice
    print 'Working ...'
            
def recursive_search(record, mediatype, search_keys, record_title, mode):

    media_found = []
    keys = search_keys.keys()

    for key, value in record.iteritems():

        if key in keys:
            if isinstance(value, list):
                for item in value:
                    extract = {'fulcrum_id': item['{}_id'.format(mediatype.rstrip('s'))],
                               'data_name': search_keys[key],
                               'record_title': record_title,
                               'mode': mode,
                               'media_type': mediatype}
                    media_found.append(extract)
            elif isinstance(value, dict):
                extract = {'fulcrum_id': value['{}_id'.format(mediatype.rstrip('s'))],
                           'data_name': search_keys[key],
                           'record_title': record_title,
                           'mode': mode,
                           'media_type': mediatype}
                media_found.append(extract)


        #If another dict is found, check it for photos.        
        elif isinstance(value, dict):
            results = recursive_search(value, mediatype, search_keys, record_title, mode)
            for result in results:
                media_found.append(result)

        #If a list is found, check it for dicts, check dicts for photos.
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = recursive_search(item, mediatype, search_keys, record_title, mode)
                    for another_result in more_results:
                        media_found.append(another_result)
                        
    return media_found

                   
def media_find(records, selection_keys):

    output = []

    for record in records['records']:
        
        #Get record title.
        record_title_elements = []
        for i in selected_form['title_field_keys']:
            try:
                if isinstance(record['form_values'][i], (str, unicode)):
                    record_title_elements.append(record['form_values'][i])
                elif isinstance(record['form_values'][i], dict):
                    record_title_elements.append(record['form_values'][i]['choice_values'][0])
            except KeyError:
                record_title_elements.append('MISSING')
                
        if record_title_elements:
            record_title = ", ".join(record_title_elements)
        else:
            record_title = 'Unknown or missing title'

        #Looking at each dict in the selection_keys input, and then running the recursive search on the record.
        for eachdict in selection_keys:
            mode = eachdict['mode']
            for key in eachdict.keys():
                if key in ['photos','videos','audio','signatures']:
                    mediatype = key
            
            search_keys = eachdict[mediatype]
            #print search_keys
            #to do: run recursive search
            results = recursive_search(record, mediatype, search_keys, record_title, mode)
            if results:
                #pprint.pprint(results)
                output.extend(results)
            
    return output
                
            

            




def write_media(inputlist,outDir):
    '''
    inputlist = media_find()
    
    '''
    writecount = 0
    dlcount = 0
    
    for item in inputlist:

        #Define output path based on user-selected 'mode'.
        if item['mode'] == '1':
            dirpath = os.path.join(outDir,
                                   item['media_type'].title()
                                   )
        elif item['mode'] == '2':
            dirpath = os.path.join(outDir,
                                   item['record_title'],
                                   item['media_type'].title()
                                   )
        elif item['mode'] == '3':
            dirpath = os.path.join(outDir,
                                   item['record_title'],
                                   item['data_name']
                                   )
        else:
            print 'mode not matched'
            print type(item['mode'])
        #Define output filename, and get media from fulcrum.
        if item['media_type'] == 'photos':
            filename = item['fulcrum_id'] + '.jpg'
            #media = fulcrum.photos.media(item['fulcrum_id'])
        elif item['media_type'] == 'videos':
            filename = item['fulcrum_id'] + '.mp4'
            #media = fulcrum.videos.media(item['fulcrum_id'])
        elif item['media_type'] == 'audio':
            filename = item['fulcrum_id'] + '.aac'
            #media = fulcrum.audio.media(item['fulcrum_id'])
        elif item['media_type'] == 'signatures':
            filename = item['fulcrum_id'] + '.jpg'
            #media = fulcrum.signatures.media(item['fulcrum_id'])

        if os.path.exists(dirpath):
            os.chdir(dirpath)
        else:
            os.makedirs(dirpath)
            os.chdir(dirpath)

        if not os.path.isfile(os.path.join(dirpath,filename)):
            dlcount = dlcount + 1
            if item['media_type'] == 'photos':            
                media = fulcrum.photos.media(item['fulcrum_id'])
            elif item['media_type'] == 'videos':
                media = fulcrum.videos.media(item['fulcrum_id'])
            elif item['media_type'] == 'audio':
                media = fulcrum.audio.media(item['fulcrum_id'])
            elif item['media_type'] == 'signatures':
                media = fulcrum.signatures.media(item['fulcrum_id'])
            
            with open(filename, 'wb') as f:
                f.write(media)
                f.close()


    print '{} files downloaded.'.format(str(dlcount))


        

        


#Test Instructions

outDir = get_output_dir()

formList = create_formlist()

selected_form = which_form(formList)
form_id = selected_form['id']
form = fulcrum.forms.find(form_id)
records = fulcrum.records.search(url_params={'form_id': selected_form['id']})

media_selection = which_media()

selection_keys = get_selection_keys(media_selection)

get_storage_scheme(selection_keys)

medialist = media_find(records, selection_keys)

write_media(medialist,outDir)

import subprocess
subprocess.Popen('explorer' + " {}".format(outDir))

raw_input('Press Enter to Quit')

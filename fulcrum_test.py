from fulcrum import Fulcrum
import os
import sys

import pprint


#Ask user for API key, then create Fulcrum access object
fulcrumKey = raw_input('Enter the Fulcrum API key: ')
fulcrum = Fulcrum(key=fulcrumKey)


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
            e = sys.exec_info()[0]
            pprint.pprint(e)

    print 'Output Directory set to {}.'.format(outDir)
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
    print 'Which app do you wish to search?'
    i = 1
    for form in formList:
       print '({}). '.format(i) + form['name']
       i = i + 1

    #Get user selection and test for validity
    while True:
        try:
            #Get input, test if int.
            user_input = int(raw_input("Enter the number of your selection: "))
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
    print 'Selected:', '{}.'.format(formList[index]['name'])
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
    print 'What do you wish to download?'
    for key, value in sorted(choices.iteritems()):
        print '({}). {}'.format(key, value)

    while True:
        try:
            #Get user input and split it into a list, then convert to integers.
            user_input = raw_input('Enter the number(s) of your selection, separated by comma: ').split(',')
            print 'You entered', user_input
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
    print int_user_input
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

    aliases =   { '1': 'PhotoField',
                  '2': 'VideoField',
                  '3': 'AudioField',
                  '4': 'SignatureField' }
    output = []
    for i in selection:
        keys = {}
        mediatype =  aliases[str(i)]
        keys = form_check(form, field='type', fieldvalue=mediatype)
        if keys:
            output.append(keys)
        else:
            print 'Form does not contain fields of type {}.'.format(mediatype)

    return output



#which_media()
    
    
#Get the selected form:

#form_id = which_form(create_formlist())['id']
#form = fulcrum.forms.find(form_id)

#keydict = get_selection_keys(which_media())
#pprint.pprint(keydict)





    

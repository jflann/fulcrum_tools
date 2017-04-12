from fulcrum import Fulcrum

import pprint


#Ask user for API key, then create Fulcrum access object
fulcrumKey = raw_input('Enter the Fulcrum API key: ')
fulcrum = Fulcrum(key=fulcrumKey)



#Scan forms and return name, id, and title_field_keys.

def create_formlist(fulcrum=fulcrum):
    
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
            user_input = int(raw_input("Enter the number of your selection: "))
            test = formList[user_input - 1]     #test if input is in list index
            break
        except ValueError:
            print "Error: Please enter an integer."
        except IndexError:
            print 'Error: Enter a number between {} and {}.'.format(
                                            range(len(formList))[1],
                                            range(len(formList))[-1] + 1)

    #Output selected list info as a dict
    index = user_input - 1
    print 'Selected:', '{}.'.format(formList[index]['name'])
    output = formList[index]

    return output

    
#Get the selected form:

form_id = which_form(create_formlist())['id']
form = fulcrum.forms.find(form_id)

pprint.pprint(form)
            

    

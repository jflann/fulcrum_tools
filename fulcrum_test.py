from fulcrum import Fulcrum

import pprint


#Ask user for API key, then create Fulcrum access object
fulcrumKey = raw_input('Enter the Fulcrum API key: ')
fulcrum = Fulcrum(key=fulcrumKey)

#Get all forms.
forms = fulcrum.forms.search()['forms']

#Scan forms and return name, id, and title_field_keys.
formList = []
for form in forms:
    forminfo = {}
    for key in form:

        if key in ('name','id','title_field_keys'):
            forminfo[key]= form[key]
    formList.append(forminfo)

#Ask user which form to use.

def which_form(formList):
    print 'Which app do you wish to search?'
    i = 1
    for form in formList:
       print '({}). '.format(i) + form['name']
       i = i + 1

    index = input('Enter selection: ') - 1
    print 'Selected:', '{}.'.format(formList[index]['name'])
    output = index

    return output

which_form(formList)
    

            

    

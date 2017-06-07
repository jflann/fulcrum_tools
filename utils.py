from fulcrum import Fulcrum
import os
import sys

import requests
from pprint import pprint as pp

requests.packages.urllib3.disable_warnings()

#Ask user for API key, then create Fulcrum access object
#fulcrumKey = raw_input('Enter the Fulcrum API key: ')
fulcrumKey = ''
fulcrum = Fulcrum(key=fulcrumKey)


form = fulcrum.forms.find('')
records = fulcrum.records.search(url_params={'form_id': ''})











class Form(object):

    def __init__(self, data):
        
        self.data = data['form']
        self.name = self.data['name']
        self.form_id = self.data['id']
        self.title_field_keys = self.data['title_field_keys']
        self.record_count = self.data['record_count']


    def keys(self, elements=None, key_value='data_name'):
        """
        Returns a dictionary of keys for all form elements,
        paired with a 'key_value' which defaults to the element's
        'data_name'.  Other opptu
        """

        if elements==None:
            elements=self.data['elements']
        result = {}
        for d in elements:
            entry = {d['key']:d[key_value]}
            result.update(entry)
            if 'elements' in d:
                more = self.keys(elements=d['elements'],key_value=key_value)
                result.update(more)        
        return result

    #keys = property(_get_keys)
            



class Record(object):

    def __init__(self, data, parent_form):
        self.data = data
        self.form = parent_form
        self.id = data['id']
        self.status = data['status']

    def _get_record_title(self):
        record_title_elements = []
        
        for i in self.form.title_field_keys:
            try:
                if isinstance(self.data['form_values'][i], (str, unicode)):
                    record_title_elements.append(self.data['form_values'][i])
                elif isinstance(self.data['form_values'][i], dict):
                    record_title_elements.append(self.data['form_values'][i]['choice_values'][0])
            except KeyError:
                record_title_elements.append('MISSING')
                
        if record_title_elements:
            record_title = ", ".join(record_title_elements)
        else:
            record_title = 'Unknown or missing title'

        return record_title

    def get_photos_api(self):
        return fulcrum.photos.search(url_params={'record_id': self.id})

    def find_value(self, key):
        value = self.data
        	
        def find(key, value):
            for k, v in value.iteritems():
                if k == key:
                    yield v
                elif isinstance(v, dict):
                    for result in find(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        if isinstance(d, dict):
                            for result in find(key, d):
                                yield result
                                
        return list(find(key, value))
                

    def get_photos_data(self):
        pass

    title = property(_get_record_title)

class Subrecord(Record):

    def __init__(self):
        pass

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
            if key in ('name','id'):
                forminfo[key]= form[key]
        output.append(forminfo)
        
    return output



my_form = Form(form)
#my_record = Record(records['records'][84], my_form)

        
       


        







        
        
        

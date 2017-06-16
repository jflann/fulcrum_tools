from fulcrum import Fulcrum
import fulcrum.exceptions
import os
import sys

import requests
import uuid
from pprint import pprint as pp

requests.packages.urllib3.disable_warnings()

#Ask user for API key, then create Fulcrum access object
fulcrumKey = raw_input('Enter the Fulcrum API key: ')
#fulcrumKey = ''
fulcrum = Fulcrum(key=fulcrumKey)


#form = fulcrum.forms.find('')
#records = fulcrum.records.search(url_params={'form_id': ''})











class Form(object):

    def __init__(self, form_id):
        self.data = fulcrum.forms.find(form_id)['form']
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

    def record_ids(self):
        '''
        Returns a generator object that yields record IDs
        '''
        records = fulcrum.records.search(url_params={'form_id': self.form_id})
        record_ids = []
        for i in records['records']:
            yield i['id']
        #return tuple(record_ids)

    #keys = property(_get_keys)
            



class Record(object):

    def __init__(self, record_id):
        self._data = fulcrum.records.find(record_id)
        self.data = _data['record']
        self.form = data['form_id']
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



#my_form = Form(form)
#my_record = Record(records['records'][84], my_form)

def create_record_links(form_id):
    #Get all inspection records
    records = fulcrum.records.search(url_params={'form_id': form_id})
    #Iterate over the inspection records
    for insp in records['records']:
        #Each inspection should be linked to a site record.
        #This grabs that site's record_id.
        site_record_id = insp['form_values']['50d0'][0]['record_id']
        #Get the site record from fulcrum.
        site_record = fulcrum.records.find(site_record_id)
        #Check for the key for the repeatables section which holds the record
        #links that we are checking for
        link_found = False
        if '34b9' in site_record['record']['form_values']:
            inspection_list = site_record['record']['form_values']['34b9']
            for item in inspection_list:
                linked_id = item['form_values']['1285'][0]['record_id']
                if linked_id == insp['id']:
                    print('Got Link.')
                    link_found = True
                    break #because we found the link, can leave the loop.
            if link_found == False:
                print('Has links but not this one')
                update_record = site_record
                values = insp['form_values']
                update_repeatable = {
                    u'form_values': {u'0a08': u'N/A',
                                     u'1285': [{u'record_id': insp['id']}],
                                     u'9469': u'compliance status',
                                     u'950b': u'next inspection',
                                     u'9532': u'inspector name',
                                     u'aae2': u'inspection date'},
                    u'id': str(uuid.uuid4()),
                    u'geometry': None}
                update_repeatable['form_values']['9469'] = values['ccf2']['choice_values'][0] if  'ccf2' in values else ''
                update_repeatable['form_values']['950b'] = values['6f55'] if '6f55' in values else ''
                update_repeatable['form_values']['0a08'] = values['13b3'] if '13b3' in values else ''
                update_repeatable['form_values']['9532'] = values['6be3']['choice_values'][0] if '6be3' in values else ''
                update_repeatable['form_values']['aae2'] = values['0137'] if '0137' in values else ''

                update_record['record']['form_values']['34b9'].append(update_repeatable)
                _result = fulcrum.records.update(site_record_id, update_record)
                pp(_result)

        if link_found == False:
            print('Need to make link.')
            update_record = site_record
            values = insp['form_values']
            update_repeatable = {
                u'form_values': {u'0a08': u'N/A',
                                 u'1285': [{u'record_id': insp['id']}],
                                 u'9469': u'compliance status',
                                 u'950b': u'next inspection',
                                 u'9532': u'inspector name',
                                 u'aae2': u'inspection date'},
                u'id': str(uuid.uuid4()),
                u'geometry': None}
            update_repeatable['form_values']['9469'] = values['ccf2']['choice_values'][0] if  'ccf2' in values else ''
            update_repeatable['form_values']['950b'] = values['6f55'] if '6f55' in values else ''
            update_repeatable['form_values']['0a08'] = values['13b3'] if '13b3' in values else ''
            update_repeatable['form_values']['9532'] = values['6be3']['choice_values'][0] if '6be3' in values else ''
            update_repeatable['form_values']['aae2'] = values['0137'] if '0137' in values else ''
            update_record['record']['form_values']['34b9'] = [update_repeatable]
            _result = fulcrum.records.update(site_record_id, update_record)
            pp(_result)
            





site_form = Form('c161173c-bfe3-409b-ad2b-8e8873db785a')
inspection_form = Form('5f09547d-ac49-4a32-ad3e-4c324675b7b5')
test_repeatable = {
  u'form_values': {u'0a08': u'N/A',
                   u'1285': [{u'record_id': ''}],
                   u'9469': u'COMPLIANCE ORDERED',
                   u'950b': u'2020-06-14',
                   u'9532': u'Paul Chollsen',
                   u'aae2': u'2017-06-14'},
  u'id': '',}

template = {u'changeset_id': u'dcdb9b6a-4eaf-4752-b5fd-8f8e3c1675c6',
 u'created_at': u'1497629594',
 u'created_by_id': u'd9203479-307e-4eea-8453-ec3733f7760d',
 u'created_duration': 6,
 u'created_location': {u'altitude': 259.949462890625,
                       u'horizontal_accuracy': 65,
                       u'latitude': 44.9793827699787,
                       u'longitude': -93.2664198637534},
 u'edited_duration': 6,
 u'form_values': {u'0a08': u'N/A',
                  u'1285': [{u'record_id': u'0fc17b14-72ca-4520-8ef8-a7d8d5a14409'}],
                  u'9469': u'COMPLIANCE ORDERED',
                  u'950b': u'2020-06-14',
                  u'9532': u'Paul Chellsen',
                  u'aae2': u'2017-06-14'},
 u'geometry': {u'coordinates': [-93.2664198637534, 44.9793827699787],
               u'type': u'Point'},
 u'id': u'3e3c48db-732e-4d1b-9e35-f8009af46a37',
 u'updated_at': u'1497629600',
 u'updated_by_id': u'd9203479-307e-4eea-8453-ec3733f7760d',
 u'updated_duration': 6,
 u'updated_location': {u'altitude': 260.032867431641,
                       u'horizontal_accuracy': 65,
                       u'latitude': 44.9793508693867,
                       u'longitude': -93.2664459542137},
 u'version': 1}

#  u'34b9': u'completed_inspections'
#  u'1285': u'inspection'
        
       


        







        
        
        

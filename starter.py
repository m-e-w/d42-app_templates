import json
import yaml
from device42 import Device42Api

with open('templates.yaml', 'r') as tmp:
    templates = yaml.load(tmp.read())

with open('config.yaml', 'r') as cfg:
    config = yaml.load(cfg.read())

options = config['options']
device42 = config['device42']
device42_api = Device42Api(device42, options)
dry_run = options['dry_run']
debug = options['debug']

def remove_dupe_dicts(l):
    list_of_strings = [
        json.dumps(d, sort_keys=True)
        for d in l
    ]
    list_of_strings = set(list_of_strings)
    return [
        json.loads(s)
        for s in list_of_strings
    ]

def main():
    data = {}
    
    for template in templates: 
        data[template] = {
            "service_details": []
        }
        service_names = []

        for service in templates[template]['Services']:
            service_paths = []
            service_names.append(service)

            if templates[template]['Services'][service]['Paths']:
                for path in templates[template]['Services'][service]['Paths']:
                    service_paths.append(path)

            paths = "|".join(service_paths)
            query = "WITH service_list AS (SELECT d.device_pk d_pk, d.name d_name, si.serviceinstance_pk si_pk, s.displayname s_displayname, unnest(si.cmd_paths) cmd FROM view_service_v2 s JOIN view_serviceinstance_v2 si ON s.service_pk = si.service_fk AND s.displayname = '" + service + "' JOIN view_device_V2 d ON si.device_fk = d.device_pk) SELECT d_pk, d_name, si_pk, s_displayname FROM service_list " 
            
            if(paths):
                query += "WHERE cmd SIMILAR TO '%(" + paths + ")%'"
            
            response = device42_api._query(query)
            for item in response:
                item['topology_status'] = templates[template]['Services'][service]['topology_status']
                item['pinned'] = templates[template]['Services'][service]['pinned']
                data[template]['service_details'].append(item)

    return data
if __name__ == '__main__':
    elements = main()
    if(debug):
        print('\nDebug: Elements: %s ' % json.dumps(elements, indent=1))

    appcomps = []
    service_instances = []

    for element in elements:
        for svc in elements[element]['service_details']:
            appcomp = {
                "name" : element + ' - ' + svc['d_name'],
                "device": svc['d_name']
            }
               
            service_instance = {
                "service_detail_id": svc['si_pk'],
                "pinned": "yes",
                "topology_status": svc['topology_status'],
                "appcomps": appcomp['name']
            }
         
            appcomps.append(appcomp)
            service_instances.append(service_instance)

    appcomps = remove_dupe_dicts(appcomps)
    if(dry_run):
        print('\nDry run: Application Components')
        print(json.dumps(appcomps, indent=1))
        print('\nDry run: Service Instances')
        print(json.dumps(service_instances, indent=1))
    else:
        print('\n**********  Posting Application Components  **********')
        for ac in appcomps:
            print('\nPOST: %s' % ac)
            print('Response: %s' % device42_api._post_appcomp(ac))
        
        print('\n**********  Posting Service Instances  **********')
        for  si in service_instances:
            print('\nPOST: %s' % si)
            print('Response: %s' % device42_api._post_serviceinstance(si))
    print('\n')

 
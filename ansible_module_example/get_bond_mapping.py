from ansible.module_utils.basic import AnsibleModule
import json

# https://docs.ansible.com/ansible/2.4/dev_guide/developing_modules_general.html

def get_bond_mapping(path):
    net_config = open(path, "r")
    net_config = json.loads(net_config.read())
    results = []
    for group in net_config['network_config']:
        if 'members' in group.keys():
            members = group['members']
            interfaces = []
            for interface in members[0]['members']:
                interfaces.append(interface['name'])
            member_mapping = {}
            member_mapping[group['name']] = interfaces
            if len(members) > 1:
                for member in members[1:]:
                    interface_name = member['type'] + str(member['vlan_id'])
                    member_mapping[interface_name] = interfaces
            results.append(member_mapping)
    return results

def main():
    module = AnsibleModule(
        argument_spec = dict(
            network_config_path = dict(required=True, type='str'),
        )
    )

    path = module.params['network_config_path']
    results = get_bond_mapping(path)
    module.exit_json(changed=True, results=results)

if __name__ == '__main__':
    main()

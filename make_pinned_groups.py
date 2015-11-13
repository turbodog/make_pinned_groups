#!/usr/bin/python
"""make_pinned_groups.py: creates scripts that create node groups with pinned nodes"""

#
# Configuration
#

classifier_hostname = "localhost"
certname = "master"
num_groups = 5
pinned_nodes_per_group = 1000
nodename_prefix = "agent"
digit_padding = 6

#
# Example source data for the output
#

""" 
 curl https://<DNS NAME OF CONSOLE>:4433/classifier-api/v1/groups --cert /etc/puppetlabs/puppet/ssl/certs/<WHITELISTED CERTNAME>.pem --key /etc/puppetlabs/puppet/ssl/private_keys/<WHITELISTED CERTNAME>.pem --cacert /etc/puppetlabs/puppet/ssl/certs/ca.pem -H "Content-Type: application/json"
"""

"""
 {
   "name": "Webservers",
   "id": "58463036-0efa-4365-b367-b5401c0711d3",
   "environment": "staging",
   "parent": "00000000-0000-4000-8000-000000000000",
    "rule": [
        "or",
        [
            "=",
            "name",
            "agent000001"
        ],
        [
            "=",
            "name",
            "agent000000"
        ]
    ],
   "variables": {
     "ntp_servers": ["0.us.pool.ntp.org", "1.us.pool.ntp.org", "2.us.pool.ntp.org"]
   }
 }
"""

#
# Do it
#

base_curl_command = 'curl -X POST https://%s:4433/classifier-api/v1/groups --cert /etc/puppetlabs/puppet/ssl/certs/%s.pem --key /etc/puppetlabs/puppet/ssl/private_keys/%s.pem --cacert /etc/puppetlabs/puppet/ssl/certs/ca.pem -H "Content-Type: application/json" -d \'%%s\'' % (classifier_hostname, certname, certname)

nodename_template = "%s%%0%sd" % (nodename_prefix, digit_padding)
node_starting_index = 0
for group in range(num_groups):
	group_name = "%03d" % group
	print "Group: %s" % group_name
	f = open(group_name+'.sh', 'w')
	json_body = """
{
  "name": "Group %02d",
  "environment": "production",
  "parent": "00000000-0000-4000-8000-000000000000",
  "classes": {},
    "rule": [
        "or",\n""" % (group)
	for node_number in range(pinned_nodes_per_group-1):
		node = nodename_template % (node_starting_index + node_number)
		json_body += '	["=", "name", "%s"],\n' % (node)

	node = nodename_template % (node_starting_index + node_number + 1)
	json_body +=  '	["=", "name", "%s"]\n' % (node)
	node_starting_index += pinned_nodes_per_group
	json_body += "    ]\n}"
	curl_command = base_curl_command % (json_body)
	f.write(curl_command)
	f.close
	
#	print curl_command

from pprint import pprint as pp
import requests as r
import json
import math

class MenuValidator:
	def __init__(self, challenge_id):
		self.url = 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json'
		self.challenge_id=challenge_id
		self.root_nodes = {}
		self.menus = {}

	def validate(self):
		'''
		The main function to be called. Calls helper functions that pull data from
		the API, checks whether each path down each root node is a valid menu, then
		outputs the valid and invalid menus to a file called challenge1_output.json and challenge2_output.json
		'''
		self.pullData()
		self.validateEachPath()
		self.createJSONOutput()

	def callAPI(self, page):
		'''
		calls a page backend summer challenge 2018's API and returns the result
		return type: requests.models.Response
		'''
		params = dict(
		    id=self.challenge_id,
			page=page
		)
		return r.get(url=self.url, params=params)

	def pullData(self):
		'''
		Goes through the API's pages filling self.root_nodes with the root nodes and self.menus with all nodes
		return type: None
		'''
		
		first_page_response = self.callAPI(1)
		json_data = json.loads(first_page_response.text)

		total = json_data['pagination']['total']
		per_page = json_data['pagination']['per_page']
		total_pages = math.ceil(total / per_page)

		for menu_item in json_data['menus']:
			if 'parent_id' not in menu_item:
				self.root_nodes[menu_item['id']] = {'valid': True}
			self.menus[menu_item['id']] = menu_item['child_ids']

		if total_pages > 1:
			for page in range(2, total_pages+1):
				api_response = self.callAPI(page)
				json_data = json.loads(api_response.text)
				for menu_item in json_data['menus']:
					if 'parent_id' not in menu_item:
						self.root_nodes[menu_item['id']] = {'valid': True}
					self.menus[menu_item['id']] =  menu_item['child_ids']

	def traverseDown(self, node, root_node, path_list):
		'''
		Checks for cyclical references by recursing down the path from the given
		root node and fills up path_list with all the nodes on that path. If a 
		duplicate is present, it sets the 'valid' key for the given root node to 
		false in root_nodes. 
		'''
		path_list.append(node)
		children = self.menus[node]

		if not children:
			return
		for child in children:
			if child in path_list:
				self.root_nodes[root_node]['valid'] = False
				path_list.append(child)
			else:
				self.traverseDown(child, root_node, path_list)

	def validateEachPath(self):
		'''
		Iterates over the root nodes and applies traverseDown() to each root node
		and maps the 'children' key in root_nodes to a list containing all the
		children of that root node.
		'''
		for root in self.root_nodes:
			path = []
			self.traverseDown(root, root, path)
			self.root_nodes[root]['children'] = path

	def createJSONOutput(self):
		'''
		Reads root_nodes dictionary to check whether each path is valid.
		Creates a json dictionary that contains each root node and whether
		it's a valid menu or not and it's children that are placed under the
		keys 'valid_menus' and 'invalid_menus' accordingly.
		'''
		output={'valid_menus': [], 'invalid_menus': []}
		for root in self.root_nodes:
			if self.root_nodes[root]['valid']:
				output['valid_menus'].append({'root_id': root, 'children': self.root_nodes[root]['children']})
			else:
				output['invalid_menus'].append({'root_id': root, 'children': self.root_nodes[root]['children']})

		output_file_name = 'challenge{}_output.json'.format(self.challenge_id)
		with open(output_file_name, 'w') as output_file:
			json.dump(output, output_file)

	

if __name__ == '__main__':
	basic_challenge_id='1'
	validator = MenuValidator(basic_challenge_id)
	validator.validate()
	pp(validator.root_nodes)
	pp(validator.menus)

	bonus_challenge_id='2'
	validator2 = MenuValidator(bonus_challenge_id)
	validator2.validate()
	pp(validator2.root_nodes)
	pp(validator2.menus)

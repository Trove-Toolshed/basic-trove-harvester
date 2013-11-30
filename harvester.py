import re
import json
from urllib2 import urlopen, Request, HTTPError
from utilities import retry


class ServerError(Exception):
    pass


class TroveHarvester:

	def __init__(self, query, key, start=0, number=20):
		self.query = self._clean_query(query)
		self.key = key
		self.harvested = int(start)
		self.number = int(number)
		self.log_query()

	def _clean_query(self, query):
		"""Remove s and n values just in case."""
		query = re.sub(r'&s=\d+', '', query)
		query = re.sub(r'&n=\d+', '', query)
		return query

	def log_query(self):
		"""Do something with details of query -- ie log date"""
		pass

	@retry(ServerError, tries=10, delay=1)
	def _get_url(self, url):
		''' Try to retrieve the supplied url.'''
		req = Request(url)
		try:
			response = urlopen(req)
		except HTTPError as e:
			if e.code == 503 or e.code == 504:
				raise ServerError("The server didn't respond")
			else:
				raise
		else:
			return response

	def harvest(self):
		number = self.number
		query_url = '{}&n={}&key={}'.format(
				self.query, 
				self.number, 
				self.key
				)
		while number == self.number:
			current_url = '{}&s={}'.format(
				query_url, 
				self.harvested
				)
			print current_url
			response = self._get_url(current_url)
			try:
				results = json.load(response)
			except (AttributeError, ValueError):
				pass
				# Log errors?
			else:
				self.process_results(results['response']['zone'])
				number = int(results['response']['zone'][0]['records']['n'])


	def process_results(self, results):
		"""
		Do something with each set of results.
		Needs to update self.harvested
		"""
		self.harvested += self.number

import json
import requests
import math

AUTH = "YOUR YELP AUTH KEY HERE"

def printResults(rawJSON):
	businesses = rawJSON['businesses']
	for b in businesses:
		print (b['name'])
		print (b['url'])
		loc = b['location']['display_address']
		for line in loc:
		    print (line)
		print (b['display_phone'])
		print ('')

def csvResults(filename, rawJSON):
	try:
		f = open(filename, "w")
		f.write("name, url, addr, phone\n")
	except Exception as e:
		print("filename %s in use by another program. Please close it." % filename)
		exit()

	businesses = rawJSON['businesses']
	for b in businesses:
		f.write(b['name'] + ",")
		f.write(b['url'] + ",")
		loc = b['location']['display_address']
		for line in loc:
			
			line = line.replace(',', '')
		#	print (line)
			f.write(line + " ")
		f.write(',')
		f.write(b['display_phone'] + ",")
		f.write('\n')

	print("Results written to file %s" % filename)
	f.close()
	return filename


def requestResults(term, location, radius, num):
	# Yelp API has hard limit of 50; queue requests
	if (num > 50):
		limit = 50
		loops = math.ceil(num / 50)
	else:
		limit = num
		loops = 1

	# add offset request params to a q
	q = []
	for i in range (loops):
		offset = i * 50
		offstr = '&offset=%d' % (offset)
		q.append(offstr)

	rawJSON = {}
	payload = {'Authorization': 'Bearer %s' % AUTH}
	i = 0
	for offstr in q:
		print ("OK!!!")
		rs = 'https://api.yelp.com/v3/businesses/search?term=\"%s\"&location=\"%s\"&radius=%d&limit=%d%s' % (term, location, radius, limit, offstr)
		r = requests.get(rs, headers=payload)
		print (rs)
		print(r.status_code)
		print("\n")
		newData = r.json()
		# set initial formatting only once
		if (i == 0):
			rawJSON = newData
			i = 1
		# then just add business data
		else:
			# merge dictionaries
			oldbiz = rawJSON['businesses']
			newbiz = newData['businesses']
			fizzbuzz = oldbiz + newbiz
			rawJSON.update({'businesses':fizzbuzz})
	return rawJSON

def test():
	location = "Phoenix, AZ"
	term = "physical therapy"

	rawJSON = requestResults(term, location, 40000, 1000) # last two params are max values for Yelp
	print (rawJSON)
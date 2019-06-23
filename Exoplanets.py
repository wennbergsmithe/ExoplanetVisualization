import requests 

s_boltz = 1.3*(10 ** -23)


#pull data from API
def apiRequest():
	URL = "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=exoplanets&format=json"
	data = []
	try:
		r = requests.get(url = URL) 
		data = r.json()	
	except Exception as e:
		print(e) #error handling
	return data

#calculates stellar luminosity assuming mass and radius in solar units
def stellarLum(mass,radius):
	return (mass**2)*(radius**4)

#determines if the given of the planets lie withing the habitable zone of the given star
#assumes earthlike albedo of .3
def habZone(lum, orbRad):

	aMax = (((1 - .3) * lum) / ((16 * 3.1415) * s_boltz * (275 ** 4)))**.5
	aMin = (((1 - .3) * lum) / ((16 * 3.1415) * s_boltz * (375 ** 4)))**.5

	#if lies within range
	if(orbRad <= aMax and orbRad >= aMin):
		return True
	else:
		return False

#estimates composition of planet based on its density
def estimateComp(dens):
	if(dens < 1):
		#automatically returns HJ if it is less than 1 because most are (for efficiency)
		return "Hot Jupiter"
	elif(dens == 1):
		return "water"
	#dictionary of common planetary materials and their densities
	commonDens = { "iron":7.86, "lead":11.36, "gold":19.32, "Earth":5.51, "Neptune":1.64, "Mars":3.93, "Hot Jupiter": 1.33}
	toReturn = ""
	#difference to determine which value is closest.
	#unreasonable initial value just to initaiate variable
	smallestDiff = 999
	for material in commonDens:
		diff = commonDens[material] - dens
		absDiff = abs(diff)
		if(absDiff <= smallestDiff):
			smallestDiff = absDiff
			toReturn = material

	return toReturn


#writes the data into a csv file to be used in cytoscape
def format(planets):
	file = open("planets.csv","w") 
	
	keys = planets[0].keys()
	firstline = ""
	for key in keys:
		firstline += key + ","
	firstline = firstline[:-1]
	firstline += "\n"
	file.write(firstline) 

	for planet in planets:
		vals = planet.values()
		nextLine = ""
		for val in vals:	
			nextLine += str(val)
			nextLine += ","
		nextLine = nextLine[:-1]
		
		nextLine += "\n"
		file.write(nextLine) 

	
	file.close()


def main():
	data = apiRequest()#gather json data
	nodata = 0#just to know how many stars have no distance data
	narrowedData = []#list of planets with narrowed data and additional data computed by moi

	#for each planet within 20 parsecs
	for planet in data:
			try:
				#if there is data for density
				if(int(planet.get("pl_dens")) != None):
					planetDict = {"name":planet.get("pl_name"), "method":planet.get("pl_discmethod"), "orbitalPeriod": planet.get("pl_orbper"),
					"mass":planet.get("pl_bmassj"), "radius":planet.get("pl_radj"),"semimajor" : planet.get("pl_orbsmax"), "density":planet.get("pl_dens"), 
					"composition":estimateComp(planet.get("pl_dens")), "dist": planet.get("st_dist"),
					"luminosity": stellarLum(planet.get("st_mass"),planet.get("st_rad")),
					"Habitable?" : habZone(stellarLum(planet.get("st_mass"),planet.get("st_rad")),planet.get("pl_orbsmax"))}
					narrowedData.append(planetDict)

			except:
				nodata += 1	
	format(narrowedData)
main()

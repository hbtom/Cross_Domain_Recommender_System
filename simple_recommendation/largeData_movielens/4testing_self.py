from math import *

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs,person1,person2):
	#get the shared items
	si={}		#if s[item]==1, that means item is common in both person1 and person2
	
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item]=1


	#if no item is common
	if len(si)==0:
		return 0
	
	#sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])
	sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in si])

	return 1/(1+sum_of_squares)


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs,p1,p2):
	# Get the list of mutually rated items
	si={}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item]=1

	# Find the number of elements
	n=len(si)
	# if they are no ratings in common, return 0
	if n==0:
		return 0

	# Add up all the preferences
	sum1=sum([prefs[p1][it] for it in si])
	sum2=sum([prefs[p2][it] for it in si])

	# Sum up the squares
	sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
	sum2Sq=sum([pow(prefs[p2][it],2) for it in si])

	# Sum up the products
	pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])

	# Calculate Pearson score
	num=pSum-(sum1*sum2/n)
	den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
	if den==0:
		return 0
	r=num/den
	return r


# for person1 in critics:
# 	for person2 in critics:
# 		#if person1!=person2:
# 			print person1+"  "+person2+":",
# 			print sim_distance(critics,person1,person2),
# 			print sim_pearson(critics,person1,person2)


def top_matches(critics, person, n=5, sim=sim_pearson):
	li=[(sim(critics,person,other),other) for other in critics if other!=person]

	li.sort()
	li.reverse()

	return li[0:n]				#return only first n items

#print top_matches(critics,'Toby',n=3);

def transformPrefs(prefs):
	result={}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item,{})

			# Flip item and person
			result[item][person]=prefs[person][item]
	
	return result



# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):

	totals={}
	simSums={}

	for other in prefs:
		# don't compare me to myself
		if other==person:
			continue
		sim=similarity(prefs,person,other)

		# ignore scores of zero or lower
		if sim<=0: 
			continue

		for item in prefs[other]:
			# only score movies I haven't seen yet
			if item not in prefs[person]:								# or prefs[person][item]==0:
				# Similarity * Score
				totals.setdefault(item,0)
				totals[item]+=prefs[other][item]*sim
				# Sum of similarities
				simSums.setdefault(item,0)
				simSums[item]+=sim
				# Create the normalized list

	rankings=[(total/simSums[item],item) for item,total in totals.items()]
	# Return the sorted list
	rankings.sort()
	rankings.reverse()

	return rankings


# print getRecommendations(critics, 'Toby')
# print getRecommendations(critics, 'Toby', sim_distance)


def calculateSimilarItems(prefs,n=10):
	# Create a dictionary of items showing which other items they are most similar to
	result={}

	# Invert the preference matrix to be item-centric
	itemPrefs=transformPrefs(prefs)

	c=0
	for item in itemPrefs:
		# Status updates for large datasets
		c+=1
		if c%100==0:
			print ("%d / %d" % (c,len(itemPrefs)))

		# find the most similar items to this one
		scores=top_matches(itemPrefs,item,n=n,sim=sim_distance)
		result[item]=scores

	return result

#print (calculateSimilarItems(critics))

#get reommendation of item(movies) for a person 
def getRecommendedItems(prefs,itemMatch,user):
	userRatings=prefs[user]
	scores={}
	totalSim={}
	
	# Loop over items rated by this user
	for (item,rating) in userRatings.items():
		# Loop over items similar to this one
		for (similarity,item2) in itemMatch[item]:
			# Ignore if this user has already rated this item
			if item2 in userRatings:
				continue
			
			# Weighted sum of rating times similarity
			scores.setdefault(item2,0)
			scores[item2]+=similarity*rating
			
			# Sum of all the similarities
			totalSim.setdefault(item2,0)
			totalSim[item2]+=similarity
	
	# Divide each total score by total weighting to get an average
	rankings=[(score/totalSim[item],item) for item,score in scores.items()]
	
	# Return the rankings from highest to lowest
	rankings.sort()
	rankings.reverse()
	
	return rankings


def loadMovieLens(path='/home/jaydeep/Desktop/Mini_project/movielens_dataset/movielens_100K', file='/u1.base'):
	# Get movie titles
	movies={}
	for line in open(path+"/u.item",encoding='latin-1'):
		(id,title)=line.split('|')[0:2]
		movies[id]=title

	# Load data
	prefs={}
	for line in open(path+file):
		(user,movieid,rating,ts)=line.split('\t')
		prefs.setdefault(user,{})
		prefs[user][movies[movieid]]=float(rating)
	return prefs


if __name__=='__main__':
	trainPrefs = loadMovieLens(file="/u1.base")
	testPrefs = loadMovieLens(file='/u1.test')
	
	final_err=[]
	for user in testPrefs:
		pred = getRecommendations(trainPrefs,user)
		count=-1
		preds={}
		for rating,item in pred:
			preds[item]=rating
			# print movies[item],rating,item
		error=[]
		
		for movie in testPrefs[user]:
			if not movie in preds:
				continue 
			actualRating = testPrefs[user][movie]
			predcitedRating = preds[movie]
			diff = fabs(fabs(predcitedRating) - fabs(actualRating))
			#print (predcitedRating,actualRating,diff)
			error.append(diff)
			final_err.append(diff)
			
			
		print (sum(error)/len(error))

	print ("MAE=%lf" % (sum(final_err)/len(final_err)))
	
#MAE=0.810374


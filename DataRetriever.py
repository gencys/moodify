import ast
import os
import requests

import spotipy

#Setting up needed global variables

CWD = os.getcwd()
CLIENT_ID = '6a279884a39e43d5b5a00d40f2519094'
CLIENT_SECRET = 'c388d4f517b44c94a9176ba17bf97058'

#Function to get the client's access token

def get_client_token(client_id = CLIENT_ID, client_secret = CLIENT_SECRET):
	try:
		#Authenticates into the Spotify API and gets the token
		auth = spotipy.oauth2.SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
		token = auth.get_access_token(as_dict = False)
		return token
	except:
		raise NameError('Could not authenticate the user')

#Function that reads the StreamingHistory files downloaded from Spotify and returns them as a list of dictionaries

def get_history(path = CWD):

	data_directory = path + '/MyData/'

	files = [data_directory + x for x in os.listdir(data_directory) if x.split('.')[0][:-1] == 'StreamingHistory']

	all_streamings = []

	for file in files:
		with open(file, 'r', encoding='UTF-8') as f:
			new_streamings = ast.literal_eval(f.read())
			#This does some preprocessing by selecting only tracks that have been played for more than 40s
			all_streamings += [streaming for streaming in new_streamings if streaming["msPlayed"] > 40000 and streaming["trackName"] != "Episode"]

	return all_streamings

#Function that gets from the API the unique IDs identifying the tracks previously salvaged, it return a list of strings

def get_track_ids(streamings, token):

	#Defining the headers for the request
	headers = {
	'Accept': 'application/json',
	'Content-Type': 'application/json',
	'Authorization': f'Bearer ' + token
	}

	ids = []


	#Iterating over all of the streaming history
	for streaming in streamings:
		#Define the parameters for the query
		params = {
		'q': streaming['trackName'],
		'artist': streaming['artistName'],
		'type': 'track'
		}

		try:
			response = requests.get('https://api.spotify.com/v1/search', headers = headers, params = params, timeout = 5)
			data_retrieved = response.json()

			#Check if the request returned a non-empty answer
			if not data_retrieved:

				first_result = data_retrieved['tracks']['items'][0]

				#Assume the first result is the right one
				track_id = first_result['id']

				#Check if it really is the right one
				if first_result['name'].strip() != streaming['artistName'].strip():

					results = data_retrieved['tracks']['items']

					#If not, search for it
					for result in results:
						if result['name'].strip() == streaming['artistName'].strip():
							track_id = result['id']
			ids += [track_id]

		except:
			raise NameError('Error with the search query')
	
	return ids

#Function that gets the audio features from the API by using the IDs

def get_features(ids, token):
	#Logs in to the API
	sp = spotipy.Spotify(auth=token)
	#List of audio feature that won;t be needed
	unneeded_features = ['type', 'id', 'uri', 'track_href', 'analysis_url', 'time_signature']
	features = []

	#Test if the function was given a list or a single ID because if should work for both
	if type(ids) is list:
		
		for track_id in ids:
			try:
				#Retrieves the feature for one track
				raw_features = sp.audio_features([track_id])
				raw_features = raw_features[0]
				#Remove the unneeded audio features
				for string in unneeded_features:
					raw_features.pop(string)

				features_increment = []

				#Create a 1D array to store the features of one track
				for value in raw_features.values():
					features_increment += [value]

				#Add the 1D array to the 2D array storing the features of all the tracks
				features += [features_increment]
			except:
				print(f'Could not retrieve features for {track_id}')
				return None
		return features
	else:
		#Same idea as above but for a single ID given
		try:
			raw_features = sp.audio_features([ids])
			raw_features = raw_features[0]
			
			for string in unneeded_features:
				raw_features.pop(string)

			for value in raw_features.values():
				features += [value]

			return features
		except:
			print(f'Something went wrong for {ids}')
			return None
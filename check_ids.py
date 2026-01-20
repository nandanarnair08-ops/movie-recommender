import pickle

movies = pickle.load(open("movies_list.pkl", "rb"))

print("TYPE:", type(movies))
print("\nCOLUMNS:", movies.columns)
print("\nFIRST 5 ROWS:")
print(movies.head())

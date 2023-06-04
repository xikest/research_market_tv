import pickle
with open('dict_allSeries.pickle', 'rb') as file:
    dict_allSeries = pickle.load(file)


dict_b = {}
i = 0
for k, v in dict_allSeries.items():
    dict_b.update({k:v})
    i += 1

    if i >5:
        break

print(dict_b)

with open('dict_b.pickle', 'wb') as f:
    pickle.dump(dict_b, f)

# dict_a= {k: v[0] for k, v in dict_allSeries.items()}

#
# dict_a= {k: v[0] for k, v in dict_allSeries.items()}
# print(dict_a)
# with open('dict_allSeries.pickle', 'wb') as f:
#     pickle.dump(dict_a, f)
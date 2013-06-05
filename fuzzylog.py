def find_closest(word):
    if word in mnemonics:
        return mnemonics[word], mnemonics[word][0]
    else:
        words = []
        distances = []
        smallest_distance = 100
        for w in mnemonics:
            distance = edit_distance(word,w)
            if distance < smallest_distance:
                words.insert(0,mnemonics[w])
                distances.insert(0,distance)
                smallest_distance = distance
            else:
                words.append(mnemonics[w])
                distances.append(distance)
        return words[0], distances[0]

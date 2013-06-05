def levenshtein(s,t):
    def matrix(a,b):
        out = []
        for i in range(0,a):
            out.append([])
            for j in range(0,b):
                out[i].append(0)
        return out
    
    # Make a matrix for all string comparisons
    a, b = len(s)+1, len(t)+1
    m = matrix(a,b)
    
    # Populate the null string comparisons
    for i in range(0,a):
        m[i][0] = i
    for j in range(1,b):
        m[0][j] = j
        
    for j in range(1,b):
        for i in range(1,a):
            if s[i-1] == t[j-1]:
                m[i][j] = m[i-1][j-1]
            else:
                dln = m[i-1][j] + 1
                ins = m[i][j-1] + 1
                sub = m[i-1][j-1] + 1
                m[i][j] = min(dln, ins, sub)
        
    # We have the whole matrix but only need the final distance
    return m[a-1][b-1]

def levenshtein2(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]
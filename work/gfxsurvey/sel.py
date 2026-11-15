def sel(j, t=2950):
    seq = ['{%d,"Up"}' % t]; t += 80
    for k in range(j-2): seq.append('{%d,"Right"}' % t); t += 70
    return seq, t+100
def mash(t0, t1, btn="Button A", per=60):
    return ['{%d,"%s"}' % (t, btn) for t in range(t0, t1, per)]

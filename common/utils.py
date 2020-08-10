def chunks(l, size):
    for i in range(0, len(l), size):
        yield l[i:i+size]

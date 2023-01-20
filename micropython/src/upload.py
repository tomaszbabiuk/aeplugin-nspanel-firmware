
def readMinimum():
    with open("minimum.hmi", "rb") as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            print(chunk)
            # Do something with the chunk of data

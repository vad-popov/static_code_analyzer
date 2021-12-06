def tracklist(**kwargs):
    for key, value in kwargs.items():
        print(key)
        for key_2, value_2 in value.items():
            print(f'ALBUM: {key_2} TRACK: {value_2}')

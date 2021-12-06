def translate(**kwargs):
    for word1, word2 in kwargs.items():
        print(word1, ":", word2)

words = {"mother": "madre", "father": "padre", 
         "grandmother": "abuela", "grandfather": "abuelo"}

translate(**words)
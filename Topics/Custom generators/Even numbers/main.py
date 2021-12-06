n = int(input())

def even():
    yield from (i * 2 for i in range(n))

# Don't forget to print out the first n numbers one by one here
print(*even(), sep='\n')

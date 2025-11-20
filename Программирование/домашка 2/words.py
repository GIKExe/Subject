
def main():
	text = input()
	words = text.split()
	unique_words = []

	for word in words:
		if word and word not in unique_words:
			unique_words.append(word)
			print(word, end=' ')

if __name__ == '__main__':
	main()
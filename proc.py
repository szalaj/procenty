import yaml
if __name__== "__main__":
    print('hello proc')


    stream = open("./models/mod1.yml", 'r')
    dictionary = yaml.safe_load(stream)
    for key, value in dictionary.items():
        print (key + " : " + str(value))
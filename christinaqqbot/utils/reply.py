import random

def get_random_reply(random_list):
    random_sample =random.sample(range(0,len(random_list)),len(random_list))
    random_int=random_sample[random.randint(0,len(random_sample)-1)]
    return random_list[random_int]
import csv
import pickle
from operator import itemgetter


# jaccardova podobnost dvoch mnoznin
def jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)


def symmetric_difference(x, y):
    return list(set(x).symmetric_difference(set(y)))


# zo suboru vytvori mapovaciu tabulku user <-> vektor clankov a odstrani userov s 5 a menej clankami
def create_user_articles(train, min_articles):
    with open(train, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        user_articles = {}
        for row in reader:
            user_articles.setdefault(row['cookie'], []).append(row['sme_id'])

    cut_user_articles = {}
    for userA, articlesA in user_articles.items():
        if len(articlesA) > min_articles:
            cut_user_articles.setdefault(userA, articlesA)

    print("OK - user1: [article1, article2, article3, ...] %d" % len(cut_user_articles))
    return cut_user_articles


# pre kazdeho usera vytvori list podobnych s ich podobnostou
def create_user_similarity(user_articles):
    user_similarity = {}
    count = 0
    for userA, articlesA in user_articles.items():
        count += 1
        print(count)
        for userB, articlesB in user_articles.items():
            if userA != userB:
                similarity_ab = jaccard_similarity(articlesA, articlesB)
                user_similarity.setdefault(userA, list()).append([userB, similarity_ab])
    print("OK - user1: list([user2, similarity]) %d" % len(user_similarity))
    return user_similarity


# pre kazdeho usera usporiada list podobnych a vyberie iba prvych 10 najlepsich
def limit_top_similarity(user_similarity_dict, top_similar_users):
    top_dict = {}  # user1: list([user2, similarity]) iba prvych TOP N
    for user_a, users_b in user_similarity_dict.items():
        users_b = sorted(users_b, key=itemgetter(1), reverse=True)[:top_similar_users]
        top_dict.setdefault(user_a, users_b)
    print("OK - user1: TOPlist([user2, similarity]) %d" % len(top_dict))
    return top_dict


def recommend_articles(top_sim, user_articles, recommend_file):
    recommend = {}
    for userA, usersB in top_sim.items():
        user_a_articles = user_articles[userA]
        users_b_articles = []
        for userB, sim in usersB:
            users_b_articles += user_articles[userB]
        users_b_articles = list((set(users_b_articles)))
        diff = symmetric_difference(user_a_articles, users_b_articles)
        recommend.setdefault(userA, diff)
    with open(recommend_file, 'wb') as handle:
        pickle.dump(recommend, handle)
    print("OK - user1: [recommend_article1, recommend_article2, recommend_article3, ...] %d" % len(recommend))


def evaluation(recommend_file, test_file):
    with open(test_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        user_articles_dict = {}  # user1: [article1, article2, article3, ...]
        for row in reader:
            user_articles_dict.setdefault(row['cookie'], []).append(row['sme_id'])
    print(user_articles_dict)

    with open(recommend_file, 'rb') as handle:
        recommender_dict = pickle.load(handle)
    print(recommender_dict)


def print_to_file(recommend_pickle, recommend_file):
    with open(recommend_pickle, 'rb') as handle:
        recommend = pickle.load(handle)
    writer = csv.writer(open(recommend_file, 'w', newline='\n'))
    for userA, recommend_b in recommend.items():
        writer.writerow([userA, recommend_b])
    print("OK - Printed do file")


# MAIN
train_f = 'train_milion.csv'
test_f = 'test_pattern.csv'
recommend_p = 'recommend.pickle'
recommend_f = 'recommend.csv'
topSimilarUsers = 5
minArticles = 5

userArticles = create_user_articles(train_f, minArticles)
userSimilarity = create_user_similarity(userArticles)
topSimilarity = limit_top_similarity(userSimilarity, topSimilarUsers)
recommend_articles(topSimilarity, userArticles, recommend_p)
print_to_file(recommend_p, recommend_f)
evaluation(recommend_p, test_f)

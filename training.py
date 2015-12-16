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


# zo suboru vytvori mapovaciu tabulku user <-> vektor clankov
def create_user_articles(train_file):
    with open(train_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        user_articles_dict = {}  # user1: [article1, article2, article3, ...]
        for row in reader:
            user_articles_dict.setdefault(row['cookie'], []).append(row['sme_id'])
        return user_articles_dict


# pre kazdeho usera vytvori list podobnych s ich podobnostou
def create_user_similarity(user_articles_dict):
    user_similarity_dict = {}  # user1: list([user2, similarity])
    for userA, articlesA in user_articles_dict.items():
        for userB, articlesB in user_articles_dict.items():
            if userA != userB:
                similarity_ab = jaccard_similarity(articlesA, articlesB)
                user_similarity_dict.setdefault(userA, list()).append([userB, similarity_ab])
    return user_similarity_dict


# pre kazdeho usera usporiada list podobnych a vyberie iba prvych 10 najlepsich
def limit_top_similarity(user_similarity_dict, top_similar_users):
    top_dict = {}  # user1: list([user2, similarity]) iba prvych TOP N
    for user_a, users_b in user_similarity_dict.items():
        users_b = sorted(users_b, key=itemgetter(1), reverse=True)[:top_similar_users]
        top_dict.setdefault(user_a, users_b)
    return top_dict


def recommend_articles(top_dict, user_articles_dict, recommended_file):
    writer = csv.writer(open(recommended_file, 'w'))
    for userA, usersB in top_dict.items():
        user_a_articles = user_articles_dict[userA]
        users_b_articles = []
        for userB, sim in usersB:
            users_b_articles += user_articles_dict[userB]
        users_b_articles = list((set(users_b_articles)))
        recommended = symmetric_difference(user_a_articles, users_b_articles)
        writer.writerow([userA, recommended])
        with open('recommended.pickle', 'wb') as handle:
            pickle.dump([userA, recommended], handle)


def evaluation(recommended_file, test_file):
    with open(recommended_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        user_articles_dict = {}
        for row in reader:
            print(row['sme_id'])
            user_articles_dict.setdefault(row['cookie'], row['sme_id'])
        return user_articles_dict


# MAIN
trainFile = 'train_example.csv'
testFile = 'test_example.csv'
recommendedFile = 'recommended.csv'
topSimilarUsers = 5
userArticlesDict = create_user_articles(trainFile)
print(userArticlesDict)
print("OK - user1: [article1, article2, article3, ...] " + str(len(userArticlesDict)))
userSimilarityDict = create_user_similarity(userArticlesDict)
print("OK - user1: list([user2, similarity]) " + str(len(userSimilarityDict)))
topDict = limit_top_similarity(userSimilarityDict, topSimilarUsers)
print("OK - user1: TOPlist([user2, similarity]) " + str(len(topDict)))
recommend_articles(topDict, userArticlesDict, recommendedFile)
print("OK - user1: [recommend_article1, recommend_article2, recommend_article3, ...] ")
# evalu = evaluation(recommendedFile, testFile)
# print(evalu)
# print("OK - evaluation")

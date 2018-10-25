#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np 

def select_subset(product_set, traffic_set, question, answer, purchased_set = []):
    """
    function assumes you have already build the answer column
    
    enter the string corresponding to question number and to answer number
    """
    if answer=='idk': # case i don't know the answer return everything
        return(product_set, traffic_set, [])
    else:
        q_keep = set(product_set.loc[product_set["PropertyDefinitionId"]==int(question), "ProductId"].index.values) # had to remove this drop_duplicates() because it changed the index !!!!!!!
        a_keep = set(product_set.loc[product_set["answer"].astype(str)==str(answer), "ProductId"].index.values)
        total = a_keep.intersection(q_keep)
        products_to_keep = product_set.loc[total, "ProductId"].drop_duplicates().values          
        product_set = product_set.loc[product_set["ProductId"].isin(products_to_keep),]
        traffic_set = traffic_set.loc[traffic_set["Items_ProductId"].isin(products_to_keep),]
        if len(purchased_set) != 0:
            purchased_set = purchased_set.loc[purchased_set["Items_ProductId"].isin(products_to_keep),]
        else:
            purchased_set = []
        return(product_set, traffic_set, purchased_set)

def get_proba_Y_distribution(products_cat, purchased_cat, alpha=1):
    distribution = pd.DataFrame()
    unique_ids = products_cat['ProductId'].drop_duplicates().values
    number_prod_category_6 = len(unique_ids)
    proba_u = 1.0/number_prod_category_6 # if all products had the same probability to be bought
    distribution["uniform"] = np.repeat(proba_u, number_prod_category_6)
    distribution.index = unique_ids
    
    # step 2 take history into accounts
    sold_by_product = purchased_cat.groupby('ProductId').sum()["Items_ItemCount"]
    prod_ids = sold_by_product.index.values
    total_sold = np.sum(sold_by_product.values)
    adjust_proba_by_product = sold_by_product.values/float(total_sold)
    distribution["proportion_sold"] = 0.0 # init to 0
    distribution.loc[prod_ids, "proportion_sold"] = adjust_proba_by_product
    
    # step 3 add uniform and history and renormalize to get a proba
    unormalized_final_proba = distribution["uniform"].values + alpha*distribution["proportion_sold"].values 
    distribution["final_proba"] = unormalized_final_proba/np.sum(unormalized_final_proba)
    return(distribution)

def get_proba_Q_distribution(question, products_cat, traffic_processed, alpha=1):
    """
    assumes answer is already constructed
    """
    distribution = pd.DataFrame()
    #subset_cat = products_cat.loc[products_cat["PropertyDefinitionId"]==float(question),]
    number_products_total = len(products_cat['ProductId'].drop_duplicates().values)
    if (number_products_total==0):
        print('Nothing to return there is no product left with this filter')
        return(distribution)
     # step 1: probas is number of product per answer to the question (no history)
    possible_answers = products_cat.loc[products_cat["PropertyDefinitionId"]==int(question), "answer"] \
                                    .drop_duplicates().values.astype(float)
    nb_prod_per_answer = []
    for a in possible_answers:
        nb_prod_per_answer.append(len(select_subset(products_cat, traffic_processed, question, a)[0]["ProductId"].drop_duplicates().values))
    distribution["nb_prod"] = nb_prod_per_answer
    distribution.index = possible_answers #type float64
    s = np.sum(nb_prod_per_answer)
    distribution["catalog_proba"] = np.asarray(nb_prod_per_answer)/float(s)
    
    #step 2: add the history if available
    distribution["history_proba"] = 0
    if traffic_processed is not None:
        history_answered = []
        response = traffic_processed["answers_selected"].values
        for r_dict in response:
            if str(question) in r_dict:
                history_answered.extend(r_dict[str(question)])
        if not history_answered == []: 
            series = pd.Series(history_answered)
            add_probas = series.value_counts()
            s_add = sum(add_probas.values)
            add_probas = add_probas/s_add
            index = add_probas.index
            for i in index:
                if float(i) in distribution.index:
                    distribution.loc[float(i), "history_proba"] = add_probas.loc[i]
    distribution["final_proba"] = distribution["history_proba"].values + alpha*distribution["catalog_proba"].values
    S = np.sum(distribution["final_proba"].values)
    distribution["final_proba"] = distribution["final_proba"]/S
    """
#     with open('../data/probabilities.txt', 'a+') as f:
    with open('../data/probabilities.txt', 'w') as f:
        f.write("get_proba_Q_distribution: ")
        f.write("\n")
        distribution.to_csv(f, header=True)
        f.write("\n")
"""
    return(distribution)

def sample_from_distribution_df(dist_df, size=1):
    return(np.random.choice(dist_df.index.values, size=1, p=dist_df["final_proba"].values))

def get_questions(product_set):
    return(product_set["PropertyDefinitionId"].drop_duplicates().values)

def get_answers_y(y, product_set):
    questions = get_questions(product_set)
    tmp = product_set.loc[product_set["ProductId"]==y,]
    res = {}
    for q in questions:
        a = tmp.loc[product_set["PropertyDefinitionId"]==q,"answer"].values
        if len(a)==0:
            res.update({q: 'idk'})
        else:
            res.update({q: a[0]})
    return(res)

def get_filters_remaining(dataset):
    return(dataset["PropertyDefinitionId"].drop_duplicates().values)
    

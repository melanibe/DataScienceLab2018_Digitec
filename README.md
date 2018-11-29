# Improving Shopping at Galaxus-Digitec - Data Science Lab

## Overview of the project

### General setting and main goal
The goal of this project is to provide clients of Digitec/Galaxus with a reduced set of products that fits their criteria as fast as possible, by choosing the best sequence of questions/filters to ask.

Currently online: the user can filter out products using up to 27 different filters. This not very convenient for the user. 

We want to find a more interactive solution: ask questions to the user in order to help him/her restrict the set of products available according to his/her needs. We ask one question at a time. At each timestep, the user gives an answer and the next question is determined accordingly. The procedure stops when the set of remaining products is smaller than a certain threshold (currently 50 products). 

Note: We tested the prototype focusing on product category 6 (i.e. notebooks).

### Stages of the project

- Stage 1: Create a greedy algorithm to find the optimal ordering of the filters taking the user's answers into account at each timestep. We evaluated the performance of this algorithm in comparison to a random baseline.
- Stage 2: Imitation learning. Our greedy algorithm is very slow (computationally intensive). We want to build a neural network that would learn to copy the decisions of the optimal greedy algorithm to make it faster to use in production.
- Stage 3: Build the user interface and incorporate our best algorithm to find the next question.

## Data extraction preprocessing ('utils' subfolder)
The main script to get the necessary data for our algorithms is `init_dataframes.py`. This script can only be run on Digitec's machine as it assumes a connection to the Digitec database.

The script takes care of the following steps:

- Data extraction
  1. Extract the product catalog data corresponding to items of category 6.  (n = 7797)
  2. Extract relevant purchased articles (only items in category 6) and only consider order where there was only one unique ProductId bought.
  3. Extract traffic data that corresponds to SessionId where one notebook was bought (i.e. present in the previous dataset). Only keep the rows where the RequestUrl is parsable (very few rows unfortunately).
- Data preprocessing
  1. Issue in original dataset: sometimes the answer is stored in the PropertyValue column (continuous case) sometimes in the PropertyDefinitionOptionId column (discrete set of answers):
      - Build one unique "answer" column that contains the answers regardless of the type of the question.
      - In the continuous case (answer is stored in PropertyValue) sometimes there are too many values to propose to the user. We created a new answer in this case: based on the 10th quantile we restricted the set of possible answers to 10 bins. Example for height. 
- Output files
The output dataframe that are used throughout the project are saved in the `data` subfolder. 
  - products_cat: extract of product catalog for category 6
  - purchased_cat: purchases from products of category 6.
    only keep purchases where one unique productId was bought.
  - traffic_cat: table containing the filters used for purchases in purchased_cat.
  - filters_def_dict: dict where key is questionId
    value is array of all possible (modified) answers
  - type_filters: dict {str(float(questionId)): 'mixed'|'bin'|'value'|'option'}
    question_text_df: dataframe with columns PropertyDefinitionId
    and PropertyDefinition (string of question)
  - answer_text: dataframe with columns question_id, answer_id and answer_text.
#### Summary of the dataframes available for this project. 
| Dataframe filename  | Alias commonly used throughout the code |Columns available |
| ------------- | ------------- | ------------- |
| products_table  | products_cat | ProductId, BrandId, ProductTypeId, PropertyValue, PropertyDefinitionId, PropertyDefinitionOptionId, answer  |
| traffic_table  | traffic_cat | SessionId, answers_selected, Items_ProductId  |
| purchased_table | purchased_cat | ProductId, UserId, OrderId, SessionId, Items_ProductId, Items_ItemCount  |
| question_text_df  | | PropertyDefinition, PropertyDefinitionId  |
| answer_text | | answer_id, question_id , answer_text |

## Stage 1 - Greedy algorithm - Max Mutual Information Algorithm ('greedy' subfolder)
Max_MI algorithm: Greedy algorith that selects the next question/filter by maximizing the varying component of the mutual entropy.
Baseline algorithm: Next question/filter asked is chosen randomly from the set available questions in the updates product subset.

For the MAx_MI algorithm, run `greedy/evaluation_eliminate.py`\\
Arguments that can be added are
- -s (number of products to test on)
- -hist (Boolean to indicate whether to use history data)
- -a (parameter to determine the importance given to history data)
- -pidk (probability of user answering I don't know to a question)
- -p2a (probability of user giving 2 answers to a question)
- -p3a (probability of user giving 3 answers to a question)
The results obtained will be compared with the random baseline

## Stage 2 - Imitation Learning - DAgger algorithm ('dagger' subfolder)
We used imitation learning (an alternative to reinforcement learning for learning sequential decision-making policies) to
train our model to choose the most appropriate next question/filter, using the data generated by our greedy Max MI algoritm.\\

Run `dagger/dagger_main.py`

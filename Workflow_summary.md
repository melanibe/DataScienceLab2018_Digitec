
# WORKFLOW TO GET THE FILTERS AND ANSWERS PER CATEGORY AS WELL AS WHICH FILTERS WERE USED FOR EACH BOUGHT PRODUCT IN THE PAST

## STEP 1: Choose one product category
For prototype 1, we restrict ourselves to category 6 'notebook' for now.

cf `products_6`

## STEP 2: Modify filters if necessary i.e. make sure that all filters are categorical and not continuous
We want to ask questions to the user for which if should choose among a fixed set of answers (set defined per questions). However, for some filters the stored answer is a value (e.g. size) and therefore there could be arbitrarily many possible answers (up to 215 for product category 1099 for example). Obviously we won't offer 215 possible answers to the users, so we want to create "grouped_answers" i.e. creating bins for example size from 0 to 10 cm, from 10cm to 20cm etc... The bins are created via a histogram over the set of values found for this question in the product catalog. If there are less than 10 possible values for a filter we keep all the original values as possible answers. Hence, we derive a new product table containing in the column `Answer`:
    - either the original answer Id (e.g. Deutsch, French etc...) this Id has to be mapped to its meaning in words.
    - either the original answer value (2, 3, 10) if less than 10 different values, the stored value is the answer.
    - either the bin where the original value lies in, the stored value is the lower bound of bin corresponding to the value.
To keep track of which filters have been aggregated via histogram we create a dictionary `filter_type= {'filter': 'option'|'value'|'bin'}` and another dict `possible_answer = {'filter': [possible answer after aggregation]}`. It is important to know the type of filter because if we want to ask the question to the user we need to know the set of possible answer hence for example if my filter corresponds to options I know that I have to find the definition of the option with the id stored in the answer column. If it is a value I know that the answer column is the value itself (not an id). It is a bin, I should display the possible answers as ranges to the users (and not only the lower  bound of the interval). 

Use `create_categories` function NOT FINISHED YET
    
## STEP 3: Create the reduced_purchase table containing only the purchased product for which the final basket only contains one product
If there are several product bought in the same session we can not separate which clicks where made for which product so we chose to only use historic data for order that contained only one single product Id. 

cf. `reduced_purchased`

## STEP 4: Join reduced_purchase and product to find all product purchase in the chosen category
The new table contains all the info about the product for each product purchased in the category 6. 

cf `category_purchased_6`

## STEP 5: Join the category_purchase and the traffic table to know which requestURL where used to get the final product. 

cf `traffic_purchased_6`

WARNING: creating this table directly as a dataframe via `pd.read_sql_query` takes too much time, the notebook stops working before the query is executed. The only solution that was found is to physically create the tables `reduced_purchased`, `category_purchased_6` and `traffic_purchased_6` on the database. And then loading them as pandas dataframe for the next steps. This is not a problem because once these table are created they represent everything we need but it can't be a viable solution for a real implementation because nobody wants to create the tables for each category. However this issue is only relevant for stage 3. The found solution is sufficient for stage 1 and stage 2.

## STEP 6: Have to map the answer to new answers derived in step 2. 

Use `categorize()` and `process_answers_filter` functions

## STEP 7: Finally get a list of all filters used and their corresponding answers per Session

Use `filters_answers_per_requestURL` function and `find_all_filters_answers` function (still to be written).


from pyspark.ml.recommendation import ALS
from pyspark.sql import SparkSession
import pandas as pd
import sys

spark = SparkSession.builder.appName('ensemble average').getOrCreate()

# normalize a value to the range 1-5
def normalize(x):
    return 4 * (x - min_value) / (max_value - min_value) + 1

train_input = sys.argv[1]
test_input = sys.argv[2]
output = sys.argv[3]

# Read train and test data to Pandas dataframes
train_raw = pd.read_csv(train_input)
test_raw = pd.read_csv(test_input)

# Delete unused columns
test_raw = test_raw.drop(['date'],axis=1)
train_raw = train_raw.drop(['train_id','date'],axis=1)

# Create Spark Dataframes
train = spark.createDataFrame(train_raw)
test = spark.createDataFrame(test_raw)

# Create ALS predictor, fit the model and generate the predictions
als = ALS(userCol="user_id", itemCol="business_id", ratingCol="rating")
model = als.fit(train)
predictions = model.transform(test)

# Store result in a pandas dataframe
predict_df = predictions.select('test_id','prediction').coalesce(1).orderBy('test_id').toPandas()

### Scaling the model to range 1-5
max_value = predict_df.prediction.max()
min_value = predict_df.prediction.min()
predict_df['rating'] = predict_df.prediction.apply(normalize)

predict_df = predict_df[['test_id','rating']]

# Save the predictions in a file to submit to Kaggle
predict_df.sort_values('test_id').to_csv(output,index=False)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#reading our TSV files
lfm_df = pd.read_csv('userid-timestamp-artid-artname-traid-traname.tsv', 
                        sep='\t', header=None, error_bad_lines=False)
#Added "error_bad_lines=False" as we were getting errors due to unexpected numbers of fields on 9 lines.
lfm_df.columns = ['user_id', 'timestamp', 'artist_id', 'artist_name','track_id', 'trackname']
#Dropping columns that have little use to me. Those being "artist_id", "artist_name", "track_id", and "trackname".
lfm_df_trim = lfm_df.drop(columns=['artist_id', 'artist_name', 'track_id', 'trackname'])
#Converting the timestamp column to something a little more readable.
lfm_df_trim['timestamp'] = pd.to_datetime(lfm_df_trim['timestamp'], format='%Y-%m-%dT%H:%M:%SZ')
lfm_df_trim.sort_values(by='timestamp', ascending=False).head(10)

#Dropping outliers. There are a couple of rows with timestamp values more than a year later than the majority 
#of the values which otherwise have a nice daily progression. The removed rows have years listed as 2010 and 2013.
lfm_df_trim = lfm_df_trim.reset_index()
lfm_df_trim = lfm_df_trim.drop(lfm_df_trim.index[lfm_df_trim['index'].isin([14293405,7696484])])
lfm_df_trim = lfm_df_trim.drop(columns=['index'])
lfm_df_trim.sort_values(by='timestamp', ascending=False).head(10)

#Same preprocessing steps for the userid-profile dataset.
lfm_users = pd.read_csv('userid-profile.tsv', sep='\t')
lfm_users['registered'] = pd.to_datetime(lfm_users['registered'],format='%b %d, %Y')
lfm_users.head()

#Sorting user_id by number of timestamps with the intention of finding the users who use the platform the most.
lfm_timestamp = lfm_df_trim.groupby(['user_id']).agg('count').reset_index()
#Sorting user_id by date of signup with the intention of finding the oldest accounts. Dropping N/A values for registered date.
lfm_signup = lfm_users.sort_values('registered').dropna(subset=['registered']).reset_index(drop=True)
lfm_signup.head()

#Trying to build an RMF analysis. We don't have any values for money so this will seem to be an RF analysis.
lfm_recency = lfm_df_trim.groupby(by='user_id', as_index=False)['timestamp'].max()
lfm_recency.columns = ['user_id','last_use']

#Creating a "most recent day" value.
recent_date = lfm_recency['last_use'].max()
recent_date

#Merging dataframes.
rfm = lfm_timestamp.merge(lfm_recency, on='user_id')

#Aggregating data to get a list of number of days since last use to use for our recency calculation.
rfm1 = rfm.groupby('user_id').aggregate({'last_use': lambda date: (recent_date - date.max()).days}).reset_index()
rfm1['last_use'] = rfm1['last_use'].astype(int)

lastfm_rf = rfm1.merge(rfm, on='user_id').drop(columns = 'last_use_y')
lastfm_rf.columns = ['user_id', 'recency', 'frequency']
lastfm_rf.head()

#We don't have a Monetary value for our RFM value so let's just make a different value to check.
#I want to track the average uses per day, as unlike my current frequency value, it does not
#discriminate against users who have not been registered as long as others.

#Trimming our user profile data to remove columns that won't help us at the moment.
#This data is useful for other reasons however, as an example, this demographic data can be used
#to find which age groups, genders, and countries are more likely to be frequent users of LastFM.
lfm_users_trim = lfm_users.dropna(subset=['registered']).drop(columns=['gender','age','country'])
lfm_users_trim.columns = ['user_id','registered']

#Creating a new table of the number of total days registered for each user as 'age'.
lfm_recency_registered = lfm_users_trim.merge(lfm_recency, how='left', on='user_id')
lfm_registered_days = lfm_recency_registered.groupby('user_id').agg({'registered': lambda date: (recent_date - date.max()).days}).reset_index()
lfm_registered_days['registered'] = lfm_registered_days['registered'].astype(int)
lfm_registered_days.columns = ['user_id','age']
lfm_registered_days.sort_values('age').head()

#We have a couple of users with negative 'age' values caused by their registration date being marked as
#later than our "recent_date" value. I'm just going to drop these two users for simplicity.
lfm_registered_days = lfm_registered_days.drop(lfm_registered_days.index[lfm_registered_days['age'] < 0])
lfm_registered_days.sort_values('age').head()

#With our total days registered and our total uses (frequency) value, we can now calculate
#average uses per day for each user.
lfm_score = lfm_registered_days.merge(lastfm_rf, how='left', on='user_id')
lfm_score['uses_per_day'] = lfm_score['frequency']/lfm_score['age']

#Dropping the age column as it isn't particularly useful anymore.
lfm_score = lfm_score.drop(columns = ['age'])

#Let's take a look at some plots to see the distribution of data for each of our metrics.
plt.figure(figsize=(12,12))
plt.subplot(3, 1, 1); sns.distplot(lfm_score['recency'])
plt.subplot(3, 1, 2); sns.distplot(lfm_score['frequency'])
plt.subplot(3, 1, 3); sns.distplot(lfm_score['uses_per_day'])

#Finally, let's put together the "RFU" (Recency, Frequency, Uses Per Day) Analysis.
#First we add columns for each user based on where they fall in the quantiles for each metric.
#Note that recency is reversed as the lower recency values are more desireable.
lfm_score['R_value'] = pd.qcut(lfm_score['recency'], 4, ['4','3','2','1'])
lfm_score['F_value'] = pd.qcut(lfm_score['frequency'], 4, ['1','2','3','4'])
lfm_score['U_value'] = pd.qcut(lfm_score['uses_per_day'], 4, ['1','2','3','4'])

#Combining this all to get our score.
lfm_score['RFU_score'] = lfm_score.R_value.astype(str) + lfm_score.F_value.astype(str) + \
    lfm_score.U_value.astype(str)
lfm_score.head(10)

#Using our new RFU score, let's take a look at some of LastFM's best customers.
#Sorting by uses_per_day as I believe it to be a good metric for judging how active current users are.
toplfm_score = lfm_score[lfm_score['RFU_score']=='444'].sort_values('uses_per_day', ascending=False)
toplfm_score.head(10)
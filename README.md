# LastFM
Customer scoring model created using sampled data from LastFM users.
(Found at http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html)

To score customers in this dataset, I took an RFM (Recency, Frequency, Monetary Value)
approach. With a lack of monetary information in this dataset, I decided to replace it
with a value of “uses per day” found by dividing the user’s total number of uses
(frequency) by their account age.

I divided each metric into quantiles ranging from 1 to 4, with 4 being the most desirable 
value and 1 being the least desirable, and combined the values into our new “RFU” score,
which was used to find our top 10 most valued users.

To perform this “RFU” analysis, I performed a number ofpreprocessing steps including 
changing the datetime values into a format that was more usable for my approach and 
trimming off a number of unnecessary columns. Additionally, I removed a couple of outlier 
rows that had timestamp values listed a year or more after the majority of values.

For the “R” of my “RFU” analysis, I created a recency value that is simply a measurement
of the most recent date each user played a song on the platform compared to the most
maximum date value in the dataset. A measurement of how many days it has been since
the last time the user listened to a song with a lower number being better.

My “frequency” value is a measurement of how many times a user has played any song
using the platform, which I created by just counting up how many times any particular
user_id shows up in our dataset.

Lastly, the “uses per day” value was created by dividing the frequency value I made by
the total number of days that the user’s account has been created for. This value is very
similar to frequency in that it measures how much the user uses the platform, however I
decided to use this metric as it does not discriminate against users who have relatively
young accounts compared to others.

# Exploring the data

As fun as building out the database was, I've found more utility getting my hands dirty and learning what it says about my listening habits on Spotify. When I listen to music I tend to either put on a video from Youtube to play in the background or stream from Spotify. Perhaps, the youtube videos could be another project, but I don't want to get carried away dreaming, let's focus on the data I was able to import from Spotify and what it says. I created my account in 2013 so there is over ten years of data to parse!

---

## The Shape of the Data

| year | plays |
|------|-------|
| 2018 | 14725 |
| 2019 | 13296 |
| 2025 | 11165 |
| 2020 | 8315  |
| 2024 | 7901  |
| 2022 | 7350  |
| 2023 | 6192  |
| 2021 | 5145  |
| 2026 | 5143  |
| 2017 | 3628  |
| 2016 | 67    |
| 2013 | 17    |
| 2015 | 10    |

The first few years after creating my Spotify account in 2013, I used the service sparsely to listen to music. I remember being annoyed by the ads and my car had a CD player so I would buy CD's and download the mp3s onto my machine where I would then burn custom mixes. I would keep a *thick* notebook of CD's in my car so I had the perfect mix of music for every ocassion. Remember those days? Good times, good times.

There are two periods where I heavily relied upon Spotify to stream music. The years of 2018-2020 and 2023-2026 (projected). Since the dataset only captures listening habits from the first half of 2026, I expect that number to climb and match the previous 2 years. I have noticed Spotify is more often than not the platform I use to listen to music and I am not alone:
> 73% of the US population (aged over 12) listen to online audio every week... 35% of the population listened to Spotify in [March 2026]
[source](https://musically.com/2025/03/24/report-offers-us-listening-stats-for-spotify-and-its-rivals/)

With this in mind, I was curious how my previous peak compared to more recent years. Spotify is notorious for obfuscating their metrics so there was a mismatch in the JSON for the first era, notably they did not track how often a song was skipped until 2022. Regardless, I still think this dataset tells a story worth telling.

---

## Two Distinct Eras

The first era is defined by finally getting spotify premium so no more ads! As you can see, I began utlizing the platform much more to listen to music. This was always my introduction to recommendation algorithms where I would await my Dicover Weekly playlist to update. I enjoyed listening to old favorites like Interpol, Radiohead, Logic and Kid Cudi while discovering new artists like J Balvin and Frank Ocean. As you can see I became a big fan and had *Blonde* on repeat during that time.

**Top Artists 2018-2020**

|     artist      | plays |
|-----------------|-------|
| Frank Ocean     | 460   |
| Interpol        | 344   |
| BROCKHAMPTON    | 309   |
| Kanye West      | 243   |
| Glass Animals   | 183   |
| Radiohead       | 167   |
| Pinback         | 154   |
| Logic           | 154   |
| EARTHGANG       | 142   |
| The Beatles     | 130   |
| Deftones        | 130   |
| KIDS SEE GHOSTS | 120   |
| TV On The Radio | 115   |
| Allan Rayman    | 115   |
| J Balvin        | 112   |


**Top Tracks 2018-2020**

|         name         |     artist      | plays |
|----------------------|-----------------|-------|
| Pink + White         | Frank Ocean     | 45    |
| Baby                 | Ariel Pink      | 44    |
| White Ferrari        | Frank Ocean     | 44    |
| Liquor Sto'          | EARTHGANG       | 41    |
| He Can Only Hold Her | Amy Winehouse   | 37    |
| REEL IT IN           | Aminé           | 37    |
| Plug Walk            | Rich The Kid    | 36    |
| Don't Move           | Phantogram      | 35    |
| Moon River           | Frank Ocean     | 35    |
| anemone              | slenderbodies   | 35    |
| Cudi Montage         | KIDS SEE GHOSTS | 34    |
| Naive                | The Kooks       | 34    |
| CAROUSEL             | Aries           | 33    |
| This Modern Love     | Bloc Party      | 32    |
| Leif Erikson         | Interpol        | 31    |

The next peak of my spotify listening came in 2024 and is going strong to this day. I began working on an assembly line where we were permitted to use headphones. During this time, I also began to appreicate genres that that I had judged pre-maturaly. I never though metal music would speak to me, but what can I say, when I get obssessed with something it takes over.


**Top Artists 2023-2026**

|      artist       | plays |
|-------------------|-------|
| Death             | 481   |
| Carcass           | 453   |
| At The Gates      | 415   |
| Deafheaven        | 409   |
| Greet Death       | 330   |
| Caroline Polachek | 254   |
| Radiohead         | 253   |
| Incubus           | 253   |
| Arcade Fire       | 249   |
| Slow Pulp         | 236   |
| King Krule        | 226   |
| Show Me the Body  | 222   |
| Björk             | 217   |
| Mount Kimbie      | 211   |
| Justin Bieber     | 204   |


**Top Tracks 2024-2026**

|         name          |      artist       | plays |
|-----------------------|-------------------|-------|
| Falling Apart         | Slow Pulp         | 82    |
| Under A Serpent Sun   | At The Gates      | 76    |
| Mad Riches            | Sonder            | 63    |
| Do You Feel Nothing?  | Greet Death       | 61    |
| Pretty In Possible    | Caroline Polachek | 60    |
| Slaughter Of The Soul | At The Gates      | 56    |
| Symbolic              | Death             | 56    |
| Seaforth              | King Krule        | 50    |
| Where Am I?           | Title Fight       | 49    |
| Free Mind             | Tems              | 45    |
| At Home               | Slow Pulp         | 44    |
| Avril 14th            | Aphex Twin        | 44    |
| ALL I CAN TAKE        | Justin Bieber     | 43    |
| Hit Me Where It Hurts | Caroline Polachek | 43    |
| Into The Dead Sky     | At The Gates      | 43    |

What is interesting about this period is how much more diverse my listening was. I discovered an appreciation for metal (At the Gates has three tracks in my top ten and Death was my most listened to artist), but there's also Justin Bieber (another artist I had previously not given a chance), Aphex Twin and Caroline Polachek. I do think there is at least one song from every genre that someone will appreciate if they keep an open mind. This insight is backed up by the data:

| year | unique_artists | total_plays | plays_per_artist |
|------|----------------|-------------|------------------|
| 2025 | 1559           | 11165       | 7.2              |
| 2018 | 2427           | 14725       | 6.1              |
| 2024 | 1310           | 7909        | 6.0              |
| 2022 | 1596           | 8619        | 5.4              |
| 2019 | 2522           | 13296       | 5.3              |
| 2026 | 1116           | 5143        | 4.6              |
| 2023 | 1482           | 6192        | 4.2              |
| 2020 | 1963           | 8315        | 4.2              |
| 2021 | 1290           | 5145        | 4.0              |
| 2017 | 905            | 3628        | 4.0              |
| 2016 | 36             | 67          | 1.9              |
| 2013 | 9              | 17          | 1.9              |
| 2015 | 10             | 10          | 1.0              |

`plays_per_artist` represents the time spent on one particular artist. In more recent years, I have given more artists an opportunity to catch my ear.

---

## When I Listen

| hour | plays |
|------|-------|
| 16   | 6894  |
| 01   | 6486  |
| 02   | 6084  |
| 17   | 6006  |
| 23   | 5678  |
| 00   | 5438  |
| 22   | 5196  |
| 15   | 5129  |
| 18   | 5063  |
| 19   | 4568  |
| 21   | 4181  |
| 20   | 4061  |
| 03   | 3948  |
| 14   | 3318  |
| 04   | 2618  |
| 05   | 2518  |
| 13   | 1679  |
| 06   | 1654  |
| 07   | 1362  |
| 12   | 815   |
| 08   | 655   |
| 09   | 336   |
| 11   | 294   |
| 10   | 250   |

Interestingly, I seem to listen late at night. My sleeping habits have matured as I entered my thirties, I think. Let's see how this looks by year:

| hour | plays |
|------|-------|
| 01   | 2120  |
| 02   | 1927  |
| 16   | 1624  |
| 17   | 1576  |
| 15   | 1454  |
| 18   | 1425  |
| 03   | 1413  |
| 19   | 1232  |
| 21   | 1205  |
| 00   | 1196  |
| 22   | 1193  |
| 20   | 1192  |
| 14   | 1158  |
| 04   | 1088  |
| 13   | 1074  |
| 23   | 1030  |
| 05   | 806   |
| 12   | 506   |
| 06   | 429   |
| 07   | 290   |
| 08   | 117   |
| 11   | 110   |
| 09   | 37    |
| 10   | 15    |

<!-- RUN NEW QUERY COMPARING HOURS LISTENED GROUPED BY YEAR -->

---

## How I Listen

|   reason_start    | count | percentage |
|-------------------|-------|------------|
| clickrow          | 29993 | 35.6       |
| fwdbtn            | 22831 | 27.1       |
| trackdone         | 21164 | 25.1       |
| backbtn           | 5630  | 6.7        |
| unknown           | 2480  | 2.9        |
| playbtn           | 1047  | 1.2        |
| appload           | 707   | 0.8        |
| remote            | 227   | 0.3        |
| trackerror        | 86    | 0.1        |

I seem to know what I want to listen to rather than letting playlists play the next song. This maps with how I like to listen to music. I want to listen to what I want to listen to, I don't trust an algorithm or shuffle to play the next perfect song for the moment, but when I'm in the flow anything works.

---

## All Time Favorites

|                  name                   |      artist      | plays | skip_rate_pct |
|-----------------------------------------|------------------|-------|---------------|
| Pink + White                            | Frank Ocean      | 72    | 15.3          |
| White Ferrari                           | Frank Ocean      | 70    | 8.6           |
| Evil                                    | Interpol         | 68    | 14.7          |
| Leif Erikson                            | Interpol         | 68    | 11.8          |
| Baby                                    | Ariel Pink       | 64    | 7.8           |
| He Can Only Hold Her                    | Amy Winehouse    | 62    | 14.5          |
| Friendship (Is A Small Boat In A Storm) | Chicano Batman   | 58    | 6.9           |
| Idioteque                               | Radiohead        | 58    | 12.1          |
| Chop Suey!                              | System Of A Down | 56    | 10.7          |
| REEL IT IN                              | Aminé            | 55    | 16.4          |
| Tennessee                               | Allan Rayman     | 55    | 9.1           |
| Liquor Sto'                             | EARTHGANG        | 54    | 9.3           |
| anemone                                 | slenderbodies    | 54    | 5.6           |
| Youth                                   | Glass Animals    | 53    | 9.4           |
| Crew (feat. Brent Faiyaz & Shy Glizzy)  | GoldLink         | 52    | 0.0           |

These tracks heavily favor top songs listened to pre-2022 since the skipped paramter is not consistent.

---

## Complicated Relationships

|             name              |       artist        | plays | skip_rate_pct |
|-------------------------------|---------------------|-------|---------------|
| We Are Not A Football Team    | Minus the Bear      | 42    | 61.9          |
| Fishbrain                     | Mount Kimbie        | 39    | 69.2          |
| I Hate It Too                 | Hum                 | 37    | 62.2          |
| Drive                         | Incubus             | 35    | 65.7          |
| Again                         | Greet Death         | 33    | 72.7          |
| Maine                         | hey, nothing        | 32    | 65.6          |
| Door                          | Caroline Polachek   | 31    | 71.0          |
| Eventually                    | Tame Impala         | 31    | 61.3          |
| Make It Easy On Yourself      | The Walker Brothers | 30    | 63.3          |
| New Person, Same Old Mistakes | Tame Impala         | 30    | 66.7          |

These are tracks I tend to listen to frequently, but am often not in the mood when they come up during shuffle. You can see by the play_rate, I don't not enjoy them, but they are skipped more often than not. All of these tend to be post-2022 because the skipped feature was not measured in the data until that time.

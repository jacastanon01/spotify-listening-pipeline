# Exploring the data

As fun as building out the database was, I've found more utility getting my hands dirty and learning what it says about my listening habits on Spotify. When I listen to music I tend to either put on a video from Youtube to play in the background or stream from Spotify. Perhaps, the youtube videos could be another project, but I don't want to get carried away dreaming, let's focus on the data I was able to import from Spotify and what it says. I created my account in 2013 so there is over ten years of data to parse!

---

## The Shape of the Data

The first few years after creating my Spotify account in 2013, I used the service sparsely to listen to music. I remember being annoyed by the ads and my car had a CD player so I would buy CD's and download the mp3s onto my computer where I would then burn custom mixes. I would keep a *thick* notebook of CD's in my car so I had the perfect mix of music for every ocassion. Remember those days? Good times, good times.

Oh yeah, the data. So here I qeuried how often a track was played per year. I am not disecting the time played (which Spotfy presents as `ms_played` in the JSON), but rather counting the total streaming events per year. This tells you which years were spent mostly using Spotify to listen to songs.

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

There are two periods where I heavily relied on Spotify. The first spans 2018 to 2020, peaking in 2018 with nearly 15,000 plays. Listening stayed elevated through 2019 and into 2020, likely sustained by the pandemic and time at home, before declining through 2021 and 2022. The second period begins around 2024 and continues into 2025, though it hasn't matched the earlier highs. 2026 is likely to surpass 10,000 track streams, but since 2026 is only halfway represented in the dataset, I'll leave it as is rather than project forward.

I have noticed Spotify is more often than not the platform I use to listen to music and I am not alone:
> 73% of the US population (aged over 12) listen to online audio every week... 35% of the population listened to Spotify in [March 2026]
[source](https://musically.com/2025/03/24/report-offers-us-listening-stats-for-spotify-and-its-rivals/)

With this in mind, I was curious how my previous peak compared to more recent years. Spotify is notorious for obfuscating their metrics so there was a mismatch in the JSON for the first era, notably they did not track how often a song was skipped until 2022.

---

## Two Distinct Eras

The first era is defined by finally getting spotify premium so no more ads! As you can see, I began utlizing the platform much more to listen to music. This was always my introduction to recommendation algorithms where I would await my Dicover Weekly playlist to update. I enjoyed listening to old favorites like Interpol, Radiohead, Logic and Kendrick Lamar while discovering new artists like J Balvin and Frank Ocean. As you can see I became a big fan of Mr. Ocean and had *Blonde* on repeat during that time.

**Top Artists 2018-2020**

|      artist      | plays | minutes_played |
|------------------|-------|----------------|
| Frank Ocean      | 539   | 1097.7         |
| Interpol         | 362   | 587.3          |
| Kanye West       | 300   | 516.3          |
| Logic            | 220   | 442.1          |
| EARTHGANG        | 154   | 423.1          |
| BROCKHAMPTON     | 330   | 417.2          |
| Talking Heads    | 129   | 294.2          |
| Childish Gambino | 146   | 281.4          |
| J Balvin         | 159   | 261.5          |
| Radiohead        | 187   | 261.2          |
| Deftones         | 147   | 254.5          |
| Glass Animals    | 224   | 253.5          |
| Kendrick Lamar   | 110   | 239.7          |
| KIDS SEE GHOSTS  | 128   | 233.9          |
| Pinback          | 175   | 230.1          |

**Top Tracks 2018-2020**

|                       name                        |         artist          | plays | minutes_played |
|---------------------------------------------------|-------------------------|-------|----------------|
| Liquor Sto'                                       | EARTHGANG               | 44    | 220.9          |
| White Ferrari                                     | Frank Ocean             | 46    | 145.6          |
| Baby                                              | Ariel Pink              | 50    | 118.0          |
| Reborn                                            | KIDS SEE GHOSTS         | 30    | 100.3          |
| Love Again                                        | Ta-ku                   | 30    | 95.3           |
| In The Fade/Feel Good Hit Of The Summer (Reprise) | Queens of the Stone Age | 29    | 94.2           |
| Simulation (feat. Swamp Dogg, Justin Vernon)      | Naeem                   | 22    | 92.0           |
| Pink Matter                                       | Frank Ocean             | 33    | 90.9           |
| To Zion (feat. Carlos Santana)                    | Ms. Lauryn Hill         | 29    | 90.1           |
| Missed Calls                                      | EARTHGANG               | 34    | 87.1           |
| Pink + White                                      | Frank Ocean             | 54    | 85.5           |
| He Can Only Hold Her                              | Amy Winehouse           | 43    | 85.0           |
| Addicted                                          | JMSN                    | 30    | 84.3           |
| Provider                                          | Frank Ocean             | 40    | 80.2           |
| Afro Blue                                         | Robert Glasper          | 28    | 79.9           |

EARTHGANG was another artist I discovered during this time and took a liking to. The top 3 Frank Ocean songs come out to over 300 minutes, which don't even cover a quarter of my listening time for him during this period.

The next peak of my Spotify listening journey came in 2024 and 2025. I began working on an assembly line where we were permitted to use headphones. During this time, I also began to appreicate genres that that I had judged pre-maturely. I never though metal music would speak to me, but what can I say, when I get obssessed with something it takes over.


**Top Artists 2023-2025**

|      artist       | plays | minutes_played |
|-------------------|-------|----------------|
| Deafheaven        | 399   | 1594.1         |
| Death             | 405   | 1238.9         |
| Carcass           | 411   | 1085.8         |
| At The Gates      | 392   | 836.5          |
| Greet Death       | 313   | 636.0          |
| Slow Pulp         | 225   | 487.1          |
| Arcade Fire       | 238   | 453.6          |
| King Krule        | 224   | 446.8          |
| Caroline Polachek | 252   | 440.3          |
| Radiohead         | 208   | 415.1          |
| Mount Kimbie      | 192   | 378.1          |
| Incubus           | 204   | 377.6          |
| Björk             | 209   | 367.7          |
| Hum               | 153   | 354.1          |
| Minus the Bear    | 197   | 353.4          |


**Top Tracks 2024-2025**

|                      name                       |      artist       | plays | minutes_played |
|-------------------------------------------------|-------------------|-------|----------------|
| Falling Apart                                   | Slow Pulp         | 78    | 237.6          |
| Under A Serpent Sun                             | At The Gates      | 69    | 218.7          |
| Symbolic                                        | Death             | 44    | 197.8          |
| Do You Feel Nothing?                            | Greet Death       | 56    | 176.6          |
| Sea of Love                                     | The National      | 36    | 127.1          |
| Spring Is Coming With a Strawberry in the Mouth | Roger Doyle       | 24    | 126.2          |
| I Want to Be with You                           | Sadness           | 32    | 125.7          |
| Pretty In Possible                              | Caroline Polachek | 60    | 124.2          |
| Dream House                                     | Deafheaven        | 19    | 123.4          |
| Seaforth                                        | King Krule        | 49    | 117.4          |
| Corporal Jigsore Quandary                       | Carcass           | 27    | 114.4          |
| Sunbather                                       | Deafheaven        | 26    | 114.4          |
| Pink Elephant                                   | Arcade Fire       | 33    | 112.8          |
| We Were Born The Mutants Again With Leafling    | of Montreal       | 29    | 110.0          |
| Canary Yellow                                   | Deafheaven        | 13    | 107.2          |

Deafheaven's number of `plays` in the artists table may seem low compared to the other top 3 metal groups. They are inspired by black metal and that means long, epic songs often spanning ten minutes total. Another interesting note, I first heard "Spring Is Coming With a Strawberry in the Mouth" by Caroline Polachek on her album. When I found out it was a cover, I listened to the original by Roger Doyle, and apparantly liked it much more than Caroline's version. Besides the metal and synth-pop, there is a decent amount of time listening to an old favorite: indie rock.

What is interesting about this period is how much more diverse my listening was. My top 4 most listened to artists are metal bands, but there's also Bjork, Arcade Fire and King Krule in there. I don't think it's a coincedence for that diversity:

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

`plays_per_artist` represents the breadth of artists listened to in a particular year. In more recent years, I have given more artists an opportunity to catch my ear.

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

Late afternoons and late nights.

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

This is genuinely one of the more fun parts of this project. Finding ways to measure how a track is my favorite demonstrates the importance of good data modeling. At first, I used the averages of the skipped fields (which is a boolean(which in sqlite is represent by a 1 or 0)) to determine how often a track was skipped, but looking at my data that is an unreliable field to rely on.

| year | total_streams | null_skipped | not_skipped | skipped | skip_rate_pct |
|------|---------------|--------------|-------------|---------|---------------|
| 2013 | 17            | 0            | 10          | 7       | 41.2          |
| 2015 | 10            | 0            | 2           | 8       | 80.0          |
| 2016 | 67            | 0            | 67          | 0       | 0.0           |
| 2017 | 3628          | 0            | 3628        | 0       | 0.0           |
| 2018 | 14725         | 0            | 14725       | 0       | 0.0           |
| 2019 | 13296         | 0            | 13296       | 0       | 0.0           |
| 2020 | 8315          | 0            | 8315        | 0       | 0.0           |
| 2021 | 5145          | 0            | 5145        | 0       | 0.0           |
| 2022 | 8619          | 0            | 7781        | 838     | 9.7           |
| 2023 | 6192          | 0            | 1723        | 4469    | 72.2          |
| 2024 | 7909          | 0            | 2873        | 5036    | 63.7          |
| 2025 | 11165         | 0            | 3773        | 7392    | 66.2          |
| 2026 | 5143          | 23           | 1539        | 3581    | 69.9          |

One of the peaks of my listening history (2018-2019) currently would've had a skip rate of 0, which would skew the findings to be biased toward songs listened to during that period of time. There must be another way. Fortunantly, I added the `reason_end` and `reason_start` fields to my schema and they came in handy here. As we saw earlier, I tend to be deliberate with how I chose my tracks. Here are songs that have at least half an hour of playing time with the reason starting being a 'clickrow', which means I chose the track and the reason ending being 'trackdone', which indicates I let the track play to completion without interruption. Ordered by the minutes played

|                      name                       |      artist       | minutes_played |
|-------------------------------------------------|-------------------|----------------|
| Symbolic                                        | Death             | 83.2           |
| Falling Apart                                   | Slow Pulp         | 62.4           |
| What Once Was                                   | Her's             | 56.6           |
| Dream House                                     | Deafheaven        | 55.4           |
| White Ferrari                                   | Frank Ocean       | 48.9           |
| Do You Feel Nothing?                            | Greet Death       | 48.8           |
| Pretty In Possible                              | Caroline Polachek | 41.2           |
| Evil                                            | Interpol          | 40.4           |
| Obstacle 2                                      | Interpol          | 40.4           |
| Unison                                          | Björk             | 39.4           |
| Under A Serpent Sun                             | At The Gates      | 39.2           |
| Accept Yourself - David Jensen Session 25/08/83 | The Smiths        | 38.3           |
| Pachuca Sunrise                                 | Minus the Bear    | 38.0           |
| Liquor Sto'                                     | EARTHGANG         | 37.2           |
| Man Of Oil                                      | Animal Collective | 37.1           |
| Nights                                          | Frank Ocean       | 36.3           |
| Nikes                                           | Frank Ocean       | 34.7           |
| Story to Tell                                   | Death             | 34.4           |
| ALL I CAN TAKE                                  | Justin Bieber     | 34.2           |
| Dreams - 2004 Remaster                          | Fleetwood Mac     | 34.2           |
| The Lightning I                                 | Arcade Fire       | 34.2           |
| Sea of Love                                     | The National      | 33.4           |
| Corporal Jigsore Quandary                       | Carcass           | 33.3           |
| Old Friends                                     | Pinegrove         | 33.3           |
| Arcanum                                         | Show Me the Body  | 31.7           |
| Don't Dream It's Over                           | Crowded House     | 31.7           |
| Wait for It                                     | Leslie Odom Jr.   | 31.6           |
| Keep On Rotting in the Free World               | Carcass           | 30.6           |
| Reborn                                          | KIDS SEE GHOSTS   | 30.3           |
| Ex-Factor                                       | Ms. Lauryn Hill   | 30.2           |

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

These are tracks I tend to listen to frequently, but am often not in the mood when they come up during shuffle. You can see by the play_rate, I don't not enjoy them, but they are skipped more often than not. All of these tend to be post-2023 because Spotify relably added skipping in the middle of 2022

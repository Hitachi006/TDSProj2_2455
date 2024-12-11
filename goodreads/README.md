# Analysis Summary for goodreads.csv

The dataset conatins 10000 samples with 23 variables each

the summary is the datatypes and number of missing values is as below

| variable                  | data_type   |   missing_data |
|:--------------------------|:------------|---------------:|
| book_id                   | int64       |              0 |
| goodreads_book_id         | int64       |              0 |
| best_book_id              | int64       |              0 |
| work_id                   | int64       |              0 |
| books_count               | int64       |              0 |
| isbn                      | object      |            700 |
| isbn13                    | float64     |            585 |
| authors                   | object      |              0 |
| original_publication_year | float64     |             21 |
| original_title            | object      |            585 |
| title                     | object      |              0 |
| language_code             | object      |           1084 |
| average_rating            | float64     |              0 |
| ratings_count             | int64       |              0 |
| work_ratings_count        | int64       |              0 |
| work_text_reviews_count   | int64       |              0 |
| ratings_1                 | int64       |              0 |
| ratings_2                 | int64       |              0 |
| ratings_3                 | int64       |              0 |
| ratings_4                 | int64       |              0 |
| ratings_5                 | int64       |              0 |
| image_url                 | object      |              0 |
| small_image_url           | object      |              0 |

The variables with the highest correlation are: ratings_count and work_ratings_count, with a correlation of 1.0


# PaySim Data

Source link: [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1/data)

Structure: Created 'paysim' table with 6,362,620 rows and 11 columns

List of Columns: ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig', 'nameDest', 'oldbalanceDest', 'newbalanceDest', 'isFraud', 'isFlaggedFraud']

> [!NOTE]
>
> I've appended a datetime column for easier graphing based on the constant of Jan 1, 2025 with 1 hour steps as indicated in the dataset description.
>
> I've also appended a surrogate key which is a hash defined as follows:
> `hash( datetime || Type || nameOrig || nameDest || amount ) as tx_sk`
>
> This makes it possible to identify every row uniquely.

Head:

``` bash
step      type    amount     nameOrig  oldbalanceOrg  ...  newbalanceDest isFraud  isFlaggedFraud            datetime                 tx_sk
0     1   PAYMENT   9839.64  C1231006815      170136.00  ...            0.00       0               0 2025-01-01 01:00:00  13900611866310383366
1     1   PAYMENT   1864.28  C1666544295       21249.00  ...            0.00       0               0 2025-01-01 01:00:00   7443289086782978124
2     1  TRANSFER    181.00  C1305486145         181.00  ...            0.00       1               0 2025-01-01 01:00:00  12483813255227637210
3     1  CASH_OUT    181.00   C840083671         181.00  ...            0.00       1               0 2025-01-01 01:00:00     25989359987325576
4     1   PAYMENT  11668.14  C2048537720       41554.00  ...            0.00       0               0 2025-01-01 01:00:00   1950123046391734180
5     1   PAYMENT   7817.71    C90045638       53860.00  ...            0.00       0               0 2025-01-01 01:00:00   7809180732797165896
6     1   PAYMENT   7107.77   C154988899      183195.00  ...            0.00       0               0 2025-01-01 01:00:00  10722390766392154727
7     1   PAYMENT   7861.64  C1912850431      176087.23  ...            0.00       0               0 2025-01-01 01:00:00   2428246401720795062
8     1   PAYMENT   4024.36  C1265012928        2671.00  ...            0.00       0               0 2025-01-01 01:00:00   5602291911493582130
9     1     DEBIT   5337.77   C712410124       41720.00  ...        40348.79       0               0 2025-01-01 01:00:00  18296590939200122479
```

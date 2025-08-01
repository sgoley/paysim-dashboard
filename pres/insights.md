---
marp: true
---

# Analysis & Dashboard of PaySim Financial Transaction Data

## Scott Goley

-------

## Goals

* A write-up of your methodology

* Key insights or trends from the data

-------

## Topics to cover

* Explain what steps you took to validate and cleanse the data.
* What did you do to explore trends or patterns in the data?
* How did you decide which insights to highlight from the data?
* What additional information or context might have been useful in forming your conclusions?

-------

## Project Materials

* [Github Repo](https://github.com/sgoley/paysim-dashboard) 
* [Streamlit Cloud Dashboard](https://sg-paysim-dashboard.streamlit.app)

-------

## Validation & Cleansing

* I made a transaction surrogate key to handle for duplication
  * `hash( datetime || Type || nameOrig || nameDest || amount )`
* I confirmed that dataset does not contain obvious duplicates
* I confirmed the time range of dataset (approximately covering a 31 day period truncated to hours)
* I made an adjustment from `step` to a datetime data type for easier graphing

-------

## Explore

* The dataset contains approximately 6.36M total transactions
* It contains about 6.35M sending accounts and 2.72M receiving accounts
* 8.21K were flagged via the `isFraud` boolean variable
* With $12B in flagged transactions, this appoximates to 1% of the total 1.14T in transaction notional.

-------

![bg 85%](Dashboard.png)

-------

## Explore - Dashboard

* The dashboard itself features most of these metrics as a headline for frequent viewing
* The primary featured chart is targeted to viewing proportion of fraudulent transactions over time vs non fraud.

-------

![bg 85%](Latest%20100.png)

-------

## Explore - Latest 100

* The table version of the dataset could easily be configured to filter by some of the following as alternatives:
  1. Latest 100
  2. Latest 100 isFraud
  3. Tx Notional Value
* Or many other important attributes

-------

![bg 85%](Profiling.png)

-------

## Explore - Profiling

* For profiling the fraudulent transactions:
  1. All occur as part of the `CASH_OUT` or `TRANSFER` tx types.
  2. Of the `CASH_OUT` transactions, they tend to feature a significantly higher median and higher average notional value than non-fraudulent transactions.

-------

![bg 85%](Hour%20of%20Day.png)

-------

## Explore - Hours

* An additional feature of flagged transactions are:
  1. A significant proportion occur at a low point in transaction volume.
     1. Due to my datetime adjustment, this appears to be between the 3am - 7am hours of the day but requires further context to confirm.
  2. This is true of both `CASH_OUT` and `TRANSFER` types of flagged transactions.

-------

![bg 85%](Network%20Graph.png)

-------

## Explore - Graph

* Finally - I produced a graph exploration view so that single actors which were either the sender or receiver of a flagged `isFraud` can be deeply inspected in the context of their other transactions & counterparties.

-------

![bg 85%](Balances.png)

-------

## Explore - Balance

* This perspective shows that transaction pairs exist of identical amounts and that the original balance columns can likely not be trusted.
* If we assume that fraudulent transaction in the same exact amount are linked, the movement becomes obvious:
    1. Initiate a `TRANSFER` to an account of bad actor control
    2. Initiate a `CASH_OUT` transaction for the full quantity captured.

-------

## Additional Context
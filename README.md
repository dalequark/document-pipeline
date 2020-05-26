# Document Parsing Pipeline

This repo provides code for building a document processing pipeline on GCP. It works like this:

1. Upload a document as text, as a pdf, or as an image to the cloud (in this case, a Google Cloud Storage bucket).
2. The document gets tagged by type (i.e. "invoice," "article," etc) and then put into a new folder/storage bucket based on that type.
3. Each document type is processed differently. A file that's moved to the "article" bucket gets tagged (i.e. Sports, Politics, Technology). A file that's moved the "invoices" folder gets analyze for prices, phone numbers, and other entities.
4. Extracted data then gets put into a bigquery table.

## Step 0: Enable APIs

For this project, you'll need to enable these GCP services:
- AutoML Natural Language
- Natural Language API
- Vision API
- Places API

![document pipeline architecture](https://github.com/dalequark/document-pipeline/blob/master/document_pipeline.png)

## Step 1: Create Storage Buckets

First, you'll want to create a couple of [Storage Buckets](https://cloud.google.com/storage/docs/creating-buckets).

Create one folder, something like `gs://input-documents`, where you'll initially upload your unsorted documemts.

Next, create folders for each of the file types you want to move documents to. In this project, I have code to analyze invoices and articles, so I created three buckets:

- `gs://articles`
- `gs://invoices`
- `gs://unsorted-docs`

## Step 2: Create an AutoML Document Classification Model

Next, you'll want to build a model that sorts documents by type, labeling them as invoices, invoices, articles, emails, and so on. To do this, I used the [RVL-CDIP dataset](https://www.cs.cmu.edu/~aharley/rvl-cdip/):

![rvl-cdip-1](https://www.cs.cmu.edu/~aharley/rvl-cdip/images/sample1.png)
![rvl-cdip-2](https://www.cs.cmu.edu/~aharley/rvl-cdip/images/sample2.png)

    A. W. Harley, A. Ufkes, K. G. Derpanis, "Evaluation of Deep Convolutional Nets for Document Image Classification and Retrieval," in ICDAR, 2015

This huge dataset contains 400,000 grayscale document images in 16 classes.

I also added some scanned invoice data from the [Scanned invoices OCR and Information Extraction Dataset](https://rrc.cvc.uab.es/?ch=13).

Because this dataset combined was so huge and hard to work with, I just used a sample of documents with this breakdown of document type:

|label          | count |
|---------------|-------| 
|advertisement  | 902   |
|budget         | 900   |
|email          | 900   |
|form           | 900   |
|handwritten    | 900   |
|invoice        | 900   |
|letter         | 900   |
|news           | 188   |
|invoice        | 626   |

I've hosted all this data at `https://console.cloud.google.com/storage/browser/doc-classification-training-data` (or `gs://doc-classification-training-data`). The training files, as `pdfs` and `txt` data, are in the `processed_files` folder. You'll need to copy those files to your own GCP project in order to train your own model. You'll also see a file `automl_input.csv` in the bucket. This is the `csv` file you'll use to import data into AutoML Natural Language.

AutoML Natural Language is a tool that builds custom deep learning models from user-provided training data. It works with text and pdf files. This is what I used to build my document type classifier. [The docs](https://cloud.google.com/natural-language/automl/docs/beginners-guide) will show you how to train your own document classification model. When you're done training your model, Google Cloud will host the model for you. 

To use your AutoML model in your app, you'll need to find your model name:

`projects/YOUR LONG NUMBER/locations/us-central1/models/YOUR LONG MODEL ID NUMBER`

We'll use this id in the next step.

## Step 3: Set up Cloud Functions

This document pipeline is designed so that when you upload files to an input bucket (i.e. `gs://input-documents`), they're sorted by type by the AutoML model we built in Step 2.

After you've created this storage bucket and trained your AutoML model, you'll need to create a new [cloud function](https://cloud.google.com/functions/docs/quickstart-python) that runs every time a new file is uploaded to `gs://input-documents`.

Create a new cloud function with the code in `sort_documents.py`. For this to work, you'll need to set several environmental variables in the Cloud Functions console, like `INVOICES_BUCKET`, `UNSORTED_BUCKET`, and `ARTICLES_BUCKET`. These should be the names of the corresponding buckets you created, without the preceding `gs:` (i.e. `gs://reciepts` -> `invoices`). You'll also need to set the environmental variable `SORT_MODEL_NAME` to the model name we found in the last step (that entire long path that ends in model id number).

Once you've set up this function, documents uploaded to `gs://input_documents` (or whatever you've called your input document folder) will be classified and moved into the invoices, articles, or unsorted buckets respectively.

There are two more cloud functions defined in this repository:

- analyze_invoice.py
- tag_article.py

You'll want to create two new cloud functions that connects these scripts to your invoices and article buckets.

But first, you'll need to create a bigquery table to store the data extracted from those functions

## Step 4: Create BigQuery Tables

[Create two BigQuery tables](https://cloud.google.com/bigquery/docs/tables). One, which you can call something like, "article_tags", will store the tags extracted by your `tag_article` cloud functions. It's schema should be:

| column name | type |
|-------------|------|
| filename    |string|
| tag         |string|

Create a second table called something like `invoice_data` with the schema:

| column name | type |
|-------------|------|
| filename    |string|
| address     |string|
|phone_nunmber|string|
|name         |string|
|total        |float |
|date_str     |string|

For each of these tables, note the Table ID, which should be of the form:

`your-project-name.your-dataset-name.your-table-name`

## Step 5: Create Remaining Cloud Functions

Now that you've created those BigQuery tables, you can deploy the cloud functions:

- tag_article.py
- analyze_invoice.py

As you deploy, you'll need to set the environmental variables `ARTICLE_TAGS_TABLE` and `invoiceS_TABLE` respectively to their BigQuery table IDs. For the `analyze_receiept` cloud function, you'll also need to [create an API key](https://cloud.google.com/docs/authentication/api-keys and set the environmental varialbe `GOOGLE_API_KEY` to that key (this script uses the Google Places API to find information about businesses from their phone numbers).

[This documentation](https://cloud.google.com/functions/docs/quickstart-python) shows you how to create a Python cloud function on Google Cloud. 

## Step 6: Analyze

Voila! You're done. Upload a file to your `gs://input-documents` and watch as its sorted and analyzed.

**This is not an officially supported Google product**

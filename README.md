# Neurobagel subcommunities

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/neurobagel/communities/update_term_vocab_files.yaml?style=flat-square&label=Community%20standardized%20term%20vocabularies&link=https%3A%2F%2Fgithub.com%2Fneurobagel%2Fcommunities%2Fblob%2Fmain%2F.github%2Fworkflows%2Fupdate_term_vocab_files.yaml)](https://github.com/neurobagel/communities/blob/main/.github/workflows/update_term_vocab_files.yaml)

Scripts and configuration files that allow Neurobagel subcommunities to define custom standardized vocabularies used among their studies or sites and make them available for use within the Neurobagel tool ecosystem.

## Creating a new subcommunity vocabulary of assessments (WIP)
<!-- TODO: Once finalized, add instructions for creating a file with vocab namespace metadata. -->

Neurobagel expects each subcommunity-curated vocabulary to be maintained in a single Google Sheets table.

1. Use this [template Google Sheet](https://docs.google.com/spreadsheets/d/1O02EnpRCNMALeGpyVzDw6bSuDlJuvTPMNvqILDKk1xM/edit?usp=sharing) for creating a Neurobagel subcommunity vocabulary table.
Make a copy of the template (**File** > **Make a copy**) and give it a descriptive name, e.g., "\<SUBCOMMUNITY NAME\> Assessment Vocabulary".

2. Open the **Share** settings and set the access permissions for your Google Sheet to **Anyone with the link**.

3. Populate the sheet with information about your subcommunity's assessment terms. 
Guidelines for each column can be found in the spreadsheet comments or in the [section below](#about-the-subcommunity-vocabulary-table).

4. Once the terms have been finalized by your subcommunity, share the ID of your Google Sheet with the Neurobagel team. 
You can find it in the spreadsheet's URL, after the `/d/` part.
e.g., `1aBcD2EfGh1234567890` is the spreadsheet ID for https://docs.google.com/spreadsheets/d/1aBcD2EfGh1234567890/edit#gid=0.

### About the subcommunity vocabulary table

Each row in the table describes a unique assessment used by studies or sites in your subcommunity. 

An example vocabulary table with two assessments:

ID | Name | Abbreviation | Description
---- | ---- | ---- | ----
trm_001 | Beck's Depression Inventory | BDI | 21-item self-report questionnaire for depressive symptoms
trm_002 | Hamilton Rating Scale for Depression | HRDS | Clinician-administered scale for depressive symptom severity
... | ... | ... | ...

>[!IMPORTANT]
>Your spreadsheet must include at least the columns `ID`, `Name`, `Abbreviation`, and `Description`, but you may add more columns as needed to track additional information.

We recommend filling out all four columns whenever possible for optimal clarity and documentation.

#### Information for each assessment term (row):  

- **ID** (required): A unique identifier for the assessment term. 
    This functions as a stable tag for the assessment, allowing it to be consistently referenced even if its name or other details are updated. 
    We recommend using the format `trm_` followed by a numeric ID.
- **Name** (required): The full name of the assessment.
- **Abbreviation** (optional): The short abbreviation or acronym for the assessment, if one is used.
- **Description** (optional): A brief description of the assessment.

>[!WARNING]
>Once an ID is assigned to an assessment, do not modify it (unless you need to remove that term from your vocabulary entirely). 
>Changing an ID can create duplicates or conflicts with existing data dictionaries, potentially causing them to stop working correctly.

# Neurobagel communities

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/neurobagel/communities/update_term_vocab_files.yaml?style=flat-square&label=Community%20standardized%20term%20vocabularies&link=https%3A%2F%2Fgithub.com%2Fneurobagel%2Fcommunities%2Fblob%2Fmain%2F.github%2Fworkflows%2Fupdate_term_vocab_files.yaml)](https://github.com/neurobagel/communities/blob/main/.github/workflows/update_term_vocab_files.yaml)

Scripts and configuration files that allow Neurobagel communities to define custom standardized vocabularies used among their studies or sites and make them available for use within the Neurobagel tool ecosystem.

>[!NOTE]
>Imaging modality terms are handled separately from community configs: 
>The `imaging_modalities.json` file is used by all communities, 
>and so we store it only in the Neurobagel community configuration.
>Do not copy this file into a community as it will be ignored.

## Creating a new community vocabulary of assessments (WIP)
<!-- TODO: Once finalized, add instructions for creating a file with vocab namespace metadata. -->

Neurobagel expects each community-curated vocabulary to be maintained in a single Google Sheets table.

1. Use this [template Google Sheet](https://docs.google.com/spreadsheets/d/1O02EnpRCNMALeGpyVzDw6bSuDlJuvTPMNvqILDKk1xM/edit?usp=sharing) for creating a Neurobagel community vocabulary curation table.
Make a copy of the template (**File** > **Make a copy**) and give it a descriptive name, e.g., "\<community NAME\> Assessment Vocabulary".

2. Open the **Share** settings and set the access permissions for your Google Sheet to **Anyone with the link can view**.
    We strongly recommend restricting editor permissions by explicitly adding email addresses of community members.

3. Populate the sheet with information about your community's assessment terms. 
Guidelines for each column can be found in the spreadsheet comments or in the [vocabulary curation table reference](#community-vocabulary-curation-table-reference) below.

4. Once the terms have been finalized by your community, share the ID of your Google Sheet with the Neurobagel team. 
You can find it in the spreadsheet's URL, after the `/d/` part.
e.g., `1aBcD2EfGh1234567890` is the spreadsheet ID for https://docs.google.com/spreadsheets/d/1aBcD2EfGh1234567890/edit#gid=0.

### Example community vocabulary curation table

id | name | abbreviation | description
---- | ---- | ---- | ----
trm_001 | Beck's Depression Inventory | BDI | 21-item self-report questionnaire for depressive symptoms
trm_002 | Hamilton Rating Scale for Depression | HRDS | Clinician-administered scale for depressive symptom severity
... | ... | ... | ...

For more information on each column, see the [vocabulary curation table reference](#community-vocabulary-table-reference).

## Community vocabulary curation table reference

Each row in the table describes a unique assessment used by studies or sites in your community.

Columns supported by Neurobagel are listed below. Required/optional refers to a whether a value must be provided for each row. Column names are **case-insensitive**.

- **`id`** (required)
    - A unique identifier for the assessment term, containing only alphanumeric characters (A–Z, a–z, 0–9), underscores (_), and hyphens (-).
    This acts as a stable tag for the assessment that is used internally by Neurobagel, allowing the concept to be referenced consistently even if its name or other details are updated. 
    - We recommend using an abstract identifier (e.g., `trm_` followed by a numeric ID) rather than the term name or abbreviation, to ensure identifier uniqueness within your vocabulary.
- **`name`** (required)
    - The full name of the assessment, as it should appear to users in the annotation tool.
- **`abbreviation`** (optional)
    - The short abbreviation or acronym for the assessment, if one is used.
    If provided, the abbreviation will be included in the user-facing label in the annotation tool 
    and allow the assessment to be found by abbreviation.
- **`description`** (optional)
    - A brief description of the assessment.
- **`invalid_reason`** (optional): 
    - Reason or community-defined code indicating why a term must be excluded (e.g., `duplicate`, `deprecated`).
    Any row with a non-empty value in this column will be automatically excluded from the final vocabulary.

>[!WARNING]
> Once your community vocabulary has been integrated into Neurobagel, do not modify IDs of existing assessment terms. 
> Changing a term's ID can create duplicates or conflicts with existing data dictionaries, potentially causing them to stop working correctly.
> To deprecate a term, use the `invalid_reason` column instead.

>[!IMPORTANT]
>Your spreadsheet must include at least the columns `id`, `name`, `abbreviation`, and `description`. 
We recommend filling out all four of these columns whenever possible for optimal clarity and documentation.

You may also add more columns to your curation table beyond those listed above for community-specific use.  
Additional columns will be safely ignored by Neurobagel.

## Questions?

Open an [issue](https://github.com/neurobagel/communities/issues/new) or reach out to us on [Discord](https://discord.gg/HWMHYu44RM)!

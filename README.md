# dataquest-refseq
data analysis on protein data source that will be integrate into Biothings API

# Pre-cleaned data file overview
The data is stored in tabular format with headers, so we can directly load data with `\t` delimiter

```
https://ftp.ncbi.nlm.nih.gov/pub/CCDS/
├── current_mouse/
│   ├── CCDS.current.txt
│   └── CCDS_attributes.current.txt
└── current_human/
    ├── CCDS.current.txt
    └── CCDS_attributes.current.txt
```

# Expected data schema

## Interested data attributes
`gene_id`: the gene ID

`ccds_id`: the ccds ID

`match_type`: Comparison with reference annotation sources (RefSeq vs. Ensembl)
- In total there is 2 types: `Identical`, `Partial`

`ccds_status`: the status of ccds. 

- In total there is 8 status: `Candidate`, `Public`, `Reviewed, update pending`, `Reviewed, withdrawal pending`, `Under review, update`, `Under review, withdrawal`, `Withdrawn`, `Withdrawn, inconsistent annotation`

`attribute`: the side notes for ccds
- only 9 types
- example: CDS uses downstream AUG
- example: Inferred exon combination
- example: Nonsense-mediated decay (NMD) candidate
...


## Mapping Example
```
{
  "_id": "21957",
  "ccds_ids": [
    {
      "ccds_id": "ccds12345.1",
      "status": "public",
      "match_type": "identical",
      "attribute": "nonsense-mediated decay (nmd) candidate"
    },
    {
      "ccds_id": "ccds67890.2",
      "status": ["reviewed", "update pending"],
      "match_type": "partial",
      "attribute": "inferred exon combination"
    }
  ]
}
```











<!-- 


# Data Source Introduction
The data source is from [RefSeq](https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/mRNA_Prot/). They come in forms of human
"human.{number}.protein.gpff.gz". There are in total 199,055 records of protein sequences acorss 16 gpff files. 

Problem: **Each record contains numerous fields, particularly within the nested FEATURES section. Need to identify and confirm the essential fields required for data integration.**

# Data Set Description
Each protein record follows the standard GenPept format with three main sections.

**Header information**: this section contains the top-level attributes like protein ID, definition, organism details, etc.

**FEATURES INFORMATION**: this section contains the detailed annotations mapped to specific regions on a specific amino acid sequence.
- each feature must has a Type (ex. Region, CDS)
- each feature must has a Location (amino acid sequence)
- each feature may have a Qualifier (ex. /gene=..., /locus_tag=...)

**ORIGIN**: the full amino acid sequence of the protein.

here is an example:
```
LOCUS       NP_001355183              382 aa            linear   PRI 26-JUN-2020
DEFINITION  killer cell immunoglobulin-like receptor 3DS1-like precursor [Homo
            sapiens].
ACCESSION   NP_001355183 XP_024308382
VERSION     NP_001355183.1
DBSOURCE    REFSEQ: accession NM_001368254.1
KEYWORDS    RefSeq; RefSeq Select.
SOURCE      Homo sapiens (human)
  ORGANISM  Homo sapiens
            Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;
            Mammalia; Eutheria; Euarchontoglires; Primates; Haplorrhini;
            Catarrhini; Hominidae; Homo.
COMMENT     VALIDATED REFSEQ: This record has undergone validation or
            preliminary review. The reference sequence was derived from
            KU645196.1.

            On Jan 30, 2019 this sequence version replaced XP_024308382.1.

            ##RefSeq-Attributes-START##
            RefSeq Select criteria :: based on single protein-coding transcript
            ##RefSeq-Attributes-END##
FEATURES             Location/Qualifiers
      source          1..382
                      /organism="Homo sapiens"
                      /db_xref="taxon:9606"
                      /chromosome="19"
                      /map="19"
      Protein         1..382
                      /product="killer cell immunoglobulin-like receptor
                      3DS1-like precursor"
                      /calculated_mol_wt=40454
      sig_peptide     1..18
                      /inference="COORDINATES: ab initio prediction:SignalP:4.0"
                      /calculated_mol_wt=2011
      Region          28..117
                      /region_name="IgC2_D2_LILR_KIR_like"
                      /note="Second immunoglobulin (Ig)-like domain found in
                      Leukocyte Ig-like receptors, Natural killer inhibitory
                      receptors (KIRs) and similar domains; member of
                      Immunoglobulin Constant-2 set of IgSF domains; cd05711"
                      /db_xref="CDD:409376"
      CDS             1..382
                      /gene="LOC112268355"
                      /coded_by="NM_001368254.1:47..1195"
                      /db_xref="GeneID:112268355"
ORIGIN      
        1 mllmvvsmac vglflvqrag phmggqdkpf lsawpsavvp rgghvtlrch yrhrfnnfml
       61 ykedrihvpi fhgrifqegf nmspvttaha gnytcrgshp hsptgwsaps npmvimvtgn
      121 hrkpsllahp gplvksgerv ilqcwsdimf ehfflhkewi skdpsrlvgq ihdgvskanf
      181 sigsmmrala gtyrcygsvt htpyqlsaps dpldivvtgl yekpslsaqp gpkvqagesv
      241 tlscssrssy dmyhlsregg aherrlpavr kvnrtfqadf plgpathggt yrcfgsfrhs
      301 pyewsdpsdp llvsvtgnps sswpspteps sksgnlrhlh iligtsvvki pftillffll
      361 hrwcsnkkkc ccngpracre qk
//
```

## Avaliable Data Fields

--- Unique Keys found from the Header Section ---

`id`: (String) The primary identifier used in the LOCUS line (often the accession without the version).

`date`: (String) Date of the last modification of the record (from LOCUS).

`description`: (String) The descriptive title of the protein record (from DEFINITION).

`comment`: (String) Free-text comments about the record.

`data_file_division`: (String) NCBI's category code (e.g., PRI=Primate, HUM=Human) from the LOCUS line.

`organism`: (String) Scientific name of the source organism.

`references`: (List) Publication details (authors, title, journal, PubMed ID) associated with the sequence.

`source`: The source of the sequence (ex. Homo sapiens (human)).

`topology`: The topology of the sequence (ex. linear).

`ACCESSION`: Not sure (ex. NP_001355183 XP_024308382).

`keywords`: Not sure (ex. RefSeq; RefSeq Select.).

--- Unique Feature Keys Found Across all ---

`['Bond', 'CDS', 'Protein', 'Region', 'Site', 'mat_peptide', 'misc_feature', 'proprotein', 'sig_peptide', 'source', 'transit_peptide']`

--- Unique Feature Qualifier Keys Found Across All Files ---

`['EC_number', 'GO_component', 'GO_function', 'GO_process', 'bio_material', 'bond_type', 'calculated_mol_wt', 'cell_line', 'chromosome', 'coded_by', 'db_xref', 'exception', 'experiment', 'gene', 'gene_synonym', 'geo_loc_name', 'inference', 'isolate', 'isolation_source', 'map', 'name', 'note', 'organelle', 'organism', 'product', 'region_name', 'ribosomal_slippage', 'sex', 'site_type', 'tissue_type', 'transl_table']` -->